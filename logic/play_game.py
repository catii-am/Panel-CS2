import random
import time
from pywinauto.application import Application
import win32api
import win32con
import win32gui

import sys
import os


if hasattr(sys, '_MEIPASS'):
    temp_dir = sys._MEIPASS
else:
    temp_dir = os.path.abspath(".")

class WindowCoordinates:
    def __init__(self):
        self.coordinates = {}

    def add_window(self, window_name, x, y, status=False):
        """
        Метод для добавления нового окна с заданными координатами и статусом.
        """
        self.coordinates[window_name] = {'x': x, 'y': y, 'status': status}

    def update_status(self, window_name, new_status):
        """
        Метод для обновления статуса заданного окна.
        """
        if window_name in self.coordinates:
            self.coordinates[window_name]['status'] = new_status
        else:
            print(f"Ошибка: Окно с именем '{window_name}' не найдено.")

    def get_coordinates(self, window_name):
        """
        Метод для получения координат и статуса заданного окна.
        """
        if window_name in self.coordinates:
            return self.coordinates[window_name]["x"], self.coordinates[window_name]["y"], \
            self.coordinates[window_name]["status"],
        else:
            print(f"Ошибка: Окно с именем '{window_name}' не найдено.")
            return None

    def get_all_windows(self):
        """
        Метод для получения всех окон в виде словаря.
        """
        return self.coordinates

    def get_window_rect(self, hwnd):
        rect = win32gui.GetWindowRect(hwnd)
        x, y, width, height = rect
        return x, y

    def find_window_by_title(self, title):
        hwnd = win32gui.FindWindow(None, title)
        if hwnd != 0:
            print("Окно с заголовком '{}' найдено.".format(title))
            return hwnd
        else:
            print("Окно с заголовком '{}' не найдено.".format(title))


class PlayerStatisticsTracker:
    def __init__(self):
        self.player_stats = {}

    def update_player_stats(self, steamid, new_stats):
        """
        Метод для обновления статистики и добавление аккаунтов.
        """
        if steamid in self.player_stats:
            old_stats = self.player_stats[steamid]
            if old_stats != new_stats:
                self.player_stats[steamid] = new_stats
                print(f"Статистика для игрока с steamid {steamid} обновлена.")
                return True
        else:
            self.player_stats[steamid] = new_stats
            print(f"Добавлен новый игрок: {steamid}.")

    def get_all_stats(self):
        print(self.player_stats)

    @staticmethod
    def get_score_t(server):
        """
        Метод для получения счета для т стороны.
        """
        try:
            return int(server.get_info("map", "team_t", "score"))
        except ValueError:
            print("Ошибка: Получено нечисловое значение с сервера.")
            return None
        except Exception as e:
            print(f"Произошла ошибка при получении счета: {e}")
            return None

    @staticmethod
    def get_score_ct(server):
        """
        Метод для получения счета для кт стороны.
        """
        try:
            return int(server.get_info("map", "team_ct", "score"))
        except ValueError:
            print("Ошибка: Получено нечисловое значение с сервера.")
            return None
        except Exception as e:
            print(f"Произошла ошибка при получении счета: {e}")
            return None
    @staticmethod
    def get_game_info(server):
        ct_score = server.get_info("map", "team_ct", "score")
        t_score = server.get_info("map", "team_t", "score")
        round_phase = server.get_info("round", "phase")
        with open('sys/game_state.txt', 'w') as file:
            file.write(f'Terrorist {t_score}:{ct_score} Counter-Terrorist\nround phase: {round_phase}')
            file.close()


class WindowController:
    _gkey_cancelled = False

    @staticmethod
    def get_window_at_pos(x, y):
        """
        Метод для получения hwnd окна по координатам.
        """
        window_handle = win32gui.WindowFromPoint((x, y))
        return window_handle

    @staticmethod
    def gkey(hwnd, key, sleep, server):
        """
        Метод для эмуляции нажатия кнопок в игре с проверкой статуса раунда.
        """
        while True:
            try:
                if WindowController._gkey_cancelled:
                    return True

                MAPVK_VK_TO_VSC = 0
                repeat = 0x1

                round_info = server.get_info("round", "phase")

                if str(round_info) != "live":
                    print("Фаза раунда не является 'live'. Отмена выполнения gkey.")
                    WindowController._gkey_cancelled = True
                    return True

                app = Application().connect(handle=hwnd)
                app.window(handle=hwnd).set_focus()

                keycode = win32api.VkKeyScan(key)
                scancode = win32api.MapVirtualKey(keycode, MAPVK_VK_TO_VSC)
                lparam = win32api.MAKELONG(repeat, scancode)
                win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, keycode, lparam)
                time.sleep(sleep)
                win32api.SendMessage(hwnd, win32con.WM_KEYUP, keycode, lparam)
                break
            except Exception as e:
                print(e)
                time.sleep(5)
                pass

    @staticmethod
    def gkey_non_phase(hwnd, key, sleep):
        """
        Метод для эмуляции нажатия кнопок в игре без проверки статуса раунда.
        """
        while True:
            try:
                MAPVK_VK_TO_VSC = 0
                repeat = 0x1

                app = Application().connect(handle=hwnd)
                app.window(handle=hwnd).set_focus()

                keycode = win32api.VkKeyScan(key)
                scancode = win32api.MapVirtualKey(keycode, MAPVK_VK_TO_VSC)
                lparam = win32api.MAKELONG(repeat, scancode)
                win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, keycode, lparam)
                time.sleep(sleep)
                win32api.SendMessage(hwnd, win32con.WM_KEYUP, keycode, lparam)
                break
            except:
                pass

    @staticmethod
    def ct_run(x, y, server):
        """
        Логика передвижения кт стороны.
        """
        window_handle = WindowController.get_window_at_pos(int(x), int(y))
        WindowController.gkey(window_handle, "s", 0.1, server)
        WindowController.gkey(window_handle, "3", 0.1, server)
        WindowController.gkey(window_handle, "f", 0.1, server)
        WindowController.gkey(window_handle, "3", 0.1, server)
        WindowController.gkey(window_handle, "s", 0.5, server)
        WindowController.gkey(window_handle, "a", 0.5, server)
        WindowController.gkey(window_handle, "s", 0.5, server)
        WindowController.gkey(window_handle, "a", 2.5, server)
        WindowController.gkey(window_handle, "w", 2, server)
        if WindowController.gkey(window_handle, "f", 0.1, server):
            return True

    @staticmethod
    def t_run(x, y, server):
        """
        Логика передвижения т стороны.
        """
        window_handle = WindowController.get_window_at_pos(int(x), int(y))
        WindowController.gkey(window_handle, "s", 0.1, server)
        WindowController.gkey(window_handle, "3", 0.1, server)
        WindowController.gkey(window_handle, "f", 0.1, server)
        WindowController.gkey(window_handle, "3", 0.1, server)
        WindowController.gkey(window_handle, "s", 2, server)
        WindowController.gkey(window_handle, "a", 2, server)
        WindowController.gkey(window_handle, "w", 0.3, server)
        WindowController.gkey(window_handle, "a", 2.1, server)
        WindowController.gkey(window_handle, "w", 3.3, server)
        WindowController.gkey(window_handle, "d", 1, server)
        WindowController.gkey(window_handle, "a", 2.0, server)
        WindowController.gkey(window_handle, "w", 3.3, server)
        WindowController.gkey(window_handle, "d", 2.5, server)
        WindowController.gkey(window_handle, "w", 6.3, server)
        WindowController.gkey(window_handle, "d", 1.2, server)
        WindowController.gkey(window_handle, "w", 3.5, server)
        WindowController.gkey(window_handle, "d", 1, server)
        WindowController.gkey(window_handle, "c", 0.1, server)
        WindowController.gkey(window_handle, "c", 0.1, server)
        WindowController.gkey(window_handle, "w", 1.5, server)
        WindowController.gkey(window_handle, "v", 0.1, server)
        WindowController.gkey(window_handle, "w", 0.5, server)
        WindowController.gkey(window_handle, "v", 0.1, server)
        WindowController.gkey(window_handle, "w", 0.5, server)
        WindowController.gkey(window_handle, "v", 0.1, server)
        WindowController.gkey(window_handle, "w", 0.5, server)
        WindowController.gkey(window_handle, "v", 0.1, server)
        WindowController.gkey(window_handle, "w", 0.5, server)
        WindowController.gkey(window_handle, "v", 0.1, server)
        WindowController.gkey(window_handle, "w", 0.5, server)
        WindowController.gkey(window_handle, "v", 0.1, server)
        WindowController.gkey(window_handle, "w", 0.5, server)
        WindowController.gkey(window_handle, "v", 0.1, server)
        WindowController.gkey(window_handle, "w", 0.5, server)
        WindowController.gkey(window_handle, "v", 0.1, server)
        WindowController.gkey(window_handle, "w", 0.5, server)
        WindowController.gkey(window_handle, "v", 0.1, server)
        WindowController.gkey(window_handle, "w", 0.5, server)
        WindowController.gkey_non_phase(window_handle, 'f', 0.1)
        if WindowController.gkey(window_handle, "v", 0.1, server):
            return True

    @staticmethod
    def afk(x, y):
        """
        Логика анти-афк.
        """
        window_handle = WindowController.get_window_at_pos(x, y)
        WindowController.gkey_non_phase(window_handle, "w", 0.1)
        WindowController.gkey_non_phase(window_handle, "z", 1.5)
        time.sleep(0.1)
        WindowController.gkey_non_phase(window_handle, "z", 1.5)

    @staticmethod
    def reset_gkey_cancelled():
        """
        Метод для сброса состояния игры.
        """
        WindowController._gkey_cancelled = False


class GameLogic:
    @staticmethod
    def take_window_with_statistic(a, b, window_coords):
        for window_id in range(int(a), int(b) + 1):
            x, y, status = window_coords.get_coordinates(str(window_id))
            if status:
                print(f'Побежал {window_id} бот с киллом')
                return x, y, window_id

        window_id = random.randint(a, b)
        x, y, status = window_coords.get_coordinates(str(window_id))
        print(f'Побежал рандомный {window_id} бот т.к. команда не имеет киллов')
        return x, y, window_id

    @staticmethod
    def take_window_without_statistic(a, b, window_coords):
        for window_id in range(int(a), int(b) + 1):
            x, y, status = window_coords.get_coordinates(str(window_id))
            if not status:
                print(f'Побежал {window_id} бот без килла')
                return x, y, window_id

        window_id = random.randint(a, b)
        x, y, status = window_coords.get_coordinates(str(window_id))
        print(f'Побежал рандомный {window_id} бот т.к. вся команда сделала хотя бы один килл')
        return x, y, window_id


def play_game(server):
    play_time = time.time()
    team_changed = False
    tracker = PlayerStatisticsTracker()
    window_coords = WindowCoordinates()
    game_logic = GameLogic()

    """Добавляем информацию об окнах."""

    window_coords.add_window("1", 160, 133)
    window_coords.add_window("2", 480, 133)
    window_coords.add_window("3", 800, 133)
    window_coords.add_window("4", 1120, 133)
    window_coords.add_window("5", 1440, 133)
    window_coords.add_window("6", 160, 398)
    window_coords.add_window("7", 480, 398)
    window_coords.add_window("8", 800, 398)
    window_coords.add_window("9", 1120, 398)
    window_coords.add_window("10", 1440, 398)


    """Старт GSI сервера."""

    server = server.GSIServer(("127.0.0.1", 3000), "S8RL9Z6Y22TYQK45JB4V8PHRJJMD9DS9")
    server.start_server()

    print('Ждем начала матча...')
    while server.get_info("round", "phase") != "live":
        tracker.get_game_info(server)
        time.sleep(1)
    print('Матч стартанул')

    afk_time = time.time()

    start_time = time.time()
    print("ждем 5 сек на добавление ботов в панель")
    while time.time() - start_time < 5:
        data = server.get_info("player")
        steamid = data['steamid']
        kills = data['match_stats']['kills']
        tracker.update_player_stats(steamid, kills)

    ct_score = PlayerStatisticsTracker.get_score_ct(server)
    t_score = PlayerStatisticsTracker.get_score_t(server)
    tracker.get_game_info(server)

    data = server.get_info("player")
    steamID = data["steamid"]
    team = data["team"]

    x, y = window_coords.get_window_rect(window_coords.find_window_by_title(steamID))

    if y == 0:
        up = True
    else:
        up = False

    if (up and team == "CT") or (not up and team == "T"):
        ct = True
        print('кт сверху')
    else:
        ct = False

    print('Ждем пока закончатся 2 раунда')
    while (ct_score + t_score) < 2:
        time.sleep(1)
        tracker.get_game_info(server)
        ct_score = PlayerStatisticsTracker.get_score_ct(server)
        t_score = PlayerStatisticsTracker.get_score_t(server)
        if time.time() - afk_time > 90:
            for i in range(1, 11):
                x, y, status = window_coords.get_coordinates(str(i))
                WindowController.afk(x, y)
                afk_time = time.time()


    while True:
        if (ct_score + t_score) == 12 and not team_changed:
            print('Смена сторон')
            if ct:
                ct = False
                team_changed = True
            elif not ct:
                ct = True
                team_changed = True
        elif t_score == 12:
            break

        if ct:
            t_run = False
            for i in range(1, 6):
                x, y, status = window_coords.get_coordinates(str(i))
                if WindowController.ct_run(x, y, server):
                    tracker.get_game_info(server)
                    WindowController.reset_gkey_cancelled()
                    print('Ждем начало нового раунда...')
                    while server.get_info("round", "phase") != "live":
                        ct_score = PlayerStatisticsTracker.get_score_ct(server)
                        t_score = PlayerStatisticsTracker.get_score_t(server)
                        tracker.get_game_info(server)
                        if (ct_score + t_score) == 12 and not team_changed:
                            print('Смена сторон')
                            if ct:
                                ct = False
                                team_changed = True
                            elif not ct:
                                team_changed = True
                                ct = True
                        elif t_score == 12:
                            break
                        if time.time() - afk_time > 90:
                            print('Боты стоят более 1.5 минут, выполняем зарядку')
                            for i in range(6, 11):
                                x, y, status = window_coords.get_coordinates(str(i))
                                WindowController.afk(x, y)
                                afk_time = time.time()
                        time.sleep(1)
                    print('Раунд стартанул')
                    break
                else:
                    t_run = True

            if time.time() - afk_time > 90:
                print('Боты стоят более 1.5 минут, выполняем зарядку')
                for i in range(6, 11):
                    x, y, status = window_coords.get_coordinates(str(i))
                    WindowController.afk(x, y)
                    afk_time = time.time()

            t_id = 6
            kill = False
            if t_run:
                while not kill:
                    x, y, window_id = game_logic.take_window_without_statistic(t_id, 10, window_coords)
                    t_id = window_id
                    if WindowController.t_run(x, y, server):
                        start_time = time.time()
                        print("Ждем 2 сек на обновление статы")
                        while time.time() - start_time < 2:
                            tracker.get_game_info(server)
                            data = server.get_info("player")
                            steamid = data['steamid']
                            kills = data['match_stats']['kills']
                            if tracker.update_player_stats(steamid, kills):
                                window_coords.update_status(str(window_id), True)
                                print(f'Бот с идентификатором {window_id} сделал киллы, помечаю его...')
                                kill = True
                                break
                            else:
                                t_id = t_id + 1
                                if t_id == 11:
                                    t_id = 6

                        WindowController.reset_gkey_cancelled()
                        print('Ждем начало нового раунда...')
                        while server.get_info("round", "phase") != "live":
                            tracker.get_game_info(server)
                            ct_score = PlayerStatisticsTracker.get_score_ct(server)
                            t_score = PlayerStatisticsTracker.get_score_t(server)
                            if (ct_score + t_score) == 12 and not team_changed:
                                print('Смена сторон')
                                if ct:
                                    team_changed = True
                                    ct = False
                                elif not ct:
                                    team_changed = True
                                    ct = True
                            elif t_score == 12:
                                break
                            if time.time() - afk_time > 90:
                                print('Боты стоят более 1.5 минут, выполняем зарядку')
                                for i in range(6, 11):
                                    tracker.get_game_info(server)
                                    x, y, status = window_coords.get_coordinates(str(i))
                                    WindowController.afk(x, y)
                                    afk_time = time.time()
                            time.sleep(1)
                        print('Раунд стартанул')

        elif not ct:
            t_run = False
            for i in range(6, 11):
                tracker.get_game_info(server)
                x, y, status = window_coords.get_coordinates(str(i))
                if WindowController.ct_run(x, y, server):
                    ct_score = PlayerStatisticsTracker.get_score_ct(server)
                    t_score = PlayerStatisticsTracker.get_score_t(server)
                    if (ct_score + t_score) == 12 and not team_changed:
                        print('Смена сторон')
                        if ct:
                            team_changed = True
                            ct = False
                        elif not ct:
                            team_changed = True
                            ct = True
                    elif t_score == 12:
                        break
                    WindowController.reset_gkey_cancelled()
                    print('Ждем начало нового раунда...')
                    while server.get_info("round", "phase") != "live":
                        tracker.get_game_info(server)
                        if time.time() - afk_time > 90:
                            print('Боты стоят более 1.5 минут, выполняем зарядку')
                            for i in range(1, 6):
                                tracker.get_game_info(server)
                                x, y, status = window_coords.get_coordinates(str(i))
                                WindowController.afk(x, y)
                                afk_time = time.time()
                        time.sleep(1)
                    print('Раунд стартанул')
                    break
                else:
                    t_run = True

            if time.time() - afk_time > 90:
                print('Боты стоят более 1.5 минут, выполняем зарядку')
                for i in range(1, 6):
                    tracker.get_game_info(server)
                    x, y, status = window_coords.get_coordinates(str(i))
                    WindowController.afk(x, y)
                    afk_time = time.time()

            t_id = 1
            kill = False
            if t_run:
                while not kill:
                    tracker.get_game_info(server)
                    x, y, window_id = game_logic.take_window_without_statistic(t_id, 5, window_coords)
                    t_id = window_id
                    if WindowController.t_run(x, y, server):
                        tracker.get_game_info(server)
                        start_time = time.time()
                        print("Ждем 2 сек на обновление статы")
                        while time.time() - start_time < 2:
                            tracker.get_game_info(server)
                            data = server.get_info("player")
                            steamid = data['steamid']
                            kills = data['match_stats']['kills']
                            if tracker.update_player_stats(steamid, kills):
                                tracker.get_game_info(server)
                                window_coords.update_status(str(window_id), True)
                                print(f'Бот с идентификатором {window_id} сделал киллы, помечаю его...')
                                kill = True
                                break
                            else:
                                t_id = t_id + 1
                                if t_id == 6:
                                    t_id = 1

                        WindowController.reset_gkey_cancelled()
                        print('Ждем начало нового раунда...')
                        while server.get_info("round", "phase") != "live":
                            tracker.get_game_info(server)
                            ct_score = PlayerStatisticsTracker.get_score_ct(server)
                            t_score = PlayerStatisticsTracker.get_score_t(server)
                            if (ct_score + t_score) == 12 and not team_changed:
                                print('Смена сторон')
                                if ct:
                                    team_changed = True
                                    ct = False
                                elif not ct:
                                    team_changed = True
                                    ct = True
                            elif t_score == 12:
                                break
                            if time.time() - afk_time > 90:
                                print('Боты стоят более 1.5 минут, выполняем зарядку')
                                for i in range(1, 6):
                                    x, y, status = window_coords.get_coordinates(str(i))
                                    WindowController.afk(x, y)
                                    afk_time = time.time()
                            time.sleep(1)
                        print('Раунд стартанул')

    print('Ждем пока закончится игра')
    while (ct_score + t_score) != 24:
        time.sleep(1)
        tracker.get_game_info(server)
        ct_score = PlayerStatisticsTracker.get_score_ct(server)
        t_score = PlayerStatisticsTracker.get_score_t(server)
        if time.time() - afk_time > 90:
            for i in range(1, 11):
                x, y, status = window_coords.get_coordinates(str(i))
                WindowController.afk(x, y)
                afk_time = time.time()

    tracker.get_all_stats()
    # with open('sys/games.txt', 'a') as file:
    #     file.write(str(game_stats))


    print('Игра закончена, счет 12:12')
    server.server_close()
    time.sleep(10)
