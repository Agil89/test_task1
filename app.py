from flask import Flask, request, jsonify
import sqlite3
import requests
import random
import time
from threading import Thread

app = Flask(__name__)

class User:
    def __init__(self, id, username, balance):
        self.id = id
        self.username = username
        self.balance = balance

    @staticmethod
    def create_table():
        # Создание таблицы пользователей в базе данных SQLite, если она не существует
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY, username TEXT, balance REAL)''')
        conn.commit()
        conn.close()

    @staticmethod
    def add_user(username, balance):
        # Добавление нового пользователя в базу данных
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, balance) VALUES (?, ?)", (username, balance))
        conn.commit()
        conn.close()

    @staticmethod
    def update_balance(user_id, new_balance):
        # Обновление баланса пользователя в базе данных
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, user_id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_balance(user_id):
        # Получение текущего баланса пользователя из базы данных
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
        balance = c.fetchone()[0]
        conn.close()
        return balance

def fetch_weather(city):
    # Получение данных о погоде для указанного города из открытого API
    api_key = 'api_key'
    url = f'https://api.weatherapi.com/v1/current.json?q={city}&key={api_key}'
    response = requests.get(url)
    data = response.json()
    if 'current' in data:
        temperature_celsius = data['current']['temp_c']
        return temperature_celsius
    else:
        return None

@app.route('/update_balance', methods=['POST'])
def update_balance():
    # Обновление баланса пользователя на основе температуры в указанном городе
    data = request.json
    user_id = data.get('userId')
    city = data.get('city')
    temperature = fetch_weather(city)
    if temperature is None:
        return jsonify({'error': 'Failed to fetch weather data'}), 500

    current_balance = User.get_balance(user_id)
    if current_balance is None:
        return jsonify({'error': 'User not found'}), 404

    new_balance = current_balance + temperature
    if new_balance < 0:
        return jsonify({'error': 'Insufficient balance'}), 400

    User.update_balance(user_id, new_balance)
    return jsonify({'message': 'Balance updated successfully'}), 200

if __name__ == '__main__':
    User.create_table()

    # Добавление некоторых тестовых пользователей
    User.add_user('user1', 10000)
    User.add_user('user2', 12000)
    User.add_user('user3', 8000)
    User.add_user('user4', 15000)
    User.add_user('user5', 5000)

    # Симуляция запросов
    cities = ['New York', 'London', 'Paris', 'Tokyo', 'Moscow']
    def simulate_requests():
        while True:
            city = random.choice(cities)
            user_id = random.randint(1, 5)
            update_balance_data = {'userId': user_id, 'city': city}
            response = requests.post('http://127.0.0.1:5000/update_balance', json=update_balance_data)
            print(response.json())
            time.sleep(60)  # Симуляция запросов каждую минуту

    Thread(target=simulate_requests).start()

    app.run(debug=True)
