import time
from threading import Thread
from flask import Flask, render_template, url_for, request, jsonify
import webview
import asyncio


app = Flask(__name__)


# Определение маршрутов
@app.route('/')
@app.route('/accounts')
def index():
    # Чтение данных из файла accounts.txt
    with open('accounts.txt', 'r') as file:
        accounts_data = file.readlines()

    # Создание списка словарей для хранения данных об аккаунтах
    accounts = []
    for line in accounts_data:
        login, password, privatekey, level, avatar = line.strip().split(':')
        accounts.append({
            'login': login,
            'password': password,
            'privatekey': privatekey,
            'level': level,
            'avatar': avatar
        })
    return render_template('index.html', accounts=accounts)


@app.route('/dashboard')
def dashboard():
    with open('static/score.txt') as file:
        score = file.read()
    # Здесь можно добавить функционал для страницы Dashboard
    return render_template('dashboard.html', score=score)


@app.route('/settings')
def settings():
    # Здесь можно добавить функционал для страницы Settings
    return render_template('settings.html')


@app.route('/launch_steam', methods=['POST'])
def launch_steam():
    # Получаем данные из запроса
    data = request.json
    selected_accounts = data.get('selectedAccounts', [])

    # Проверяем количество выбранных аккаунтов
    if len(selected_accounts) < 10:
        error_message = 'Выбрано менее 10 аккаунтов'
        return jsonify({'error': error_message}), 400
    elif len(selected_accounts) > 10:
        error_message = 'Выбрано более 10 аккаунтов'
        return jsonify({'error': error_message}), 400

    return jsonify(selected_accounts)


@app.route('/start_game', methods=['GET'])
def start_game():
    # Здесь выполняйте код, который нужно выполнить при нажатии на кнопку "Start Game"
    # Например, запустите игру или выполните другие действия
    print('start game')
    # Возвращаем ответ клиенту
    return jsonify({'message': 'Game started successfully'}), 200


@app.route('/save_settings', methods=['POST'])
def save_settings():
    steam_path = request.form['steam_path']
    launch_parameters = request.form['launch_parameters']

    # Здесь код для записи значений в файл config.cfg
    with open('static/config.cfg', 'w') as f:
        f.write(f'SteamPath:{steam_path}\n')
        f.write(f'Arguments:{launch_parameters}\n')

    return jsonify({'message': 'Settings saved successfully'})

# Запуск приложения
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')