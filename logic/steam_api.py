import base64
import time

import requests
from steampy import guard
import rsa
import json
from bs4 import BeautifulSoup


class LoginExecutor:
    def __init__(self, username: str, password: str, shared_secret: str, session: requests.Session = requests.Session()) -> None:
        self.username = username
        self.password = password
        self.shared_secret = shared_secret
        self.session = session
        self.client_id = ''
        self.steamid = ''
        self.request_id = ''
        self.refresh_token = ''

    def login(self) -> requests.Session:
        login_response = self._send_login_request()  # 创建登录会话
        self._update_stem_guard(login_response)
        self._pool_sessions_steam()
        finallized_response = self._finallez_login()
        self._set_tokens(finallized_response)
        self.set_sessionid_cookies()

        return self.session

    def _send_login_request(self) -> requests.Response:
        rsa_params = self._fetch_rsa_params()
        data = {
            'persistence': "1",
            'encrypted_password': rsa_params['encrypted_password'],
            'account_name': self.username,
            'encryption_timestamp': rsa_params['rsa_timestamp'],
        }
        response = self.session.post("https://api.steampowered.com/IAuthenticationService/BeginAuthSessionViaCredentials/v1", data=data)
        return response

    def set_sessionid_cookies(self):
        sessionid = self.session.cookies.get_dict().get('sessionid')

        community_cookie = {"name": "sessionid",
                            "value": sessionid,
                            "domain": 'steamcommunity.com'}
        self.session.cookies.set(**community_cookie)

        store_cookie = {"name": "sessionid",
                        "value": sessionid,
                        "domain": 'store.steampowered.com'}
        self.session.cookies.set(**store_cookie)

    def _fetch_rsa_params(self, retry: int = 3) -> dict:
        self.session.post("https://steamcommunity.com")  # 获得第一个Cookies
        response = self.session.get("https://api.steampowered.com/IAuthenticationService/GetPasswordRSAPublicKey/v1/?account_name=" + self.username)
        key_response = json.loads(response.text)
        for i in range(retry):
            try:
                rsa_mod = int(key_response["response"]['publickey_mod'], 16)
                rsa_exp = int(key_response["response"]['publickey_exp'], 16)
                rsa_timestamp = key_response["response"]['timestamp']
                rsa_key = rsa.PublicKey(rsa_mod, rsa_exp)
                encrypted_password = base64.b64encode(rsa.encrypt(self.password.encode('utf-8'), rsa_key))
                return {'encrypted_password': encrypted_password,
                        'rsa_timestamp': rsa_timestamp}
            except KeyError:
                if retry >= 2:
                    raise ValueError('Could not obtain rsa-key')

    def _update_stem_guard(self, login_response):
        response_json = json.loads(login_response.text).get('response')
        self.client_id = response_json.get('client_id')
        self.steamid = response_json.get('steamid')
        self.request_id = response_json.get('request_id')
        code = guard.generate_one_time_code(self.shared_secret)

        update_data = {
            'client_id': self.client_id,
            'steamid': self.steamid,
            'code_type': 3,
            'code': code
        }

        response = self.session.post("https://api.steampowered.com/IAuthenticationService/UpdateAuthSessionWithSteamGuardCode/v1/", data=update_data)

    def _pool_sessions_steam(self):
        pool_data = {
            'client_id': self.client_id,
            'request_id': self.request_id
        }
        response = self.session.post("https://api.steampowered.com//IAuthenticationService/PollAuthSessionStatus/v1/", data=pool_data)
        response_json = json.loads(response.text)
        self.refresh_token = response_json.get("response").get("refresh_token")

    def _finallez_login(self) -> requests.Response:
        try:
            sessionid = self.session.cookies.get_dict().get('sessionid')
        except Exception:
            print("获取sessionid失败", self.session.cookies.get_dict())
            raise Exception("Steam_login.py , 获取sessionid失败")
        else:
            redir = "https://steamcommunity.com/login/home/?goto="

            finallez_data = {
                'nonce': self.refresh_token,
                'sessionid': sessionid,
                'redir': redir
            }

            response = self.session.post("https://login.steampowered.com/jwt/finalizelogin", data=finallez_data)
            return response

    def _set_tokens(self, fin_resp: requests.Response):
        response_json = json.loads(fin_resp.text)
        transfer_info = response_json.get("transfer_info")
        for item in transfer_info[:2]:
            params = item.get('params')
            data = {
                'nonce': params.get("nonce"),
                'auth': params.get("auth"),
                'steamID': self.steamid
            }
            response = self.session.post(item.get('url'), data=data)

    def test_is_logined(self):
        resp = self.session.get(f"https://steamcommunity.com/profiles/{self.steamid}/home")
        print(resp.text)

    def return_steamID(self):
        return str(self.steamid)


def update_data(username, password, shared_secret):
        login = LoginExecutor(username=username, password=password, shared_secret=shared_secret)
        session = login.login()

        steamID = login.return_steamID()
        print(steamID)

        response = session.get(f'https://steamcommunity.com/profiles/{steamID}/gcpd/730')

        # Проверяем успешность запроса
        if response.status_code == 200:
            # Создаем объект BeautifulSoup для парсинга HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Находим строки с нужными данными, используя метод find_all
            rank_line = soup.find('div', string=lambda text: text and "CS:GO Profile Rank:" in text)
            xp_line = soup.find('div', string=lambda text: text and "Experience points earned towards next rank:" in text)

            # Печатаем результаты
            if rank_line and xp_line:
                rank = rank_line.get_text(strip=True).split(": ")[-1]
                exp = xp_line.get_text(strip=True).split(": ")[-1]
                return rank, exp, steamID
            else:
                print("Данные не найдены.")
        else:
            print("Ошибка при получении данных:", response.status_code)

if __name__ == '__main__':
    update_data()
