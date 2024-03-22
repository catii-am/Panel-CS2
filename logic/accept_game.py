import time
from pywinauto.application import Application
import win32api
import win32con
import win32gui
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
    def accept(x, y):
        hwnd = WindowController.get_window_at_pos(x, y)
        WindowController.mouse_click(x + 160, y + 125, hwnd)
        WindowController.mouse_click(x + 160, y + 125, hwnd)
        WindowController.mouse_click(x + 160, y + 125, hwnd)

def accept_game():
    logic = Logic()
    clear = lambda: os.system('cls')
    for i in range(1, 11):
        if i == 1:
            x, y = 0, 0
            logic.accept(x, y)
        elif i == 6:
            x, y = 0, 240
            logic.accept(x, y)
        elif 2 <= i <= 5:
            x, y = (i - 1) * 320, 0
            logic.accept(x, y)
        elif 7 <= i <= 10:
            x, y = (i - 6) * 320, 240
            logic.accept(x, y)
        print(f'Игра на {i} окне принята')
    clear()
    print('Загрузка игры')
    time.sleep(30)
