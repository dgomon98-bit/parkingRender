import os
import sqlite3
import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

YANDEX_API_KEY = os.getenv('YANDEX_API_KEY', '1a4b06f9-3473-48fe-8bd2-26417e144fe2')

def init_db():
    conn = sqlite3.connect('parking_app.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parkings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            free_spots INTEGER DEFAULT 0,
            total_spots INTEGER DEFAULT 100,
            address TEXT,
            price TEXT,
            type TEXT DEFAULT 'main',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Проверка наличия данных (вставка демо-парковок)
    cursor.execute("SELECT COUNT(*) FROM parkings")
    count = cursor.fetchone()[0]
    if count == 0:
        # Вставка основных и дополнительных парковок (список сокращён для примера)
        # В реальном коде вставьте полные списки из вашего исходного кода
        main_parkings = [
            ('Кремль', 55.752023, 37.617499, 8, 150, 'Красная площадь', None, 'main'),
            # ... остальные
        ]
        additional_parkings = [
            ('Парковка ул. Воздвиженка', 55.7530, 37.6110, 12, 50, 'ул. Воздвиженка, 5', '200 руб/час', 'additional'),
            # ... остальные
        ]
        cursor.executemany('''
            INSERT INTO parkings (name, lat, lon, free_spots, total_spots, address, price, type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', main_parkings + additional_parkings)
        print("Добавлены демо-парковки")
    conn.commit()
    conn.close()

init_db()

@app.route('/api/parkings')
def get_parkings():
    conn = sqlite3.connect('parking_app.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, lat, lon, free_spots, total_spots, address, price, type FROM parkings ORDER BY name')
    parkings = []
    for row in cursor.fetchall():
        parking = dict(row)
        free_percent = (parking['free_spots'] / parking['total_spots'] * 100) if parking['total_spots'] > 0 else 0
        parking['free_percent'] = round(free_percent, 1)
        parkings.append(parking)
    conn.close()
    return jsonify(parkings)

@app.route('/')
def index():
    return render_template('index.html', api_key=YANDEX_API_KEY)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin':
            return render_template('login.html', success="Вы успешно вошли! (Демо-режим)")
        else:
            error = 'Неверный логин или пароль. Попробуйте admin/admin.'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    success = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        if not username or not password:
            error = 'Заполните все поля.'
        elif password != confirm:
            error = 'Пароли не совпадают.'
        else:
            success = f'Пользователь {username} успешно зарегистрирован! (Демо-режим)'
    return render_template('register.html', error=error, success=success)

@app.route('/add_parking', methods=['POST'])
def add_parking():
    try:
        data = request.get_json()
        conn = sqlite3.connect('parking_app.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO parkings (name, lat, lon, free_spots, total_spots, address, price, type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['lat'],
            data['lon'],
            data['free_spots'],
            data['total_spots'],
            data.get('address', ''),
            data.get('price', None),
            data.get('type', 'main')
        ))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Парковка добавлена'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/admin/fix_coordinates', methods=['POST'])
def fix_coordinates():
    # (функция без изменений, оставлена как есть)
    pass  # реализация из исходного кода

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
