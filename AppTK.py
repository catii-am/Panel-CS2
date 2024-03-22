import time
from tkinter import *
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
from logic import steam_login, tile_windows, play_game, make_lobby, accept_game
from gsi import server
import threading
from tkinter import filedialog

import sys
import os

if hasattr(sys, '_MEIPASS'):
    temp_dir = sys._MEIPASS
else:
    temp_dir = os.path.abspath(".")

def extract_values_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        shared_secret_start = content.find('"shared_secret"') + len('"shared_secret":"')
        shared_secret_end = content.find('"', shared_secret_start + 1)
        shared_secret = content[shared_secret_start:shared_secret_end]

        username_start = content.rfind('"account_name":"') + len('"account_name":"')
        username_end = content.find('"', username_start + 1)
        username = content[username_start:username_end]

    return shared_secret, username

def username_exists_in_accounts(username, accounts_data):
    for line in accounts_data:
        if username in line:
            return True
    return False

def make_list_from_file(file):
    with open(file, 'r') as f:
        return [x for x in f.read().split("\n") if x]


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        # Название приложения
        self.title("Catii Farm")
        self.overrideredirect(True)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = 874
        window_height = 72

        x = (screen_width - window_width) // 2
        y = screen_height - window_height - 48

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Создание фрейма для шапки
        self.header_frame = tk.Frame(self)
        self.header_frame.pack(side="top", fill="x")

        # Название приложения
        self.app_name_label = tk.Label(self.header_frame, text="Catti Farm", font=("Arial", 16))
        self.app_name_label.grid(row=0, column=1, padx=10, pady=10)

        # Создание фрейма для кнопок навигации
        self.nav_frame = tk.Frame(self.header_frame)
        self.nav_frame.grid(row=0, column=2, padx=10, pady=10)

        # Создание кнопок навигации
        nav_buttons = [
            ("DashBoard", os.path.join(temp_dir, 'static/icon/dashboard.png'), self.show_dashboard),
            ("Accounts", os.path.join(temp_dir, "static/icon/accounts.png"), self.show_accounts),
            ("Settings", os.path.join(temp_dir, "static/icon/settings.png"), self.show_settings),
            ("Info", os.path.join(temp_dir, "static/icon/info.png"), self.show_info),
            ("Notification", os.path.join(temp_dir, "static/icon/notification.png"), self.show_notifications),
            ("Profile", os.path.join(temp_dir, "static/icon/account.png"), self.show_profile)
        ]

        for index, (text, icon, command) in enumerate(nav_buttons):
            # Загружаем изображение и масштабируем его
            image = Image.open(icon)
            image.thumbnail((32, 32))  # Масштабируем изображение до 32x32
            photo = ImageTk.PhotoImage(image)

            button = ttk.Button(self.nav_frame, image=photo, compound="right", command=command)
            button.image = photo  # Сохраняем ссылку на изображение, чтобы избежать сборки мусора
            button.grid(row=0, column=index, padx=5, pady=5)

        # Обработчики событий для перемещения окна
        self.start_x = 0
        self.start_y = 0
        self.bind('<ButtonPress-1>', self.start_move)
        self.bind('<B1-Motion>', self.on_move)

    def start_move(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_move(self, event):
        x = self.winfo_x() + (event.x - self.start_x)
        y = self.winfo_y() + (event.y - self.start_y)
        self.geometry('+{x}+{y}'.format(x=x, y=y))

    def show_dashboard(self):
        dashboard_window = DashboardWindow(self)
        dashboard_window.grab_set()

    def show_accounts(self):
        accounts_window = AccountsWindow(self)
        accounts_window.grab_set()

    def show_settings(self):
        settings_window = SettingsWindow(self)
        settings_window.grab_set()

    def show_info(self):
        # Здесь будет код для отображения экрана Info
        print("Info screen")

    def show_notifications(self):
        # Здесь будет код для отображения экрана Notification
        print("Notification screen")

    def show_profile(self):
        # Здесь будет код для отображения экрана Profile
        print("Profile screen")


class AccountsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.selected_index = None

        self.title("Accounts")
        self.geometry("600x400")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = 600
        window_height = 400

        x = (screen_width - window_width) // 2
        y = screen_height - window_height - 48 - 104

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Надпись "Accounts"
        accounts_label = tk.Label(self, text="Accounts", font=("Arial", 16))
        accounts_label.pack(side="top", pady=10)

        # Кнопка "Add account"
        add_account_button = ttk.Button(self, text="Add account", command=self.add_account)
        add_account_button.pack(side="right", padx=10, pady=10)

        # Создание фрейма с прокруткой для списка аккаунтов
        accounts_frame = tk.Frame(self)
        accounts_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(accounts_frame)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(accounts_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        # Создание внутреннего фрейма для списка аккаунтов
        self.accounts_inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.accounts_inner_frame, anchor="nw")

        # Загрузка аккаунтов из файла
        self.load_accounts()

        # Обработка прокрутки
        self.accounts_inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Блок кнопок
        button_block = tk.Frame(self)
        button_block.pack(side="bottom", pady=10)

        start_game_button = ttk.Button(button_block, text="Play game", command=self.start_game)
        start_game_button.grid(row=0, column=0, padx=5)

        accept_game_button = ttk.Button(button_block, text="Accept game", command=self.accept_game)
        accept_game_button.grid(row=0, column=1, padx=5)

        launch_steam_button = ttk.Button(button_block, text="Launch Steam", command=lambda: self.launch_steam())
        launch_steam_button.grid(row=0, column=2, padx=5)

        arrange_windows_button = ttk.Button(button_block, text="Arrange windows", command=self.arrange_windows)
        arrange_windows_button.grid(row=0, column=3, padx=5)

        gather_lobby_button = ttk.Button(button_block, text="Gather lobby", command=self.make_lobby)
        gather_lobby_button.grid(row=0, column=4, padx=5)

    def get_checkbox_index(self):
        # Определяем индекс чекбокса
        index = (self.selected_index // 10) + 1
        return index

    def start_game(self):
        answer = messagebox.askyesno("Confirmation", "КТ сверху?")
        thread = threading.Thread(target=play_game.play_game, args=(server, answer,))
        thread.start()

    def accept_game(self):
        thread = threading.Thread(target=accept_game.accept_game)
        thread.start()

    def on_checkbox_click(self, index):
        self.selected_index = index  # Сохраняем выбранный индекс

    def launch_steam(self):
        if self.selected_index is not None:
            checkbox_index = (self.selected_index // 10) + 1
            thread = threading.Thread(target=steam_login.steam_login, args=(checkbox_index,))
            thread.start()

    def arrange_windows(self):
        thread = threading.Thread(target=tile_windows.move_window)
        thread.start()

    def make_lobby(self):
        thread = threading.Thread(target=make_lobby.make_lobby)
        thread.start()
    def load_accounts(self):
        # Загрузка аккаунтов из файла accounts.txt
        accounts = make_list_from_file("sys/accounts.txt")

        # Создаем чекбоксы для выбора каждых 10 аккаунтов
        for i in range(0, len(accounts), 10):
            start_index = i
            end_index = min(i + 9, len(accounts) - 1)

            # Создаем промежуточный фрейм для каждых 10 аккаунтов
            intermediate_frame = tk.Frame(self.accounts_inner_frame)
            intermediate_frame.grid(row=i, column=0, sticky="w")

            select_label = ttk.Checkbutton(intermediate_frame, text=f"{start_index + 1}-{end_index + 1}",
                                           command=lambda index=start_index: self.on_checkbox_click(index))
            select_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

            for j in range(start_index, end_index + 1):
                username = accounts[j].split(":")[0]
                account_label = tk.Label(intermediate_frame, text=username)
                account_label.grid(row=j - start_index + 1, column=1, sticky="w", padx=20, pady=2)

        # Устанавливаем размер колонок для выравнивания
        self.accounts_inner_frame.grid_columnconfigure(1, weight=1)

    def add_account(self):
        users = []

        # Открыть диалоговое окно для выбора файлов
        file_paths = filedialog.askopenfilenames(title="Выберите файлы аккаунтов",
                                                 filetypes=[("Text Files", "*.maFile")])
        accounts_file = "sys/accounts.txt"

        # Проверить, что были выбраны файлы
        if file_paths:
            # Открыть файлы и добавить информацию в accounts.txt
            with open(accounts_file, 'r') as file:
                accounts_data = file.readlines()

            for file_path in file_paths:
                shared_secret, username = extract_values_from_file(file_path)
                if username:
                    if not username_exists_in_accounts(username, accounts_data):
                        password = None
                        users.append([username, password, shared_secret])

            # Проверяем, не пустой ли кортеж users
            if not users:
                messagebox.showinfo("Информация", "Не найдены новые аккаунты.")
            else:
                add_account_window = AddAccountWindow(self, users)
                self.wait_window(add_account_window)

                if add_account_window.window_closed:
                    messagebox.showinfo("Информация", "Добавление аккаунтов отменено")
                    return False

                else:
                    with open("sys/accounts.txt", 'a') as file:
                        for user_info in users:
                            username, password, shared_secret = user_info
                            file.write(f"{username}:{password}:{shared_secret}\n")
        else:
            messagebox.showinfo("Информация", "Не выбраны файлы аккаунтов.")


class AddAccountWindow(tk.Toplevel):
    def __init__(self, parent, users):
        super().__init__(parent)
        self.window_closed = None
        self.users = users
        self.password_entries = []  # Создаем список для хранения объектов Entry
        self.title("Добавить аккаунты")
        self.geometry("500x350")
        self.setup_ui()

    def setup_ui(self):
        # Создаем фрейм для размещения Entry и меток
        entry_frame = tk.Frame(self)
        entry_frame.pack(side="left", fill="both", expand=True)

        # Создаем Canvas для добавления прокручиваемой области
        self.canvas = tk.Canvas(entry_frame, borderwidth=0)
        self.frame = tk.Frame(self.canvas)
        self.vsb = tk.Scrollbar(entry_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        # Упаковываем виджеты в окне
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw")

        # Привязываем событие прокрутки колеса мыши
        self.frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # Создаем и размещаем Entry для каждого пользователя
        for user_info in self.users:
            username = user_info[0]
            frame = tk.Frame(self.frame)
            frame.pack(fill="x", padx=10, pady=5)
            label = tk.Label(frame, text=username)
            label.pack(side="left", padx=5)
            entry = tk.Entry(frame)
            entry.pack(side="right", padx=5)
            # Добавляем объект Entry в список password_entries
            self.password_entries.append(entry)

        # Обновляем размещение фрейма с прокручиваемым содержимым
        self.update_frame()

        # Создаем фрейм для кнопки "Сохранить"
        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", fill="x")

        # Создаем и размещаем кнопку "Сохранить" во внутреннем фрейме
        save_button = tk.Button(button_frame, text="Сохранить", command=self.save_passwords)
        save_button.pack(side="right", pady=10, padx=10)

        # Переопределяем обработчик закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.cancel)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def update_frame(self):
        # Устанавливаем высоту фрейма с содержимым равной высоте содержимого
        self.frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def save_passwords(self):
        for i, password_entry in enumerate(self.password_entries):
            password = password_entry.get()
            # Получаем соответствующий пользователю объект Entry
            user_info = self.users[i]
            if password:
                user_info[1] = password
            else:
                messagebox.showerror("Ошибка", f"Не введен пароль для пользователя {user_info[0]}")
                return

        self.destroy()

    def cancel(self):
        self.window_closed = True
        self.destroy()


class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        config_file = "sys/config.cfg"
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

        self.selected_index = None

        self.title("Settings")
        self.geometry("600x200")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = 600
        window_height = 400

        x = (screen_width - window_width) // 2
        y = screen_height - window_height - 48 - 104

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Текст "Settings"
        settings_label = tk.Label(self, text="Settings", font=("Arial", 16))
        settings_label.pack(pady=10)

        # Разделитель
        ttk.Separator(self, orient="horizontal").pack(fill="x")

        # Создаем фрейм для элементов
        input_frame = tk.Frame(self)
        input_frame.pack(pady=10)

        # Текст "Steam Path" и поле ввода
        steam_path_label = tk.Label(input_frame, text="Steam Path:")
        steam_path_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.steam_path_entry = tk.Entry(input_frame)
        self.steam_path_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Текст "Launch Parameters" и поле ввода
        launch_parameters_label = tk.Label(input_frame, text="Launch Parameters:")
        launch_parameters_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.launch_parameters_entry = tk.Entry(input_frame)
        self.launch_parameters_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.steam_path_entry.insert(0, steam_path)
        self.launch_parameters_entry.insert(0, arguments)

        # Кнопка "Save"
        save_button = ttk.Button(self, text="Save", command=self.save_settings)
        save_button.pack(pady=10)

    def save_settings(self):
        steam_path = self.steam_path_entry.get()
        launch_parameters = self.launch_parameters_entry.get()
        config_file = "sys/config.cfg"
        with open(config_file, "w") as file:
            file.write(f'SteamPath:{steam_path}\nArguments:{launch_parameters}')
        # Код для сохранения настроек


class DashboardWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Dashboard")
        self.geometry("600x300")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = 600
        window_height = 300

        x = (screen_width - window_width) // 2
        y = screen_height - window_height - 48 - 104

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Текст "Game Score"
        self.game_score_label = tk.Label(self, text="Game Score", font=("Arial", 16))
        self.game_score_label.pack(pady=10)

        # Счет матча из файла game_state.txt
        self.match_score_label = tk.Label(self, text="", font=("Arial", 14))
        self.match_score_label.pack()

        # Текущее состояние матча из файла game_state.txt
        self.current_state_label = tk.Label(self, text="")
        self.current_state_label.pack()

        # Периодическое обновление данных
        self.update_data()

    def update_data(self):
        game_info = make_list_from_file('sys/game_state.txt')
        match_score = game_info[0]
        current_state = game_info[1]

        # Обновляем счет матча из файла game_state.txt
        self.match_score_label.config(text=match_score)

        # Обновляем текущее состояние матча из файла game_state.txt
        self.current_state_label.config(text=current_state)

        # Повторно вызываем этот метод через 1000 миллисекунд (1 секунда)
        self.after(1000, self.update_data)

if __name__ == "__main__":
    try:
        app = Application()
        app.mainloop()
    except Exception as e:
        print(e)
        time.sleep(30)
