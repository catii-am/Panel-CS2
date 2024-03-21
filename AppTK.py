from tkinter import *
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from logic import steam_login, tile_windows, play_game, make_lobby, accept_game


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

        # Добавление логотипа
        image = Image.open("logo.png")
        image.thumbnail((64, 64))  # Масштабируем изображение до 32x32
        photo = ImageTk.PhotoImage(image)
        self.logo = ttk.Button(image=photo, compound="left", command=self.show_accounts)
        self.logo.image = photo

        # Название приложения
        self.app_name_label = tk.Label(self.header_frame, text="Catti Farm", font=("Arial", 16))
        self.app_name_label.grid(row=0, column=1, padx=10, pady=10)

        # Создание фрейма для кнопок навигации
        self.nav_frame = tk.Frame(self.header_frame)
        self.nav_frame.grid(row=0, column=2, padx=10, pady=10)

        # Создание кнопок навигации
        nav_buttons = [
            ("DashBoard", "static/icon/dashboard.png", self.show_dashboard),
            ("Accounts", "static/icon/accounts.png", self.show_accounts),
            ("Settings", "static/icon/settings.png", self.show_settings),
            ("Info", "static/icon/info.png", self.show_info),
            ("Notification", "static/icon/notification.png", self.show_notifications),
            ("Profile", "static/icon/account.png", self.show_profile)
        ]

        for index, (text, icon, command) in enumerate(nav_buttons):
            # Загружаем изображение и масштабируем его
            image = Image.open(icon)
            image.thumbnail((32, 32))  # Масштабируем изображение до 32x32
            photo = ImageTk.PhotoImage(image)

            button = ttk.Button(self.nav_frame, image=photo, compound="right", command=command)
            button.image = photo  # Сохраняем ссылку на изображение, чтобы избежать сборки мусора
            button.grid(row=0, column=index, padx=5, pady=5)

        # По умолчанию отображаем DashBoard
        # self.show_accounts()

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
        # Здесь будет код для отображения экрана DashBoard
        print("DashBoard screen")

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

        # self.overrideredirect(True)

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

        start_game_button = ttk.Button(button_block, text="Start game", command=self.start_game)
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
        print("start game")

    def accept_game(self):
        accept_game.accept_game()

    def on_checkbox_click(self, index):
        self.selected_index = index  # Сохраняем выбранный индекс

    def launch_steam(self):
        if self.selected_index is not None:
            checkbox_index = (self.selected_index // 10) + 1
            steam_login.steam_login(checkbox_index)

    def arrange_windows(self):
        tile_windows.move_window()

    def make_lobby(self):
        make_lobby.make_lobby()

    def load_accounts(self):
        # Загрузка аккаунтов из файла accounts.txt
        accounts = make_list_from_file("accounts.txt")

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
        print('add account')


class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        config_file = "config.cfg"
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
        with open("config.cfg", "w") as file:
            file.write(f'SteamPath:{steam_path}\nArguments:{launch_parameters}')
        # Ваш код для сохранения настроек


if __name__ == "__main__":
    app = Application()
    app.mainloop()
