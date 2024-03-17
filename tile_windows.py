import time
from pywinauto.application import Application
import win32api
import win32con
import win32gui


class WindowController:
    @staticmethod
    def get_window_at_pos(x, y):
        window_handle = win32gui.WindowFromPoint((x, y))
        return window_handle

    @staticmethod
    def move_window_at_pos(x, y, window_handle):
        win32gui.SetWindowPos(window_handle, win32con.HWND_TOP, x, y, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)

    @staticmethod
    def close_info(x, y, hwnd):
        app = Application().connect(handle=hwnd)
        app.window(handle=hwnd).set_focus()

        win32api.SetCursorPos((x+160, y+70))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x+160, y+70, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x+160, y+70, 0, 0)
        time.sleep(0.1)
        win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
        time.sleep(0.1)
        win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
        time.sleep(0.1)
        win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)

def move_window():
    window_controller = WindowController()
    for i in range(1, 11):
        hwnd = window_controller.get_window_at_pos(960, 540)
        if i == 1:
            x, y = 0, 0
            window_controller.move_window_at_pos(x, y, hwnd)
            window_controller.close_info(x, y, hwnd)
        elif i == 6:
            x, y = 0, 240
            window_controller.move_window_at_pos(x, y, hwnd)
            window_controller.close_info(x, y, hwnd)
        elif 2 <= i <= 5:
            x, y = (i - 1) * 320, 0
            window_controller.move_window_at_pos((i - 1) * 320, 0, hwnd)
            window_controller.close_info(x, y, hwnd)
        elif 7 <= i <= 10:
            x, y = (i - 6) * 320, 240
            window_controller.move_window_at_pos((i - 6) * 320, 240, hwnd)
            window_controller.close_info(x, y, hwnd)

    print('Все окна выставлены, переходим к созданию лобби...')
