from flask import Flask, request, send_file, jsonify
import sqlite3 as sq
import os
import zipfile
from io import BytesIO
from datetime import datetime, date, timedelta
import requests  # Для отправки данных на сервер
import json  # Для сериализации данных
import bcrypt  # Для хеширования паролей

app = Flask(__name__)

DATABASE = 'logins.db'  # Путь к базе данных logins.db
STUDENTS_DBS_DIR = 'students_dbs'  # Папка для баз данных студентов
ADMINS_DBS_DIR = 'admins_dbs'  # Папка для баз данных администраторов
TEACHERS_DBS_DIR = 'teachers_dbs'  # Папка для баз данных учителей
CLASSES_FILE = 'classes.txt'  # Файл для хранения списка классов

# Замените на адрес вашего сервера
SERVER_URL = 'http://your_server_address:5000'

# Вспомогательные функции

def get_db_connection():
    """Устанавливает соединение с базой данных."""
    conn = None
    try:
        conn = sq.connect(DATABASE)
        conn.row_factory = sq.Row  # Возвращает строки в виде словарей
        return conn
    except sq.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        if conn:
            conn.close()
        raise  # Повторно вызывает исключение для обработки на уровне выше

def execute_query(query, args=()):
    """Выполняет запрос к базе данных."""
    conn = get_db_connection()
    cur = None
    try:
        cur = conn.cursor()
        cur.execute(query, args)
        conn.commit()
        if cur.description:  # Проверяет, является ли запрос SELECT
            return [dict(zip([col[0] for col in cur.description], row)) for row in cur.fetchall()]
        return None
    except sq.Error as e:
        print(f"Ошибка базы данных: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def update_db_version(db_path):
    """Обновляет версию базы данных."""
    conn = None
    cur = None
    try:
        conn = sq.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='version';")
        if cur.fetchone() is None:
            cur.execute("CREATE TABLE version (Date TEXT, Version INTEGER);")
            cur.execute("INSERT INTO version (Date, Version) VALUES (?, ?);", (datetime.now(), 1))
            conn.commit()
            conn.close()
            return
        query = "SELECT Date, Version FROM version;"
        cur.execute(query)
        rows = cur.fetchone()
        if rows:
            date_val, version_val = rows
            if version_val is None:
                ver = 1
            else:
                ver = int(version_val) + 1
        else:
            cur.execute("INSERT INTO version (Date, Version) VALUES (?, ?);", (datetime.now(), ver))
        query = "UPDATE version SET Date = ?, Version = ?;"
        cur.execute(query, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ver))
        conn.commit()
        conn.close()
    except sq.Error as e:
        print(f"Ошибка базы данных: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def create_admin_db(login):
    """Создает базу данных для администратора."""
    conn = None
    cur = None
    try:
        os.makedirs("admins_dbs", exist_ok=True)
        db_path = f"admins_dbs/{login}.db"
        conn = sq.connect(db_path)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS adm (id INTEGER PRIMARY KEY)")  # Простая таблица
        conn.commit()
        print(f"База данных для администратора {login} успешно создана.")
    except sq.Error as e:
        print(f"Ошибка при создании базы данных администратора: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def create_teacher_db(login, classes):
    """Создает базу данных для учителя."""
    conn = None
    cur = None
    try:
        os.makedirs("teachers_dbs", exist_ok=True)
        db_path = f"teachers_dbs/{login}.db"
        conn = sq.connect(db_path)
        cur = conn.cursor()

        # Таблица с классами
        cur.execute("CREATE TABLE IF NOT EXISTS classes (class_name TEXT PRIMARY KEY)")
        for class_name in classes:
            cur.execute("INSERT INTO classes (class_name) VALUES (?)", (class_name,))

        conn.commit()
        print(f"База данных для учителя {login} успешно создана.")
    except sq.Error as e:
        print(f"Ошибка при создании базы данных учителя: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def add_data_bases(classes_list):
    """Создает базы данных и таблицы для классов."""
    conn = None
    cur = None
    try:
        os.makedirs(STUDENTS_DBS_DIR, exist_ok=True)
        print("Создана главная папка")
    except FileExistsError:
        print("Главная папка уже существует")

    for item in classes_list:
        class_dir = f"students_dbs/{item}"
        try:
            os.mkdir(class_dir)
            print(f"Создана папка для {item}")
        except FileExistsError:
            print(f"Папка для {item} уже существует")

        timetable_db = f"{class_dir}/time_table.db"

        try:
            conn = sq.connect(timetable_db)
            cur = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS time_table(
                id INTEGER PRIMARY KEY,
                Monday TEXT,
                Tuesday TEXT,
                Wednesday TEXT,
                Thursday TEXT,
                Friday TEXT,
                Saturday TEXT,
                Sunday TEXT);
                """)

            for i in range(15):
                cur.execute("INSERT INTO time_table (Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (None, None, None, None, None, None, None))
            conn.commit()
            conn.close()
            print(f"Создано расписание для {item}")

        except sq.Error as e:
            print(f"Ошибка базы данных: {e}")
            raise

        class_list_db = f"{class_dir}/class_list.db"

        try:
            conn = sq.connect(class_list_db)
            cur = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS class_list(
                Name TEXT,
                Surname TEXT,
                Patronymic TEXT,
                Login TEXT);
                """)
            conn.commit()
            conn.close()
            print(f"Создан список класса {item}")

        except sq.Error as e:
            print(f"Ошибка базы данных: {e}")
            raise

        home_work_db = f"{class_dir}/home_works.db"

        try:
            conn = sq.connect(home_work_db)
            cur = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS home_work(Date TEXT);""")
            start_date = date(date.today().year, 1, 1)
            end_date = date(date.today().year, 12, 31)
            val2 = ""
            current_date = start_date
            while current_date <= end_date:
                val2 = current_date.strftime("%Y-%m-%d")
                current_date += timedelta(days=1)
                cur.execute("""INSERT INTO home_work (Date) VALUES (?)""", (val2,))
            conn.commit()
            conn.close()

        except sq.Error as e:
            print(f"Ошибка базы данных: {e}")
            raise

def load_classes():
    """Загружает список классов из файла."""
    try:
        with open(CLASSES_FILE, 'r') as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []

def save_classes(classes):
    """Сохраняет список классов в файл."""
    try:
        with open(CLASSES_FILE, 'w') as f:
            for cls in classes:
                f.write(f"{cls}\n")
    except Exception as e:
        print(f"Ошибка при сохранении классов в файл: {e}")

existing_classes = load_classes()

@app.route('/classes', methods=['GET'])
def get_classes():
    """Возвращает список существующих классов."""
    return jsonify(existing_classes)

@app.route('/add_class', methods=['POST'])
def add_class_route():
    """Добавляет новый класс и создает связанные базы данных."""
    data = request.json
    if not data or 'class_name' not in data:
        return jsonify({"message": "Отсутствует название класса"}), 400

    class_name = data['class_name']
    if class_name in existing_classes:
        return jsonify({"message": f"Класс {class_name} уже существует."}), 409

    try:
        add_data_bases([class_name])
        existing_classes.append(class_name)
        save_classes(existing_classes)
        return jsonify({"message": f"Класс {class_name} успешно добавлен."}), 201
    except Exception as e:
        print(f"Ошибка при добавлении класса: {e}")
        return jsonify({"message": f"Не удалось добавить класс {class_name}: {str(e)}"}), 500

@app.route('/time_table_add', methods=['POST'])
def time_table_add_route():
    """Добавляет запись в расписание в базу данных."""
    data = request.json
    if not data or not all(k in data for k in ('class_name', 'day', 'lesson_number', 'lesson_name')):
        return jsonify({"message": "Отсутствуют обязательные поля"}), 400

    try:
        class_name = data['class_name']
        day = data['day']
        lesson_number = data['lesson_number']
        lesson_name = data['lesson_name']

        # Формируем путь к базе данных
        timetable_db = os.path.join(STUDENTS_DBS_DIR, class_name, 'time_table.db')

        if not os.path.exists(timetable_db):
            return jsonify({"message": f"База данных расписания для класса {class_name} не существует."}), 404

        # Подключаемся к базе данных
        conn = sq.connect(timetable_db)
        cur = conn.cursor()

        try:
            # Проверяем номер урока
            if not isinstance(lesson_number, int) or lesson_number < 1 or lesson_number > 15:
                return jsonify({"message": "Некорректный номер урока. Должен быть от 1 до 15."}), 400

            # Обновляем запрос
            update_query = f"UPDATE time_table SET {day} = ? WHERE id = ?;"
            cur.execute(update_query, (lesson_name, lesson_number))

            if cur.rowcount == 0:
                conn.rollback()
                return jsonify({"message": "Нет обновленных строк. Номер урока может быть некорректным."}), 400

            conn.commit()

            # Функция для обновления списка уроков
            lesson_list_file = os.path.join(STUDENTS_DBS_DIR, class_name, 'lesson_list.txt')
            with open(lesson_list_file, 'r+', encoding='utf-8') as f:
                lessons = [line.strip() for line in f]
                if lesson_name not in lessons:
                    f.write(lesson_name + '\n')

            # Успешный ответ
            return jsonify({"message": "Запись в расписание успешно добавлена."}), 200

        except sq.Error as e:
            print(f"Ошибка базы данных: {e}")
            conn.rollback()
            return jsonify({"message": f"Ошибка базы данных: {e}"}), 500

        finally:
            cur.close()
            conn.close()

    except Exception as e:
        print(f"Общая ошибка: {e}")
        return jsonify({"message": f"Общая ошибка сервера: {e}"}), 500

def hash_password(password):
    """Хеширует пароль с использованием bcrypt."""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def check_password(password, hashed_password):
    """Проверяет, соответствует ли пароль хешу."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

@app.route('/add_user', methods=['POST'])
def add_user_route():
    """Добавляет нового пользователя в базу данных."""
    conn = None
    cur = None

    data = request.json
    if not data:
        return jsonify({"message": "Данные не предоставлены"}), 400

    try:
        role = data.get('role')
        login = data.get('login')
        password = data.get('password')

        if not all([role, login, password]):
            return jsonify({"message": "Отсутствуют обязательные поля"}), 400

        info = ""
        if role == "admin":
            admin_name = data.get('admin_name')
            if not admin_name:
                return jsonify({"message": "Требуется имя администратора"}), 400
            info = admin_name
            create_admin_db(login)

        elif role == "teacher":
            teacher_surname = data.get('teacher_surname')
            teacher_name = data.get('teacher_name')
            teacher_patronymic = data.get('teacher_patronymic')
            classes = data.get('classes')

            if not all([teacher_surname, teacher_name, teacher_patronymic, classes]):
                return jsonify({"message": "Отсутствуют данные учителя"}), 400

            info = f"{teacher_surname},{teacher_name},{teacher_patronymic}"
            create_teacher_db(login, classes)

        elif role == "student":
            class_name = data.get('class_name')
            student_name = data.get('student_name')
            student_surname = data.get('student_surname')
            student_patronymic = data.get('student_patronymic')
            if not all([class_name, student_name, student_surname, student_patronymic]):
                return jsonify({"message": "Отсутствуют данные студента"}), 400
            info = class_name

            # ------------------------ Операции с базой данных для студентов ------------------------
            conn = None # Инициализируем conn
            cur = None  # Инициализируем cur
            conn2 = None # Инициализируем conn2
            cur2 = None  # Инициализируем cur2
            conn3 = None # Инициализируем conn3
            cur3 = None  # Инициализируем cur3
            try:
                conn = get_db_connection() # Используем функцию для получения соединения
                cur = conn.cursor()

                lesson_list_file = os.path.join(STUDENTS_DBS_DIR, class_name, 'lesson_list.txt')
                try: #Оборачиваем в try except чтение файла.
                    with open(lesson_list_file, "r", encoding="utf-8") as f:
                        lessons_list = [line.strip() for line in f.readlines()]
                except FileNotFoundError as e:
                    return jsonify({"message": f"Файл не найден: {e}"}), 500
                except Exception as e: # Добавляем обработку других возможных ошибок чтения файла
                     return jsonify({"message": f"Ошибка при чтении файла: {e}"}), 500


                val = "?, "
                strs = "Дата TEXT, \n"
                strs2 = "Дата, "
                val2 = ["01.01"]
                for item in lessons_list:
                    strs += f"{item} TEXT,\n"
                    strs2 += f"{item}, "
                    val += "?, "
                    val2.append(None)

                strs = strs[:-2]
                strs2 = strs2[:-2]
                val = val[:-2]
                ins = f"""INSERT INTO marks ({strs2}) VALUES ({val})"""
                e = f"""CREATE TABLE IF NOT EXISTS marks({strs});"""

                student_db_path = os.path.join(STUDENTS_DBS_DIR, class_name, f"{login}.db")

                try: # Оборачиваем работу с базой в try except
                    conn2 = sq.connect(student_db_path)
                    cur2 = conn2.cursor()
                    cur2.execute(e)
                    conn2.commit()

                    start_date = date(date.today().year, 1, 1)
                    end_date = date(date.today().year, 12, 31)

                    current_date = start_date
                    while current_date <= end_date:
                        val2[0] = current_date.strftime("%Y-%m-%d")
                        current_date += timedelta(days=1)
                        cur2.execute(ins, tuple(val2))  # Передаем val2 как кортеж

                    conn2.commit()

                except sq.Error as e:
                    print(f"Ошибка базы данных: {e}")
                    return jsonify({"message": "Ошибка базы данных при настройке студента"}), 500
                except Exception as e:
                    return jsonify({"message": f"Ошибка при работе с базой данных ученика: {e}"}), 500

                try: # оборачиваем создание записи о студенте в try except
                    class_list_db_path = os.path.join(STUDENTS_DBS_DIR, class_name, "class_list.db")
                    conn3 = sq.connect(class_list_db_path)
                    cur3 = conn3.cursor()
                    cur3.execute(f"""INSERT INTO class_list(Name, Surname, Patronymic, Login) VALUES (?, ?, ?, ?)""",
                                 (student_name, student_surname, student_patronymic, login))
                    conn3.commit()

                except sq.Error as e:
                    print(f"Ошибка базы данных: {e}")
                    return jsonify({"message": "Ошибка при добавлении студента в список класса"}), 500
                except Exception as e:
                    return jsonify({"message": f"Ошибка при добавлении ученика в список класса: {e}"}), 500


            except FileNotFoundError as e:
                return jsonify({"message": f"Файл не найден: {e}"}), 500
            except sq.Error as e:
                print(f"Ошибка базы данных: {e}")
                return jsonify({"message": "Ошибка базы данных при настройке студента"}), 500
            except Exception as e:
                print(f"Неожиданная ошибка: {e}")
                return jsonify({"message": "Неожиданная ошибка при настройке студента"}), 500
    finally:
        if cur2:  # Проверяем, что cur2 существует
                cur2.close()
        if conn2: # Проверяем, что conn2 существует
                conn2.close()
        if cur3:  # Проверяем, что cur3 существует
                cur3.close()
        if conn3: # Проверяем, что conn3 существует
                conn3.close()
        if cur:  # Проверяем, что cur существует
                cur.close()
        if conn: # Проверяем, что conn существует
                conn.close()


@app.route('/process', methods=['POST'])
def process():
    """Обрабатывает вход пользователя и возвращает соответствующие файлы."""
    data = request.json.get('message')
    if not data or len(data) != 2:
        return jsonify({"message": "Некорректный ввод"}), 400

    print(f"Получено от клиента: {data}")

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Проверяем наличие пользователя в базе данных
        cur.execute("SELECT password FROM users WHERE login = ?", (data[0],))
        user = cur.fetchone()

        if user:
           # Верифицируем пароль
           hashed_password = user[0]
           if check_password(data[1], hashed_password):
            # Получаем роль и информацию о пользователе
            cur.execute("SELECT role, info FROM users WHERE login = ?", (data[0],))
            inf = cur.fetchone()
            role, goto = inf

            # Определяем путь к базе данных в зависимости от роли
            if role == "student":
                way = "students_dbs"
                file_paths = [
                    f"{way}/{goto}/{data[0]}.db",
                    f"{way}/{goto}/home_works.db",
                    f"{way}/{goto}/time_table.db"
                ]
            elif role == "teacher":
                way = "teachers_dbs"
                file_paths = [
                    f"{way}/{data[0]}.db",
                ]

            elif role == "admin":
                way = "admins_dbs"
                file_paths = [
                    f"{way}/{data[0]}.db",
                ]
            else:
                return jsonify({"message": "Неизвестная роль"}), 400

            # Проверяем, существуют ли файлы
            existing_files = [fp for fp in file_paths if os.path.exists(fp)]
            if not existing_files:
                return jsonify({"message": "Файлы не найдены"}), 404

            # Создаём архив в памяти
            memory_file = BytesIO()
            with zipfile.ZipFile(memory_file, 'w') as zipf:
                for file in existing_files:
                    zipf.write(file, os.path.basename(file))

            # Перемещаем указатель в начало файла
            memory_file.seek(0)

            # Отправляем архив клиенту
            return send_file(
                memory_file,
                as_attachment=True,
                download_name=f"{data[0]}_files.zip",
                mimetype="application/zip"
            )
           else:
               return jsonify({"message": "Неверный логин или пароль"}), 401
        else:
            return jsonify({"message": "Неверный логин или пароль"}), 401

    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"message": "Внутренняя ошибка сервера"}), 500

    finally:
        # Закрываем соединение с базой данных
        if cur:
            cur.close()
        if conn:
            conn.close()

# Функция для загрузки классов из файла
def load_classes():
    try:
        with open(CLASSES_FILE, 'r') as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []

# Функция для сохранения классов в файл
def save_classes(classes):
    try:
        with open(CLASSES_FILE, 'w') as f:
            for cls in classes:
                f.write(f"{cls}\n")
    except Exception as e:
        print(f"Ошибка при сохранении классов в файл: {e}")

# Загружаем существующие классы при запуске приложения
if not os.path.exists(CLASSES_FILE):
    with open(CLASSES_FILE, 'w') as f:
        f.write("")  # Создаем пустой файл
    existing_classes = []
else:
    existing_classes = load_classes()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Измененный маршрут для обработки обновления файлов
@app.route('/update_file', methods=['POST'])
def update_file():
    """Получает данные файла и путь для обновления файла на сервере."""
    try:
        data = request.json
        if not data or not all(k in data for k in ('file_path', 'file_content')):
            return jsonify({"message": "Отсутствует file_path или file_content"}), 400

        file_path = data['file_path']
        file_content = data['file_content']

        # Формируем абсолютный путь к файлу
        absolute_file_path = os.path.join(os.getcwd(), file_path)

        # Записываем полученное содержимое в файл
        with open(absolute_file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)

        return jsonify({"message": f"Файл {file_path} успешно обновлен."}), 200

    except Exception as e:
        print(f"Ошибка при обновлении файла: {e}")
        return jsonify({"message": f"Не удалось обновить файл: {str(e)}"}), 500

# Функция на стороне клиента (в вашем PyQt приложении) для отправки данных на сервер
def send_data_to_server(file_path, file_content):
    """Отправляет содержимое файла на сервер для обновления файла."""
    url = f'{SERVER_URL}/update_file'
    headers = {'Content-Type': 'application/json'}
    data = {'file_path': file_path, 'file_content': file_content}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Вызывает HTTPError для плохих ответов (4xx или 5xx)
        print(f"Ответ сервера: {response.json()}")  # Печатает сообщение ответа
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None

if __name__ == '__main__':
    # Создаем необходимые директории, если они не существуют
    os.makedirs(STUDENTS_DBS_DIR, exist_ok=True)
    os.makedirs(ADMINS_DBS_DIR, exist_ok=True)
    os.makedirs(TEACHERS_DBS_DIR, exist_ok=True)

    # Создаем базу данных logins.db, если она не существует, и добавляем таблицу users
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            login TEXT UNIQUE,
            password TEXT,
            role TEXT,
            info TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

    # Загружаем существующие классы
    if not os.path.exists(CLASSES_FILE):
        with open(CLASSES_FILE, 'w') as f:
            f.write("")  # Создаем пустой файл
        existing_classes = []
    else:
        existing_classes = load_classes()
    app.run(debug=True)