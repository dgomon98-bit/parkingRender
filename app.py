from flask import Flask, jsonify, render_template_string, request
import sqlite3
import os
import requests

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

    cursor.execute("PRAGMA table_info(parkings)")
    columns = [col[1] for col in cursor.fetchall()]
    

    cursor.execute("SELECT COUNT(*) FROM parkings")
    count = cursor.fetchone()[0]

    if count == 0:
        # Основные парковки 
        main_parkings = [
            ('Кремль', 55.752023, 37.617499, 8, 150, 'Красная площадь', None, 'main'),
            ('ТЦ Афимолл Сити', 55.749162, 37.539742, 45, 200, 'Пресненская наб., 2', '100–150 руб/час', 'main'),
            ('Парк Горького', 55.731412, 37.603648, 85, 120, 'ул. Крымский Вал, 9', None, 'main'),
            ('ВДНХ', 55.825200, 37.638100, 5, 80, 'пр. Мира, 119', '100 руб/час', 'main'),
            ('Москва-Сити', 55.749700, 37.539300, 12, 150, 'Пресненская наб., 8', '200–300 руб/час', 'main'),
            ('ТЦ Европейский', 55.746600, 37.516500, 35, 100, 'пл. Киевского Вокзала, 2', '150 руб/час', 'main'),
            ('ТЦ Авиапарк', 55.803000, 37.533100, 60, 200, 'Ходынский бульвар, 4', '100 руб/час', 'main'),
            ('ЦУМ', 55.760803, 37.619776, 15, 50, 'ул. Петровка, 2', '200 руб/час', 'main'),
            ('ГУМ', 55.754700, 37.621600, 2, 30, 'Красная площадь, 3', '150 руб/час', 'main'),
            ('ТРЦ Охотный ряд', 55.753391, 37.612322, 25, 70, 'пл. Манежная, 1', '100 руб/час', 'main'),
            ('Парк Зарядье', 55.751300, 37.627800, 40, 80, 'ул. Варварка, 6', '200 руб/час', 'main'),
            ('Лужники', 55.715900, 37.553800, 70, 150, 'ул. Лужники, 24', '100–150 руб/час', 'main'),
            ('Воробьевы горы', 55.710800, 37.553200, 50, 80, 'Воробьевы горы', None, 'main'),
            ('Крокус Сити', 55.825800, 37.390300, 90, 300, '66 км МКАД', '100 руб/час', 'main'),
            ('Мега Химки', 55.897200, 37.424400, 120, 500, 'Ленинградское ш., 1', 'бесплатно первые 2 часа', 'main'),
            ('ТЦ Водный', 55.840000, 37.486000, 45, 150, 'Головинское ш., 5', '50 руб/час', 'main'),
            ('ТРК Атриум', 55.756000, 37.655000, 70, 250, 'Земляной Вал, 33', '150 руб/час', 'main'),
            ('ТЦ Метрополис', 55.823000, 37.498000, 120, 400, 'Ленинградское ш., 16А', '100 руб/час', 'main'),
            ('ТЦ Ходынское поле', 55.790000, 37.535000, 35, 120, 'Ходынский бульвар, 4', '50 руб/час', 'main'),
            ('ТЦ Columbus', 55.612200, 37.604500, 55, 200, 'ул. Кировоградская, 9', 'бесплатно', 'main'),
            ('ТЦ Каширский двор', 55.654500, 37.648000, 40, 150, 'Каширское ш., 61', None, 'main'),
            ('ТРК Vegas', 55.623000, 37.654000, 110, 350, 'Каширское ш., 1', 'бесплатно', 'main'),
            ('ТЦ Глобал Сити', 55.640000, 37.618000, 30, 100, 'ул. Днепропетровская, 2', None, 'main'),
            ('ТЦ Европарк', 55.743000, 37.419000, 65, 180, 'Ярцевская ул., 25', '100 руб/час', 'main'),
            ('ТРК Океания', 55.728500, 37.479000, 90, 300, 'Кутузовский пр., 57', '100 руб/час', 'main'),
            ('ТРЦ Щелковский', 55.812000, 37.798000, 85, 250, 'ул. Уральская, 2', '50 руб/час', 'main'),
            ('ТРЦ Город', 55.752000, 37.753000, 50, 200, 'шоссе Энтузиастов, 12', 'бесплатно', 'main'),
            ('ТРЦ "Ривьера"', 55.690000, 37.580000, 200, 500, 'Автозаводская ул., 18', '100 руб/час', 'main'),
            ('ТЦ "Золотой Вавилон"', 55.838000, 37.660000, 150, 400, 'пр. Мира, 211', 'бесплатно первые 2 часа', 'main'),
            ('ТРЦ "Фестиваль"', 55.805000, 37.500000, 80, 250, 'ул. Фестивальная, 2Б', '50 руб/час', 'main'),
            ('ТЦ "Варшавский"', 55.648000, 37.620000, 60, 200, 'Варшавское ш., 87', None, 'main'),
            ('ТРК "Щука"', 55.807000, 37.457000, 130, 350, 'ул. Щукинская, 42', '100 руб/час', 'main'),
            ('ТЦ "Калейдоскоп"', 55.858000, 37.395000, 90, 300, 'ул. Сходненская, 56', '50 руб/час', 'main'),
            ('ТРЦ "Июнь"', 55.916000, 37.740000, 250, 600, 'ул. Коммунистическая, 1', 'бесплатно', 'main'),
            ('ТЦ "РИО"', 55.874000, 37.525000, 180, 450, 'Дмитровское ш., 163А', '100 руб/час', 'main'),
            ('ТЦ "Мозаика"', 55.712000, 37.680000, 70, 250, 'ул. Кожуховская, 13', None, 'main'),
            ('ТРК "Саларис"', 55.620000, 37.430000, 300, 800, 'Киевское ш., 23-й км', 'бесплатно', 'main'),
        ]

        #Второстепенные парковки(чтобы улучшить точность : Invoke-WebRequest -Uri http://localhost:5000/admin/fix_coordinates -Method POST ввести в терминал powershell)
        additional_parkings = [
            # Вокруг Кремля
            ('Парковка ул. Воздвиженка', 55.7530, 37.6110, 12, 50, 'ул. Воздвиженка, 5', '200 руб/час', 'additional'),
            ('Парковка Моховая ул.', 55.7545, 37.6140, 8, 40, 'ул. Моховая, 15', '150 руб/час', 'additional'),
            ('Парковка Театральный пр.', 55.7580, 37.6190, 20, 80, 'Театральный проезд, 3', '180 руб/час', 'additional'),
            # Вокруг Афимолла
            ('Парковка Башня Федерация', 55.7480, 37.5370, 30, 120, 'Пресненская наб., 12', '250 руб/час', 'additional'),
            ('Парковка Expocentre', 55.7510, 37.5400, 45, 150, 'Краснопресненская наб., 14', '200 руб/час', 'additional'),
            # Вокруг Парка Горького
            ('Парковка ул. Тимура Фрунзе', 55.7310, 37.6000, 18, 60, 'ул. Тимура Фрунзе, 11', '100 руб/час', 'additional'),
            ('Парковка Ленинский пр.', 55.7250, 37.5950, 25, 90, 'Ленинский проспект, 20', '120 руб/час', 'additional'),
            # Вокруг ВДНХ
            ('Парковка Ботанический сад', 55.8300, 37.6400, 40, 150, 'ул. Ботаническая, 4', '80 руб/час', 'additional'),
            ('Парковка ул. Сергея Эйзенштейна', 55.8230, 37.6440, 35, 110, 'ул. Сергея Эйзенштейна, 3', '100 руб/час', 'additional'),
            # Вокруг Москва-Сити
            ('Парковка 1-й Красногвардейский пр.', 55.7510, 37.5350, 22, 100, '1-й Красногвардейский пр., 15', '220 руб/час', 'additional'),
            ('Парковка Тестовская ул.', 55.7530, 37.5270, 15, 70, 'ул. Тестовская, 10', '200 руб/час', 'additional'),
            # Вокруг Европейского
            ('Парковка Бережковская наб.', 55.7440, 37.5200, 28, 90, 'Бережковская наб., 12', '150 руб/час', 'additional'),
            ('Парковка пл. Европы', 55.7480, 37.5200, 18, 60, 'площадь Европы, 2', '170 руб/час', 'additional'),
            # Вокруг Авиапарка
            ('Парковка Ходынский бульвар', 55.8050, 37.5300, 50, 200, 'Ходынский бульвар, 8', '80 руб/час', 'additional'),
            ('Парковка ул. Авиаконструктора Микояна', 55.8000, 37.5250, 30, 120, 'ул. Авиаконструктора Микояна, 10', '90 руб/час', 'additional'),
            # Вокруг ЦУМа
            ('Парковка Петровка', 55.7620, 37.6200, 10, 40, 'ул. Петровка, 5', '250 руб/час', 'additional'),
            ('Парковка Кузнецкий Мост', 55.7590, 37.6240, 12, 45, 'ул. Кузнецкий Мост, 7', '230 руб/час', 'additional'),
            # Вокруг ГУМа
            ('Парковка Никольская ул.', 55.7560, 37.6240, 8, 30, 'ул. Никольская, 10', '200 руб/час', 'additional'),
            ('Парковка Ильинка', 55.7540, 37.6250, 10, 35, 'ул. Ильинка, 5', '210 руб/час', 'additional'),
            # Вокруг Охотного ряда
            ('Парковка Тверская ул.', 55.7590, 37.6150, 15, 50, 'ул. Тверская, 7', '200 руб/час', 'additional'),
            ('Парковка Манежная пл.', 55.7560, 37.6130, 5, 25, 'Манежная площадь, 1', '190 руб/час', 'additional'),
            # Вокруг Зарядья
            ('Парковка Варварка', 55.7520, 37.6300, 20, 70, 'ул. Варварка, 8', '180 руб/час', 'additional'),
            ('Парковка Китайгородский пр.', 55.7490, 37.6320, 15, 55, 'Китайгородский проезд, 7', '170 руб/час', 'additional'),
            # Вокруг Лужников
            ('Парковка ул. Лужники', 55.7170, 37.5500, 60, 200, 'ул. Лужники, 20', '100 руб/час', 'additional'),
            ('Парковка Новолужнецкий пр.', 55.7140, 37.5600, 45, 150, 'Новолужнецкий проезд, 8', '110 руб/час', 'additional'),
            # Вокруг Воробьёвых гор
            ('Парковка Университетский пр.', 55.7080, 37.5500, 30, 120, 'Университетский проспект, 13', '90 руб/час', 'additional'),
            ('Парковка Мичуринский пр.', 55.7050, 37.5400, 40, 140, 'Мичуринский проспект, 19', '100 руб/час', 'additional'),
            # Вокруг Крокус Сити
            ('Парковка Крокус Экспо', 55.8280, 37.3850, 150, 500, '65-66 км МКАД', '100 руб/час', 'additional'),
            ('Парковка МКАД 66-й км', 55.8220, 37.3950, 80, 300, '66-й км МКАД', '80 руб/час', 'additional'),
            # Вокруг Мега Химки
            ('Парковка Мега Химки 2', 55.8990, 37.4210, 200, 600, 'Ленинградское ш., 1к1', 'бесплатно', 'additional'),
            ('Парковка Ленинградское ш., 5', 55.8940, 37.4290, 50, 180, 'Ленинградское ш., 5', '50 руб/час', 'additional'),
            # Вокруг  Водного
            ('Парковка Головинское ш., 7', 55.8420, 37.4830, 25, 80, 'Головинское ш., 7', '60 руб/час', 'additional'),
            ('Парковка ул. Адмирала Макарова', 55.8380, 37.4900, 30, 100, 'ул. Адмирала Макарова, 6', '70 руб/час', 'additional'),
            # Вокруг Атриума
            ('Парковка Курского вокзала', 55.7580, 37.6600, 60, 200, 'площадь Курского Вокзала', '150 руб/час', 'additional'),
            ('Парковка ул. Казакова', 55.7550, 37.6580, 35, 130, 'ул. Казакова, 12', '120 руб/час', 'additional'),
            # Вокруг Метрополиса
            ('Парковка Ленинградское ш., 14', 55.8250, 37.4950, 45, 150, 'Ленинградское ш., 14', '100 руб/час', 'additional'),
            ('Парковка 3-й Балтийский пер.', 55.8200, 37.5000, 20, 70, '3-й Балтийский пер., 4', '90 руб/час', 'additional'),
            # Вокруг Ходынского поля
            ('Парковка ул. Зорге', 55.7920, 37.5320, 30, 110, 'ул. Зорге, 15', '80 руб/час', 'additional'),
            ('Парковка ул. Куусинена', 55.7880, 37.5400, 22, 85, 'ул. Куусинена, 6', '70 руб/час', 'additional'),
            # Вокруг Колумбуса
            ('Парковка ул. Кировоградская, 20', 55.6100, 37.6020, 40, 140, 'ул. Кировоградская, 20', '60 руб/час', 'additional'),
            ('Парковка Варшавское ш., 140', 55.6150, 37.6100, 35, 120, 'Варшавское ш., 140', '50 руб/час', 'additional'),
            # Вокруг Каширского двора
            ('Парковка Каширское ш., 63', 55.6560, 37.6450, 25, 90, 'Каширское ш., 63', '70 руб/час', 'additional'),
            ('Парковка ул. Москворечье', 55.6500, 37.6520, 20, 75, 'ул. Москворечье, 12', '60 руб/час', 'additional'),
            # Вокруг Вегаса
            ('Парковка Каширское ш., 3', 55.6260, 37.6500, 80, 250, 'Каширское ш., 3', 'бесплатно', 'additional'),
            ('Парковка Пролетарский пр.', 55.6200, 37.6600, 45, 160, 'Пролетарский проспект, 30', '50 руб/час', 'additional'),
            # Вокруг Глобал Сити
            ('Парковка ул. Днепропетровская, 5', 55.6420, 37.6160, 15, 60, 'ул. Днепропетровская, 5', '70 руб/час', 'additional'),
            ('Парковка ул. Чертановская', 55.6370, 37.6200, 20, 70, 'ул. Чертановская, 30', '60 руб/час', 'additional'),
            # Вокруг Европарка
            ('Парковка Ярцевская ул., 27', 55.7450, 37.4160, 30, 100, 'Ярцевская ул., 27', '80 руб/час', 'additional'),
            ('Парковка Рублевское ш., 50', 55.7400, 37.4100, 40, 130, 'Рублевское ш., 50', '90 руб/час', 'additional'),
            # Вокруг Океании
            ('Парковка Кутузовский пр., 55', 55.7300, 37.4750, 60, 200, 'Кутузовский пр., 55', '120 руб/час', 'additional'),
            ('Парковка ул. Герасима Курина', 55.7250, 37.4850, 35, 120, 'ул. Герасима Курина, 20', '100 руб/час', 'additional'),
            # Вокруг Щелковского
            ('Парковка Щелковское ш., 100', 55.8150, 37.8020, 30, 110, 'Щелковское ш., 100', '50 руб/час', 'additional'),
            ('Парковка ул. Уральская, 10', 55.8100, 37.7950, 25, 90, 'ул. Уральская, 10', '60 руб/час', 'additional'),
            # Вокруг Города
            ('Парковка шоссе Энтузиастов, 15', 55.7540, 37.7500, 20, 80, 'шоссе Энтузиастов, 15', '70 руб/час', 'additional'),
            ('Парковка ул. Плеханова', 55.7500, 37.7600, 18, 65, 'ул. Плеханова, 12', '60 руб/час', 'additional'),
            # Вокруг Ривьеры
            ('Парковка Автозаводская ул., 16', 55.6920, 37.5780, 50, 180, 'Автозаводская ул., 16', '80 руб/час', 'additional'),
            ('Парковка ул. Ленинская Слобода', 55.6880, 37.5850, 40, 150, 'ул. Ленинская Слобода, 26', '70 руб/час', 'additional'),
            # Вокруг Золотого Вавилона
            ('Парковка пр. Мира, 213', 55.8400, 37.6580, 60, 200, 'пр. Мира, 213', 'бесплатно первые 2 часа', 'additional'),
            ('Парковка ул. Бажова', 55.8350, 37.6650, 35, 120, 'ул. Бажова, 8', '50 руб/час', 'additional'),
            # Вокруг Фестиваля
            ('Парковка ул. Фестивальная, 4', 55.8070, 37.4970, 25, 90, 'ул. Фестивальная, 4', '60 руб/час', 'additional'),
            ('Парковка Ленинградское ш., 74', 55.8020, 37.5050, 30, 100, 'Ленинградское ш., 74', '70 руб/час', 'additional'),
            # Вокруг Варшавского
            ('Парковка Варшавское ш., 89', 55.6500, 37.6180, 20, 75, 'Варшавское ш., 89', '50 руб/час', 'additional'),
            ('Парковка ул. Подольских Курсантов', 55.6450, 37.6250, 18, 60, 'ул. Подольских Курсантов, 18', '40 руб/час', 'additional'),
            # Вокруг Щуки
            ('Парковка ул. Щукинская, 44', 55.8090, 37.4550, 45, 150, 'ул. Щукинская, 44', '80 руб/час', 'additional'),
            ('Парковка ул. Авиационная', 55.8050, 37.4600, 30, 110, 'ул. Авиационная, 30', '70 руб/час', 'additional'),
            # Вокруг Калейдоскопа
            ('Парковка ул. Сходненская, 58', 55.8600, 37.3930, 30, 110, 'ул. Сходненская, 58', '60 руб/час', 'additional'),
            ('Парковка ул. Героев Панфиловцев', 55.8550, 37.4000, 25, 90, 'ул. Героев Панфиловцев, 20', '50 руб/час', 'additional'),
            # Вокруг Июня 
            ('Парковка ул. Коммунистическая, 3', 55.9180, 37.7420, 80, 250, 'ул. Коммунистическая, 3', 'бесплатно', 'additional'),
            ('Парковка ул. Мира, 2', 55.9140, 37.7350, 50, 180, 'ул. Мира, 2', '40 руб/час', 'additional'),
            # Вокруг РИО 
            ('Парковка Дмитровское ш., 165', 55.8760, 37.5230, 60, 200, 'Дмитровское ш., 165', '70 руб/час', 'additional'),
            ('Парковка ул. Софьи Ковалевской', 55.8720, 37.5280, 35, 120, 'ул. Софьи Ковалевской, 10', '60 руб/час', 'additional'),
            # Вокруг Мозаики
            ('Парковка ул. Кожуховская, 15', 55.7140, 37.6780, 25, 90, 'ул. Кожуховская, 15', '50 руб/час', 'additional'),
            ('Парковка ул. Южнопортовая', 55.7100, 37.6850, 30, 100, 'ул. Южнопортовая, 22', '40 руб/час', 'additional'),
            # Вокруг Салариса
            ('Парковка Киевское ш., 23-й км, стр.2', 55.6220, 37.4280, 120, 400, 'Киевское ш., 23-й км, стр.2', 'бесплатно', 'additional'),
            ('Парковка ул. Адмирала Корнилова', 55.6180, 37.4350, 70, 250, 'ул. Адмирала Корнилова, 20', '30 руб/час', 'additional'),
        ]

        cursor.executemany('''
            INSERT INTO parkings (name, lat, lon, free_spots, total_spots, address, price, type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', main_parkings + additional_parkings)

        print(f"Добавлено {len(main_parkings)} основных и {len(additional_parkings)} дополнительных парковок")

    conn.commit()
    conn.close()

init_db()


MAIN_HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Карта парковок Москвы</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
            animation: slideDown 0.5s ease;
        }
        
        .header h1 {
            color: #333;
            font-size: 28px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .header h1 i {
            color: #ff4757;
        }
        
        .auth-buttons {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 50px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
        }
        
        .btn-primary {
            background: linear-gradient(45deg, #ff4757, #ff3838);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 7px 15px rgba(255, 71, 87, 0.4);
        }
        
        .btn-secondary {
            background: transparent;
            color: #333;
            border: 2px solid #ddd;
        }
        
        .btn-secondary:hover {
            border-color: #ff4757;
            color: #ff4757;
        }
        
        .btn-help {
            background: transparent;
            color: #ff4757;
            border: 2px solid #ff4757;
            border-radius: 50px;
            padding: 12px 20px;
        }
        .btn-help:hover {
            background: #ff4757;
            color: white;
            transform: translateY(-3px);
            box-shadow: 0 7px 15px rgba(255, 71, 87, 0.4);
        }
        
        #map {
            width: 100%;
            height: 70vh;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            overflow: hidden;
            animation: fadeIn 0.8s ease;
            background: #f0f0f0;
        }
        
        .legend {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            margin-top: 25px;
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 20px;
            border-radius: 10px;
            background: rgba(0,0,0,0.02);
            transition: transform 0.3s ease;
        }
        
        .legend-item:hover {
            transform: translateX(5px);
            background: rgba(0,0,0,0.05);
        }
        
        .status-dot {
            width: 20px;
            height: 20px;
            border-radius: 50%;
        }
        
        .status-green {
            background: linear-gradient(45deg, #00b894, #00a085);
            box-shadow: 0 0 10px rgba(0, 184, 148, 0.3);
        }
        
        .status-yellow {
            background: linear-gradient(45deg, #fdcb6e, #e17055);
            box-shadow: 0 0 10px rgba(253, 203, 110, 0.3);
        }
        
        .status-red {
            background: linear-gradient(45deg, #ff7675, #d63031);
            box-shadow: 0 0 10px rgba(255, 118, 117, 0.3);
        }
        
        .stats {
            display: flex;
            gap: 30px;
            margin-top: 20px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
        }
        
        .stat-box {
            text-align: center;
            padding: 15px;
            flex: 1;
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        
        .stat-box:hover {
            transform: translateY(-5px);
        }
        
        .stat-value {
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }

        .support {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            margin-top: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            text-align: center;
            animation: fadeIn 0.8s ease;
        }
        .support h3 {
            color: #333;
            margin-bottom: 20px;
            font-size: 22px;
            font-weight: 600;
        }
        .support h3 i {
            color: #ff4757;
            margin-right: 10px;
        }
        .support .contacts {
            display: flex;
            justify-content: center;
            gap: 40px;
            flex-wrap: wrap;
        }
        .support .contacts div {
            display: flex;
            align-items: center;
            gap: 12px;
            color: #555;
            font-size: 18px;
            background: rgba(0,0,0,0.02);
            padding: 12px 25px;
            border-radius: 50px;
            transition: transform 0.3s ease;
        }
        .support .contacts div:hover {
            transform: translateY(-3px);
            background: rgba(255, 71, 87, 0.1);
        }
        .support .contacts i {
            color: #ff4757;
            font-size: 22px;
        }

        /* Стили для модального окна-гайда */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
            animation: fadeIn 0.3s ease;
        }
        .modal-content {
            background: rgba(255,255,255,0.95);
            margin: 5% auto;
            padding: 30px;
            border-radius: 20px;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            transform: translateY(0);
            animation: slideDown 0.4s ease;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .modal-header h2 {
            color: #333;
            font-size: 24px;
        }
        .modal-header h2 i {
            color: #ff4757;
            margin-right: 10px;
        }
        .close {
            color: #aaa;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        .close:hover {
            color: #ff4757;
        }
        .modal-body {
            margin-bottom: 25px;
        }
        .modal-body p {
            color: #555;
            margin-bottom: 15px;
            font-size: 16px;
        }
        .modal-body ul {
            list-style: none;
            padding: 0;
        }
        .modal-body li {
            margin-bottom: 12px;
            color: #666;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .dot {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            display: inline-block;
        }
        .dot.green { background: linear-gradient(45deg, #00b894, #00a085); }
        .dot.yellow { background: linear-gradient(45deg, #fdcb6e, #e17055); }
        .dot.red { background: linear-gradient(45deg, #ff7675, #d63031); }
        .modal-footer {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .dont-show {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #666;
            font-size: 14px;
            cursor: pointer;
        }
        .dont-show input {
            width: 18px;
            height: 18px;
            cursor: pointer;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: scale(0.95);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                gap: 20px;
                text-align: center;
            }
            
            .auth-buttons {
                flex-direction: column;
                width: 100%;
            }
            
            .btn {
                width: 100%;
                justify-content: center;
            }
            
            #map {
                height: 60vh;
            }
            
            .support .contacts {
                gap: 20px;
            }
            .support .contacts div {
                width: 100%;
                justify-content: center;
            }
        }
        
        .map-error {
            color: #ff4757;
            font-weight: bold;
            text-align: center;
            padding: 20px;
        }
        
        .map-error a {
            color: #ff4757;
            text-decoration: underline;
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>
                <i class="fas fa-parking"></i>
                Парковки Москвы - Карта свободных мест
            </h1>
            <div class="auth-buttons">
                <button class="btn btn-help" onclick="showGuide()">
                    <i class="fas fa-question-circle"></i> Помощь
                </button>
                <a href="/login" class="btn btn-primary">
                    <i class="fas fa-sign-in-alt"></i>
                    Войти
                </a>
                <a href="/register" class="btn btn-secondary">
                    <i class="fas fa-user-plus"></i>
                    Регистрация
                </a>
            </div>
        </div>
        
        <div id="map"></div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="status-dot status-green"></div>
                <div>
                    <strong>Много свободных мест</strong><br>
                    <small>≥ 30% свободно</small>
                </div>
            </div>
            <div class="legend-item">
                <div class="status-dot status-yellow"></div>
                <div>
                    <strong>Мало свободных мест</strong><br>
                    <small>10-30% свободно</small>
                </div>
            </div>
            <div class="legend-item">
                <div class="status-dot status-red"></div>
                <div>
                    <strong>Почти нет мест</strong><br>
                    <small>< 10% свободно</small>
                </div>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-box" style="background: rgba(0, 184, 148, 0.1);">
                <i class="fas fa-check-circle" style="color: #00b894; font-size: 24px;"></i>
                <div id="free-count" class="stat-value">0</div>
                <div>Свободные парковки</div>
            </div>
            <div class="stat-box" style="background: rgba(253, 203, 110, 0.1);">
                <i class="fas fa-exclamation-triangle" style="color: #fdcb6e; font-size: 24px;"></i>
                <div id="medium-count" class="stat-value">0</div>
                <div>Почти заполнены</div>
            </div>
            <div class="stat-box" style="background: rgba(255, 118, 117, 0.1);">
                <i class="fas fa-times-circle" style="color: #ff7675; font-size: 24px;"></i>
                <div id="full-count" class="stat-value">0</div>
                <div>Заполнены</div>
            </div>
        </div>

        <div class="support">
            <h3>
                <i class="fas fa-headset"></i>
                Тех-поддержка. Ответим на Ваши вопросы.
            </h3>
            <div class="contacts">
                <div>
                    <i class="fas fa-phone-alt"></i>
                    +7 (916) 651-07-43
                </div>
                <div>
                    <i class="fas fa-envelope"></i>
                    retygret80@gmail.com
                </div>
            </div>
        </div>
    </div>

    <!-- Модальное окно-гайд -->
    <div id="guide-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2><i class="fas fa-compass"></i> Добро пожаловать!</h2>
                <span class="close" onclick="closeGuide()">&times;</span>
            </div>
            <div class="modal-body">
                <p>Это карта парковок Москвы. Вот как ей пользоваться:</p>
                <ul>
                    <li><span class="dot green"></span> <strong>Зелёные метки</strong> – много свободных мест (≥30%)</li>
                    <li><span class="dot yellow"></span> <strong>Жёлтые метки</strong> – мало мест (10–30%)</li>
                    <li><span class="dot red"></span> <strong>Красные метки</strong> – почти нет мест (<10%)</li>
                    <li>🔍 Приблизьте карту (зум ≥15), чтобы увидеть дополнительные парковки</li>
                    <li>👆 Нажмите на метку для подробной информации</li>
                </ul>
            </div>
            <div class="modal-footer">
                <button class="btn btn-primary" onclick="closeGuide()">Понятно, спасибо!</button>
                <label class="dont-show">
                    <input type="checkbox" id="dont-show-guide"> Не показывать при следующем входе
                </label>
            </div>
        </div>
    </div>
    
    <script>
        let map;
        let placemarks = [];
        let additionalPlacemarks = [];
        let freeParkings = 0, mediumParkings = 0, fullParkings = 0;

        
        function getPriceColor(priceStr) {
            if (!priceStr || priceStr === 'None' || priceStr === '' || priceStr.toLowerCase().includes('бесплатно')) {
                return { bg: '#cccccc20', text: '#666' }; // серый для бесплатных/неопределенных
            }
            const match = priceStr.match(/\\d+/); // ищем первое число
            if (!match) return { bg: '#cccccc20', text: '#666' };
            const num = parseInt(match[0], 10);
            if (num < 100) return { bg: '#00b89420', text: '#00b894' };      // зелёный
            if (num >= 100 && num <= 150) return { bg: '#fdcb6e20', text: '#fdcb6e' }; // жёлтый
            return { bg: '#ff767520', text: '#ff7675' };                      // красный
        }
        
        function loadYandexMaps(apiKey) {
            return new Promise((resolve, reject) => {
                if (typeof ymaps !== 'undefined') {
                    resolve();
                    return;
                }
                if (!apiKey) {
                    reject(new Error('API ключ не указан. Получите ключ на https://developer.tech.yandex.ru/ и установите переменную окружения YANDEX_MAPS_API_KEY или впишите его в код.'));
                    return;
                }
                const script = document.createElement('script');
                script.src = `https://api-maps.yandex.ru/2.1/?lang=ru_RU&apikey=${apiKey}`;
                script.async = true;
                script.onload = () => {
                    console.log('Яндекс.Карты загружены');
                    resolve();
                };
                script.onerror = () => reject(new Error('Не удалось загрузить Яндекс.Карты. Проверьте подключение к интернету.'));
                document.head.appendChild(script);
            });
        }
        
        async function init() {
            try {
                const apiKey = "{{ api_key|safe }}";
                await loadYandexMaps(apiKey);
                
                ymaps.ready(() => {
                    map = new ymaps.Map('map', {
                        center: [55.75, 37.61],
                        zoom: 11,
                        controls: ['zoomControl', 'fullscreenControl', 'typeSelector']
                    });
                    
                    loadParkings();
                    
                    map.events.add('boundschange', function (e) {
                        if (e.get('newZoom') !== undefined) {
                            updateAdditionalVisibility(e.get('newZoom'));
                        }
                    });
                    
                    setInterval(loadParkings, 30000);
                });
            } catch (error) {
                console.error('Ошибка инициализации карты:', error);
                document.getElementById('map').innerHTML = `<div class="map-error"><i class="fas fa-exclamation-triangle"></i><p>${error.message}</p><p>Подробнее: <a href="https://developer.tech.yandex.ru/" target="_blank">Получить ключ Яндекс.Карт</a></p></div>`;
            }
        }
        
        function loadParkings() {
            fetch('/api/parkings')
                .then(response => response.json())
                .then(parkings => {
                    map.geoObjects.removeAll();
                    placemarks = [];
                    additionalPlacemarks = [];
                    
                    freeParkings = 0;
                    mediumParkings = 0;
                    fullParkings = 0;
                    
                    parkings.forEach(parking => {
                        let status, color, icon;
                        
                        if (parking.free_percent >= 30) {
                            status = "Свободно";
                            color = "#00b894";
                            icon = "islands#greenIcon";
                            freeParkings++;
                        } else if (parking.free_percent >= 10) {
                            status = "Мало мест";
                            color = "#fdcb6e";
                            icon = "islands#yellowIcon";
                            mediumParkings++;
                        } else {
                            status = "Заполнена";
                            color = "#ff7675";
                            icon = "islands#redIcon";
                            fullParkings++;
                        }
                        
                       
                        let priceHtml = '';
                        if (parking.price && parking.price !== 'None' && parking.price !== '') {
                            const priceColor = getPriceColor(parking.price);
                            priceHtml = `<div style="margin-top: 10px; padding: 8px; border-radius: 8px; background: ${priceColor.bg}; color: ${priceColor.text}; font-weight: 500;"><i class="fas fa-ruble-sign"></i> ${parking.price}</div>`;
                        }
                        
                        const placemark = new ymaps.Placemark(
                            [parking.lat, parking.lon],
                            {
                                balloonContent: `
                                    <div style="padding: 15px; max-width: 300px;">
                                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
                                            <div style="width: 12px; height: 12px; border-radius: 50%; background: ${color};"></div>
                                            <h3 style="margin: 0; color: #333;">${parking.name}</h3>
                                        </div>
                                        <div style="background: ${color}20; padding: 10px; border-radius: 8px; margin-bottom: 15px;">
                                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                                <span>Статус:</span>
                                                <strong style="color: ${color};">${status}</strong>
                                            </div>
                                            <div style="display: flex; justify-content: space-between;">
                                                <span>Свободно:</span>
                                                <strong>${parking.free_spots} из ${parking.total_spots}</strong>
                                            </div>
                                        </div>
                                        <div style="margin-bottom: 15px;">
                                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                                <span>Заполненность:</span>
                                                <strong>${(100 - parking.free_percent).toFixed(1)}%</strong>
                                            </div>
                                            <div style="background: #eee; height: 8px; border-radius: 4px; overflow: hidden;">
                                                <div style="width: ${100 - parking.free_percent}%; height: 100%; background: ${color};"></div>
                                            </div>
                                        </div>
                                        ${parking.address ? `<div style="color: #666; font-size: 14px;"><i class="fas fa-map-marker-alt"></i> ${parking.address}</div>` : ''}
                                        ${priceHtml}
                                    </div>
                                `,
                                iconCaption: parking.name,
                                hintContent: `${parking.name} - ${status}`
                            },
                            {
                                preset: icon,
                                iconColor: color,
                                balloonCloseButton: true,
                                hideIconOnBalloonOpen: false
                            }
                        );
                        
                        map.geoObjects.add(placemark);
                        placemarks.push(placemark);
                        
                        if (parking.type === 'additional') {
                            additionalPlacemarks.push(placemark);
                        }
                    });
                    
                    const currentZoom = map.getZoom();
                    updateAdditionalVisibility(currentZoom);
                    
                    updateStats();
                })
                .catch(error => {
                    console.error('Ошибка загрузки парковок:', error);
                });
        }
        
        function updateAdditionalVisibility(zoom) {
            const threshold = 15;
            const visible = zoom >= threshold;
            additionalPlacemarks.forEach(pm => {
                pm.options.set('visible', visible);
            });
            console.log(`Дополнительные парковки ${visible ? 'показаны' : 'скрыты'} (зум: ${zoom})`);
        }
        
        function updateStats() {
            document.getElementById('free-count').textContent = freeParkings;
            document.getElementById('medium-count').textContent = mediumParkings;
            document.getElementById('full-count').textContent = fullParkings;
        }

        // Функции для гайда
        function showGuide() {
            document.getElementById('guide-modal').style.display = 'block';
        }

        function closeGuide() {
            document.getElementById('guide-modal').style.display = 'none';
            if (document.getElementById('dont-show-guide').checked) {
                localStorage.setItem('guideShown', 'true');
            }
        }

        // Показываем гайд при первом посещении
        window.onload = function() {
            if (!localStorage.getItem('guideShown')) {
                showGuide();
            }
        };
        
        init();
    </script>
</body>
</html>
'''



LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход - Парковки Москвы</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            max-width: 500px;
            width: 90%;
            margin: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px 20px 0 0;
            padding: 25px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .header h1 {
            color: #333;
            font-size: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }
        
        .header h1 i {
            color: #ff4757;
        }
        
        .form-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 0 0 20px 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        
        .form-group label i {
            color: #ff4757;
            margin-right: 8px;
        }
        
        .form-group input {
            width: 100%;
            padding: 15px;
            border: 2px solid #eee;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #ff4757;
        }
        
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 50px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            text-decoration: none;
        }
        
        .btn-primary {
            background: linear-gradient(45deg, #ff4757, #ff3838);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 7px 15px rgba(255, 71, 87, 0.4);
        }
        
        .back-link {
            text-align: center;
            margin-top: 20px;
        }
        
        .back-link a {
            color: #ff4757;
            text-decoration: none;
            font-weight: 500;
        }
        
        .back-link a:hover {
            text-decoration: underline;
        }
        
        .error-message {
            background: rgba(255, 71, 87, 0.1);
            color: #ff4757;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            border: 1px solid #ff4757;
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>
                <i class="fas fa-parking"></i>
                Вход
            </h1>
        </div>
        <div class="form-container">
            {% if error %}
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i> {{ error }}
            </div>
            {% endif %}
            
            <form method="post">
                <div class="form-group">
                    <label><i class="fas fa-user"></i> Логин</label>
                    <input type="text" name="username" placeholder="Введите логин" required>
                </div>
                <div class="form-group">
                    <label><i class="fas fa-lock"></i> Пароль</label>
                    <input type="password" name="password" placeholder="Введите пароль" required>
                </div>
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-sign-in-alt"></i> Войти
                </button>
            </form>
            <div class="back-link">
                <a href="/"><i class="fas fa-arrow-left"></i> Вернуться на главную</a>
            </div>
        </div>
    </div>
</body>
</html>
'''


REGISTER_HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Регистрация - Парковки Москвы</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            max-width: 500px;
            width: 90%;
            margin: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px 20px 0 0;
            padding: 25px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .header h1 {
            color: #333;
            font-size: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }
        
        .header h1 i {
            color: #ff4757;
        }
        
        .form-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 0 0 20px 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        
        .form-group label i {
            color: #ff4757;
            margin-right: 8px;
        }
        
        .form-group input {
            width: 100%;
            padding: 15px;
            border: 2px solid #eee;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #ff4757;
        }
        
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 50px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            text-decoration: none;
        }
        
        .btn-primary {
            background: linear-gradient(45deg, #ff4757, #ff3838);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 7px 15px rgba(255, 71, 87, 0.4);
        }
        
        .back-link {
            text-align: center;
            margin-top: 20px;
        }
        
        .back-link a {
            color: #ff4757;
            text-decoration: none;
            font-weight: 500;
        }
        
        .back-link a:hover {
            text-decoration: underline;
        }
        
        .success-message {
            background: rgba(0, 184, 148, 0.1);
            color: #00b894;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            border: 1px solid #00b894;
        }
        
        .error-message {
            background: rgba(255, 71, 87, 0.1);
            color: #ff4757;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            border: 1px solid #ff4757;
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>
                <i class="fas fa-parking"></i>
                Регистрация
            </h1>
        </div>
        <div class="form-container">
            {% if success %}
            <div class="success-message">
                <i class="fas fa-check-circle"></i> {{ success }}
            </div>
            {% endif %}
            
            {% if error %}
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i> {{ error }}
            </div>
            {% endif %}
            
            <form method="post">
                <div class="form-group">
                    <label><i class="fas fa-user"></i> Логин</label>
                    <input type="text" name="username" placeholder="Придумайте логин" required>
                </div>
                <div class="form-group">
                    <label><i class="fas fa-lock"></i> Пароль</label>
                    <input type="password" name="password" placeholder="Придумайте пароль" required>
                </div>
                <div class="form-group">
                    <label><i class="fas fa-lock"></i> Подтверждение пароля</label>
                    <input type="password" name="confirm_password" placeholder="Повторите пароль" required>
                </div>
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-user-plus"></i> Зарегистрироваться
                </button>
            </form>
            <div class="back-link">
                <a href="/"><i class="fas fa-arrow-left"></i> Вернуться на главную</a>
            </div>
        </div>
    </div>
</body>
</html>
'''


@app.route('/api/parkings')
def get_parkings():
    conn = sqlite3.connect('parking_app.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT name, lat, lon, free_spots, total_spots, address, price, type FROM parkings ORDER BY name')
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
    return render_template_string(MAIN_HTML, api_key=YANDEX_API_KEY)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin':
            return render_template_string(LOGIN_HTML, success="Вы успешно вошли! (Демо-режим)")
        else:
            error = 'Неверный логин или пароль. Попробуйте admin/admin.'
    return render_template_string(LOGIN_HTML, error=error)

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
    return render_template_string(REGISTER_HTML, error=error, success=success)

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
    def geocode(address):
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": YANDEX_API_KEY,
            "geocode": address + ", Москва",
            "format": "json"
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            members = data["response"]["GeoObjectCollection"]["featureMember"]
            if members:
                pos = members[0]["GeoObject"]["Point"]["pos"]
                lon, lat = map(float, pos.split())
                return lat, lon
        except Exception as e:
            print(f"Геокодирование {address}: ошибка {e}")
        return None, None

    conn = sqlite3.connect('parking_app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, address FROM parkings WHERE address IS NOT NULL AND address != ''")
    parkings = cursor.fetchall()

    fixed = 0
    failed = 0
    for pid, name, address in parkings:
        lat, lon = geocode(address)
        if lat is not None and lon is not None:
            cursor.execute(
                "UPDATE parkings SET lat = ?, lon = ? WHERE id = ?",
                (lat, lon, pid)
            )
            fixed += 1
            print(f"Исправлено: {name} -> ({lat:.6f}, {lon:.6f})")
        else:
            failed += 1
            print(f"Не удалось: {name} (адрес: {address})")

    conn.commit()
    conn.close()
    return jsonify({"fixed": fixed, "failed": failed, "total": len(parkings)})

if __name__ == '__main__':
    print(" http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
