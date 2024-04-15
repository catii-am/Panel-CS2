import subprocess
import win32gui
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
import time
import hmac
import struct
import base64
import requests
from hashlib import sha1

import sys
import os

if hasattr(sys, '_MEIPASS'):
    temp_dir = sys._MEIPASS
else:
    temp_dir = os.path.abspath(".")

def make_list_from_file(file):
    with open(file, 'r') as f:
        return [x for x in f.read().split("\n") if x]


symbols = '23456789BCDFGHJKMNPQRTVWXY'
server_time = 0


def getQueryTime():
    try:
        timeout = 0
        if timeout <= time.time() - 1:
            request = requests.post('https://api.steampowered.com/ITwoFactorService/QueryTime/v0001', timeout=30)
            json = request.json()
            server_time = int(json['response']['server_time']) - time.time()
            return server_time
    except:
        return 0


def getGuardCode(shared_secret):
    code = ''
    timestamp = time.time() + getQueryTime()
    _hmac = hmac.new(base64.b64decode(shared_secret), struct.pack('>Q', int(timestamp / 30)), sha1).digest()
    _ord = ord(_hmac[19:20]) & 0xF
    value = struct.unpack('>I', _hmac[_ord:_ord + 4])[0] & 0x7fffffff
    for i in range(5):
        code += symbols[value % len(symbols)]
        value = int(value / len(symbols))
    return code


def extract_values_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        shared_secret_start = content.find('"shared_secret"') + len('"shared_secret":"')
        shared_secret_end = content.find('"', shared_secret_start + 1)
        shared_secret = content[shared_secret_start:shared_secret_end]

        uri_start = content.rfind('"account_name":"') + len('"account_name":"')
        uri_end = content.find('"', uri_start + 1)
        uri = content[uri_start:uri_end]

    return shared_secret, uri


# Функция для проверки наличия uri в файле accounts.txt
def uri_exists_in_accounts(uri, accounts_data):
    for line in accounts_data:
        if uri in line:
            return True
    return False


# Функция для добавления uri в файл accounts.txt
def add_uri_to_accounts(uri, password, shared_secret, accounts_file):
    with open(accounts_file, 'a') as file:
        file.write(f"{uri}:{password}:{shared_secret}\n")


# Основная функция для обработки файлов в директории
def process_files_in_directory(directory):
    accounts_file = 'accounts.txt'

    # Считываем содержимое accounts.txt
    with open(accounts_file, 'r') as file:
        accounts_data = file.readlines()
    new_accounts = 0
    old_accounts = 0
    for filename in os.listdir(directory):
        if filename.endswith(''):
            file_path = os.path.join(directory, filename)
            shared_secret, uri = extract_values_from_file(file_path)
            if uri:
                if not uri_exists_in_accounts(uri, accounts_data):
                    password = input(f"Введите пароль для нового аккаунта ({uri}): ")
                    add_uri_to_accounts(uri, password, shared_secret, accounts_file)
                    new_accounts = new_accounts + 1
                else:
                    old_accounts = old_accounts + 1
    all_accounts = old_accounts + new_accounts
    return all_accounts, new_accounts


class Steam:
    def __int__(self) -> None:
        pass

    def start_steam(self, steam_path, arguments):
        program_path = rf'{steam_path}'
        arguments = ['-vgui', '-applaunch', '730', '-novid', '-nosound', '-console', '-nojoy', '+exec autoexec.cfg']

        subprocess.Popen([program_path] + arguments)

    def wait_for_window(self, title, timeout=10):
        end_time = time.time() + timeout
        while True:
            hwnd = win32gui.FindWindow(None, title)
            if hwnd != 0:
                return hwnd
            if time.time() > end_time:
                raise TimeoutError(f"Window with title '{title}' not found within {timeout} seconds.")
            time.sleep(0.5)

    def bring_window_to_front(self, hwnd):
        app = Application().connect(handle=hwnd)
        app.window(handle=hwnd).set_focus()
        return app

    def send_username(self, username):
        send_keys(username)
        send_keys('{TAB}')

    def send_password(self, password):
        clean_pass = ''
        for c in password:
            if c in ['(', ')', '{', '}', '%']:
                clean_pass += ('{' + c + '}')
            else:
                clean_pass += c
        send_keys(clean_pass)
        send_keys('{ENTER}')

    def send_SGC(self, SGC):
        send_keys(SGC)


def steam_login(acc_quest):
    config_file = "sys/config.cfg"
    steam_path = None
    arguments = []

    # Чтение файла конфигурации
    with open(config_file, "r") as f:
        for line in f:
            # Разделение строки по первому символу ":"
            key_value = line.strip().split(":", 1)
            if len(key_value) == 2:
                key, value = key_value
                if key.strip() == "SteamPath":
                    steam_path = value.strip()
                elif key.strip() == "Arguments":
                    arguments = value.strip().split()

    steam = Steam()

    acc_list = make_list_from_file("sys/accounts.txt")
    first_number = 1
    second_number = 11

    if acc_quest > 1:
        acc_quest = acc_quest - 1
        for i in range(acc_quest):
            first_number = first_number + 10
            second_number = second_number + 10

    if acc_quest >= 1:
        last_hwnd = None
        for i in range(first_number, second_number):
            account = acc_list[i - 1]
            username = account.split(":")[0]
            password = account.split(":")[1]
            SGAKey = account.split(":")[2]
            print(f'Вход в аккаунт {username}')
            steam.start_steam(steam_path, arguments)

            while True:
                hwnd = steam.wait_for_window("Войти в Steam", timeout=120)
                if last_hwnd != hwnd:
                    time.sleep(2)
                    steam.bring_window_to_front(hwnd)
                    steam.send_username(username)
                    steam.bring_window_to_front(hwnd)
                    steam.send_password(password)
                    time.sleep(5)
                    steam.bring_window_to_front(hwnd)
                    SGC = getGuardCode(SGAKey)
                    steam.send_SGC(SGC)
                    last_hwnd = hwnd
                    time.sleep(10)
                    break
                else:
                    time.sleep(1)