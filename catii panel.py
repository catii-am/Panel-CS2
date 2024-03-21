from logic import play_game
from logic import steam_login
from gsi import server
import pyperclip
from logic import tile_windows
from logic import make_lobby
from logic import accept_game

config = ('bind c "yaw +3409 1 1";bind z +duck;sensitivity 1.2;bind v +attack2;bind f "toggle fps_max 10 30";bind q '
          'disconnect;bind g "fps_max 60";fps_max 60')

if __name__ == "__main__":
    # tile, invite = steam_login.steam_login()
    # if tile:
    #     tile_windows.move_window()
    # if invite:
    #     make_lobby.make_lobby()
    # print('В буфер обмена был скопирован конфиг, вставь его в консоль и начинай поиск игры')
    # pyperclip.copy(config)
    # while True:
    #     accept_game.accept_game()
        play_game.play_game(server)
