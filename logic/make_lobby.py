import time
from pywinauto.application import Application
import win32api
import win32con
import win32gui
import pyperclip
from pywinauto.keyboard import send_keys
import os


class WindowController:
    @staticmethod
    def get_window_at_pos(x, y):
        window_handle = win32gui.WindowFromPoint((x, y))
        return window_handle

    @staticmethod
    def mouse_click(x, y, hwnd):
        app = Application().connect(handle=hwnd)
        app.window(handle=hwnd).set_focus()
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        time.sleep(0.1)

class Logic:
    @staticmethod
    def open_code_leader(x, y):
        hwnd = WindowController.get_window_at_pos(x+160, y+120) # Получаем hwnd окна
        WindowController.mouse_click(x+160, y+120, hwnd) # Кликаем по окну дабы его активировать
        WindowController.mouse_click(x+315, y+120, hwnd)
        time.sleep(0.7)
        WindowController.mouse_click(x+320, y+32, hwnd)

    @staticmethod
    def open_code(x, y):
        hwnd = WindowController.get_window_at_pos(x + 160, y + 120) # Получаем hwnd окна
        WindowController.mouse_click(x + 160, y + 120, hwnd) # Кликаем по окну дабы его активировать
        WindowController.mouse_click(x + 315, y + 120, hwnd)
        time.sleep(0.7)
        WindowController.mouse_click(x + 316, y + 32, hwnd)
        time.sleep(0.1)
        WindowController.mouse_click(x + 316, y + 32, hwnd)
        time.sleep(0.7)
        WindowController.mouse_click(x + 177, y + 160, hwnd)
        time.sleep(0.2)
        WindowController.mouse_click(x + 177, y + 160, hwnd)
        time.sleep(0.2)
        WindowController.mouse_click(x + 177, y + 160, hwnd)
        time.sleep(0.2)
        WindowController.mouse_click(x + 200, y + 160, hwnd)
        time.sleep(0.1)

    @staticmethod
    def invite_to_lobby(x, y):
        hwnd = WindowController.get_window_at_pos(x+160, y+120) # Получаем hwnd окна
        WindowController.mouse_click(x+160, y+120, hwnd) # Кликаем по окну дабы его активировать
        WindowController.mouse_click(x + 135, y + 140, hwnd)
        time.sleep(1)
        invite_code = pyperclip.paste()
        send_keys(invite_code)
        time.sleep(0.5)
        WindowController.mouse_click(x + 140, y + 145, hwnd)
        time.sleep(2)
        WindowController.mouse_click(x + 177, y + 170, hwnd)
        WindowController.mouse_click(x + 177, y + 175, hwnd)
        WindowController.mouse_click(x + 177, y + 180, hwnd)
        WindowController.mouse_click(x + 177, y + 185, hwnd)
        WindowController.mouse_click(x + 177, y + 190, hwnd)
        time.sleep(1)
        WindowController.mouse_click(x + 200, y + 170, hwnd)
        time.sleep(0.5)

    @staticmethod
    def accept_invite(x, y):
        hwnd = WindowController.get_window_at_pos(x + 160, y + 120) # Получаем hwnd окна
        WindowController.mouse_click(x + 160, y + 120, hwnd) # Кликаем по окну дабы его активировать
        WindowController.mouse_click(x + 315, y + 120, hwnd)
        time.sleep(0.7)
        WindowController.mouse_click(x + 258, y + 55, hwnd)
        time.sleep(0.5)



def make_lobby():
    clear = lambda: os.system('cls')
    logic = Logic()
    print('Приглашаем верхние акки в лобби...')
    for i in range(2, 6):
        logic.open_code_leader(0, 0)
        x, y = (i - 1) * 320, 0
        logic.open_code(x, y)
        logic.invite_to_lobby(0, 0)
    print('Все акки сверху были приглашены в лобби, принимаем приглашение...')
    for i in range(2, 6):
        x, y = (i - 1) * 320, 0
        logic.accept_invite(x, y)

    print('Приглашения приняты, приступаем к нижним аккам...')
    for i in range(2, 6):
        logic.open_code_leader(0, 240)
        x, y = (i - 1) * 320, 240
        logic.open_code(x, y)
        logic.invite_to_lobby(0, 240)
    print('Все акки снизу были приглашены в лобби, принимаем приглашение...')
    for i in range(2, 6):
        x, y = (i - 1) * 320, 240
        logic.accept_invite(x, y)
    print('Все акки снизу приняли приглашения')
    time.sleep(1)
    clear()
    print('Все аккаунты были приглашены')
