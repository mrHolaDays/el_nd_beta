import sys
import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QFrame,
    QSizePolicy, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtCore import Qt
import sqlite3
import os

class StudentInterface(QWidget):
    """
    Класс интерфейса студента, отображающий расписание, домашнее задание и оценки.
    """
    def __init__(self, login, class_name):
        """
        Инициализация интерфейса студента.

        Args:
            login (str): Логин студента.
            class_name (str): Название класса студента.
        """
        super().__init__()
        self.login = login  # Логин студента (используется для доступа к базе данных с оценками)
        self.class_name = class_name  # Название класса (не используется в текущей реализации, но может быть полезно)
        self.current_date = datetime.date.today()  # Текущая дата, используемая для отображения расписания и ДЗ
        self.initUI()  # Инициализация пользовательского интерфейса
        self.update_date_display()  # Обновление отображения даты
        self.update_schedule_homework()  # Объединенное обновление расписания и домашнего задания (вызывается сразу)

    def initUI(self):
        """
        Инициализация пользовательского интерфейса.
        """
        # Настройка окна
        self.setWindowTitle('Дневник')  # Устанавливаем заголовок окна
        self.setGeometry(100, 100, 1000, 700)  # Устанавливаем размеры окна (увеличено)
        self.setStyleSheet("background-color: #222222;")  # Устанавливаем темный фон

        # Основной макет (вертикальный)
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)  # Выравниваем элементы по верху

        # Макет для заголовка и иконки
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)  # Выравнивание по центру по вертикали и слева по горизонтали

        # Заголовок "Дневник"
        title_label = QLabel('Дневник', self)
        title_label.setFont(QFont("Arial", 24, QFont.Bold))  # Шрифт заголовка
        title_label.setStyleSheet("color: #FFFFFF; margin-left: 20px;")  # Стиль заголовка
        header_layout.addWidget(title_label)  # Добавляем заголовок в макет

        header_layout.addStretch(1)  # Добавляем растяжку для смещения иконки вправо

        # Иконка флага (например, России)
        flag_icon = QLabel()
        flag_icon.setPixmap(QIcon("russia_flag_icon.png").pixmap(35, 35))  # Загружаем иконку, настраиваем путь и размер
        header_layout.addWidget(flag_icon)  # Добавляем иконку в макет
        header_layout.setContentsMargins(0, 0, 20, 0) # add margin to the right # Добавляем отступ справа

        main_layout.addLayout(header_layout)  # Добавляем макет заголовка в основной макет

        # Макет для отображения даты
        date_layout = QHBoxLayout()
        date_layout.setAlignment(Qt.AlignCenter)  # Выравниваем элементы по центру
        date_layout.setSpacing(0) # remove spacing between date labels  # Убираем отступы между элементами

        # Кнопка "Предыдущий день"
        self.prev_day_button = QPushButton("<", self)
        self.prev_day_button.setFont(QFont("Arial", 12, QFont.Bold))  # Шрифт кнопки
        self.prev_day_button.setStyleSheet("""
            QPushButton {
                background-color: #444444;  /* Темно-серый фон */
                color: white;  /* Белый текст */
                padding: 5px 10px;
                border-radius: 5px;  /* Закругленные углы */
                border: none; /* Убираем рамку */
            }
            QPushButton:hover {
                background-color: #555555;  /* Более светлый фон при наведении */
            }
        """)
        self.prev_day_button.setCursor(Qt.PointingHandCursor)  # Курсор в виде руки при наведении
        self.prev_day_button.clicked.connect(self.previous_day)  # Подключаем обработчик нажатия
        date_layout.addWidget(self.prev_day_button)  # Добавляем кнопку в макет

        # Отображение дня недели (например, "понедельник")
        self.day_label = QLabel("", self)
        self.day_label.setFont(QFont("Arial", 12, QFont.Bold))  # Шрифт
        self.day_label.setStyleSheet("color: #FFFFFF; background-color: #663399; padding: 3px 10px; border-radius: 5px;")  # Стиль (белый текст, фиолетовый фон)
        date_layout.addWidget(self.day_label)  # Добавляем в макет

        # Отображение числа месяца (например, "20")
        self.day_number_label = QLabel("", self)
        self.day_number_label.setFont(QFont("Arial", 24, QFont.Bold))  # Шрифт
        self.day_number_label.setStyleSheet("color: #FFFFFF; padding: 0 10px; border-radius: 5px;")  # Стиль
        date_layout.addWidget(self.day_number_label)  # Добавляем в макет

        # Отображение года (например, "2024г.")
        self.year_label = QLabel("z", self)
        self.year_label.setFont(QFont("Arial", 12, QFont.Bold))  # Шрифт
        self.year_label.setStyleSheet("color: #FFFFFF; padding: 3px 10px; border-radius: 5px;")  # Стиль
        date_layout.addWidget(self.year_label)  # Добавляем в макет

        # Кнопка "Следующий день"
        self.next_day_button = QPushButton(">", self)
        self.next_day_button.setFont(QFont("Arial", 12, QFont.Bold))  # Шрифт
        self.next_day_button.setStyleSheet("""
            QPushButton {
                background-color: #444444;  /* Темно-серый фон */
                color: white;  /* Белый текст */
                padding: 5px 10px;
                border-radius: 5px;  /* Закругленные углы */
                border: none; /* Убираем рамку */
            }
            QPushButton:hover {
                background-color: #555555;  /* Более светлый фон при наведении */
            }
        """)
        self.next_day_button.setCursor(Qt.PointingHandCursor)  # Курсор в виде руки при наведении
        self.next_day_button.clicked.connect(self.next_day)  # Подключаем обработчик нажатия
        date_layout.addWidget(self.next_day_button)  # Добавляем в макет

        # Отображение месяца (например, "Март")
        self.month_label = QLabel("", self)
        self.month_label.setFont(QFont("Arial", 10))  # Шрифт
        self.month_label.setStyleSheet("color: #FFFFFF; margin-top: 5px; margin-bottom: 20px;")  # Стиль
        month_layout = QVBoxLayout()
        month_layout.setAlignment(Qt.AlignHCenter)  # Выравнивание по центру
        month_layout.addLayout(date_layout)  # Добавляем макет с кнопками и днями в макет месяца
        month_layout.addWidget(self.month_label)  # Добавляем отображение месяца в макет
        main_layout.addLayout(month_layout)  # Добавляем макет месяца в основной макет

        # Вкладки (Tabs)
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabWidget::pane { border: none; }")  # Убираем рамку вокруг вкладок

        # Вкладка "Расписание и ДЗ"
        self.schedule_homework_tab = QWidget()
        self.schedule_homework_layout = QVBoxLayout(self.schedule_homework_tab)  # Layout for the combined tab

        # Таблица для расписания и ДЗ
        self.schedule_homework_table = QTableWidget()
        self.schedule_homework_table.setStyleSheet("""
            QTableWidget {
                background-color: #333333;  /* Темно-серый фон */
                color: #FFFFFF;  /* Белый текст */
                border: none; /* Убираем рамку */
                font-size: 14px; /* Увеличиваем размер шрифта */
            }
            QHeaderView::section {
                background-color: #444444;  /* Темно-серый фон заголовков */
                color: white;  /* Белый текст заголовков */
                border: none; /* Убираем рамку */
                padding: 5px;
                font-size: 14px; /* Увеличиваем размер шрифта */
            }
        """)
        self.schedule_homework_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Автоматическое изменение размера столбцов
        self.schedule_homework_table.verticalHeader().setVisible(False)  # Скрываем номера строк
        self.schedule_homework_layout.addWidget(self.schedule_homework_table)  # Добавляем таблицу во вкладку
        self.tab_widget.addTab(self.schedule_homework_tab, "Расписание и ДЗ")  # Добавляем вкладку в QTabWidget

        # Вкладка "Оценки"
        self.grades_tab = QWidget()
        self.grades_layout = QVBoxLayout(self.grades_tab)
        self.update_grades()  # Обновляем отображение оценок
        self.tab_widget.addTab(self.grades_tab, "Оценки")  # Добавляем вкладку "Оценки"

        main_layout.addWidget(self.tab_widget)  # Добавляем вкладки в основной макет

        self.setLayout(main_layout)  # Устанавливаем основной макет для окна

    def update_date_display(self):
        """
        Обновляет отображение текущей даты (день недели, число, месяц, год).
        """
        days_week = {
            "Monday": "понедельник",
            "Tuesday": "вторник",
            "Wednesday": "среда",
            "Thursday": "четверг",
            "Friday": "пятница",
            "Saturday": "суббота",
            "Sunday": "воскресенье"
        }

        weekday_name = self.current_date.strftime("%A")  # Получаем название дня недели (на английском)
        self.day_label.setText(days_week[weekday_name])  # Устанавливаем название дня недели на русском
        self.day_number_label.setText(str(self.current_date.day))  # Устанавливаем число месяца
        self.year_label.setText(f"{self.current_date.year}г.")  # Устанавливаем год
        self.month_label.setText(self.current_date.strftime("%B"))  # Устанавливаем название месяца

    def previous_day(self):
        """
        Обработчик нажатия на кнопку "Предыдущий день".
        Уменьшает текущую дату на один день и обновляет интерфейс.
        """
        self.current_date -= datetime.timedelta(days=1)  # Вычитаем один день
        self.update_date_display()  # Обновляем отображение даты
        self.update_schedule_homework()  # Обновляем расписание и ДЗ

    def next_day(self):
        """
        Обработчик нажатия на кнопку "Следующий день".
        Увеличивает текущую дату на один день и обновляет интерфейс.
        """
        self.current_date += datetime.timedelta(days=1)  # Прибавляем один день
        self.update_date_display()  # Обновляем отображение даты
        self.update_schedule_homework()  # Обновляем расписание и ДЗ

    def update_schedule_homework(self):
        """
        Обновляет таблицу расписания и домашнего задания на основе текущей даты.
        Сочетает расписание и домашнее задание в одной таблице.
        Также получает и отображает оценки.
        """
        # Получаем расписание
        days_week =['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        to_day =self.current_date.weekday() # Получаем номер дня недели (0 - понедельник, 6 - воскресенье)
        way = f"dbs/time_table.db" # Путь к базе данных с расписанием
        con = sqlite3.connect(way) # Подключаемся к базе данных
        cur = con.cursor() # Создаем курсор для выполнения запросов
        cur.execute(f"SELECT {days_week[to_day]} FROM time_table") # Выполняем запрос для получения расписания на текущий день
        schedule_rows = cur.fetchall() # Получаем все строки расписания
        schedule = [row[0] for row in schedule_rows] # Извлекаем названия предметов из строк
        schedule = [lesson if lesson else "" for lesson in schedule] # Заменяем None на пустую строку (для пустых ячеек)
        con.close() # Закрываем подключение к базе данных

        # Получаем домашнее задание
        date_str = self.current_date.strftime("%Y-%m-%d") # Форматируем дату в строку для запроса
        way = f"dbs/home_works.db" # Путь к базе данных с домашними заданиями
        con = sqlite3.connect(way) # Подключаемся к базе данных
        cur = con.cursor() # Создаем курсор
        cur.execute(f"SELECT * FROM home_work WHERE Date = ?", (date_str,)) # Выполняем запрос для получения домашнего задания на текущую дату
        homework_data = cur.fetchone() # Получаем результат запроса (одна строка)
        con.close() # Закрываем подключение к базе данных

        # Подготавливаем словарь с домашним заданием
        homework = {}
        if homework_data:
            column_names = [description[0] for description in cur.description] # Получаем названия столбцов
            for i in range(1, len(homework_data)): # Начинаем с индекса 1, так как первый столбец - ID
                lesson_name = column_names[i] # Название предмета
                homework[lesson_name] = homework_data[i] if homework_data[i] else "" # Сохраняем домашнее задание в словарь (или пустую строку, если None)

        # Получаем оценки
        grades = self.get_grades_for_date(date_str) # Получаем оценки для текущей даты

        # Объединяем расписание и домашнее задание
        num_rows = len(schedule) # Количество уроков в расписании
        self.schedule_homework_table.setRowCount(num_rows) # Устанавливаем количество строк в таблице
        self.schedule_homework_table.setColumnCount(4)  # Добавляем столбец для оценок
        self.schedule_homework_table.setHorizontalHeaderLabels(["№", "Предмет", "Домашнее задание", "Оценка"]) # Устанавливаем заголовки столбцов
        self.schedule_homework_table.setColumnWidth(0, 50)  # Устанавливаем ширину столбца с номером урока

        for row in range(num_rows): # Перебираем строки (уроки)
            lesson_name = schedule[row] # Название предмета (из расписания)

            # Номер урока
            lesson_number_item = QTableWidgetItem(str(row + 1)) # Создаем элемент таблицы с номером урока
            lesson_number_item.setTextAlignment(Qt.AlignCenter) # Выравниваем текст по центру
            lesson_number_item.setFlags(lesson_number_item.flags() & ~Qt.ItemIsEditable)  # Делаем ячейку нередактируемой
            self.schedule_homework_table.setItem(row, 0, lesson_number_item) # Устанавливаем элемент в таблицу

            # Предмет
            lesson_item = QTableWidgetItem(lesson_name) # Создаем элемент таблицы с названием предмета
            lesson_item.setTextAlignment(Qt.AlignCenter) # Выравниваем текст по центру
            lesson_item.setFlags(lesson_item.flags() & ~Qt.ItemIsEditable)  # Делаем ячейку нередактируемой
            self.schedule_homework_table.setItem(row, 1, lesson_item) # Устанавливаем элемент в таблицу

            # Домашнее задание
            homework_text = homework.get(lesson_name, "") # Получаем домашнее задание (из словаря homework)
            homework_item = QTableWidgetItem(homework_text) # Создаем элемент таблицы с домашним заданием
            homework_item.setTextAlignment(Qt.AlignCenter) # Выравниваем текст по центру
            homework_item.setFlags(homework_item.flags() & ~Qt.ItemIsEditable)  # Делаем ячейку нередактируемой
            self.schedule_homework_table.setItem(row, 2, homework_item) # Устанавливаем элемент в таблицу

            # Оценка
            grade = grades.get(lesson_name, "")  # Получаем оценку (из словаря grades)
            grade_item = QTableWidgetItem(str(grade)) # Создаем элемент таблицы с оценкой
            grade_item.setTextAlignment(Qt.AlignCenter) # Выравниваем текст по центру
            grade_item.setFlags(grade_item.flags() & ~Qt.ItemIsEditable) # Делаем ячейку нередактируемой
            self.schedule_homework_table.setItem(row, 3, grade_item) # Устанавливаем элемент в таблицу

            # Раскраска строк в зависимости от наличия предмета
            if lesson_name: # Если есть название предмета (урок существует)
                for col in range(4): # Перебираем все столбцы
                    self.schedule_homework_table.item(row, col).setBackground(QColor("#333333")) # Устанавливаем фон для ячейки (темно-серый)
            else: # Если урока нет (пустая строка расписания)
                for col in range(4): # Перебираем все столбцы
                    self.schedule_homework_table.item(row, col).setBackground(QColor("#555555")) # Устанавливаем фон для ячейки (более светлый серый)

        self.schedule_homework_table.resizeColumnsToContents() # Подгоняем размер столбцов по содержимому

    def get_grades_for_date(self, date_str):
        """
        Получает оценки для указанной даты из базы данных студента.

        Args:
            date_str (str): Дата в формате "YYYY-MM-DD".

        Returns:
            dict: Словарь с оценками, где ключ - название предмета, значение - оценка.
        """
        grades = {}  # Создаем пустой словарь для хранения оценок
        way = f"dbs/{self.login}.db"  # Формируем путь к базе данных студента
        try:
            con = sqlite3.connect(way)  # Подключаемся к базе данных
            cur = con.cursor()  # Создаем курсор для выполнения запросов

            # Получаем все названия столбцов, кроме "Дата" (т.е. названия предметов)
            cur.execute("PRAGMA table_info(marks)")  # Выполняем запрос для получения информации о таблице marks
            columns_info = cur.fetchall()  # Получаем результаты запроса (информация о столбцах)
            lesson_names = [col[1] for col in columns_info if col[1] != "Дата"]  # Извлекаем названия предметов

            # Формируем SQL-запрос для получения оценок
            select_columns = ", ".join(lesson_names)  # Составляем строку с названиями столбцов для запроса
            query = f"SELECT {select_columns} FROM marks WHERE Дата = ?"  # Формируем SQL-запрос

            # Выполняем запрос
            cur.execute(query, (date_str,))  # Выполняем запрос с указанной датой
            grade_data = cur.fetchone()  # Получаем результаты запроса (одна строка с оценками)

            if grade_data: # Если были найдены оценки
                # Заполняем словарь с оценками
                for i, lesson_name in enumerate(lesson_names): # Перебираем названия предметов
                    grades[lesson_name] = grade_data[i] if grade_data[i] is not None else ""  # Сохраняем оценку в словарь (или пустую строку, если оценка None)
        except sqlite3.Error as e: # Обрабатываем ошибки при работе с базой данных
            print(f"Database error: {e}")  # Выводим сообщение об ошибке
        finally:
            if con: # Гарантируем, что подключение к базе данных будет закрыто
                con.close()  # Закрываем подключение
        return grades  # Возвращаем словарь с оценками

    def update_grades(self):
        """
        Обновляет отображение оценок во вкладке "Оценки".
        """
        # Очищаем старый макет оценок
        for i in reversed(range(self.grades_layout.count())):
            widget = self.grades_layout.itemAt(i).widget()  # Получаем виджет
            if widget is not None:
                widget.deleteLater()  # Удаляем виджет

        # Подключаемся к базе данных оценок студента
        way = f"dbs/{self.login}.db" # Формируем путь к базе данных
        con = sqlite3.connect(way)  # Подключаемся к базе данных
        cur = con.cursor()  # Создаем курсор

        # Получаем все данные об оценках
        cur.execute("SELECT * FROM marks")  # Выполняем запрос для получения всех оценок
        grades_data = cur.fetchall() # Получаем все данные об оценках
        # Получаем названия столбцов (даты и названия предметов)
        cur.execute("PRAGMA table_info(marks)") # Получаем информацию о столбцах таблицы
        columns_info = cur.fetchall()  # Получаем информацию о столбцах
        column_names = [col[1] for col in columns_info] # Получаем названия столбцов

        con.close()  # Закрываем подключение к базе данных

        # Создаем таблицу для отображения оценок
        grades_table = QTableWidget() # Создаем виджет таблицы
        grades_table.setColumnCount(len(column_names))  # Устанавливаем количество столбцов
        grades_table.setRowCount(len(grades_data))  # Устанавливаем количество строк
        grades_table.setHorizontalHeaderLabels(column_names)  # Устанавливаем заголовки столбцов

        # Применяем стили к заголовкам таблицы
        header = grades_table.horizontalHeader() # Получаем заголовок таблицы
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #444444;  /* Темно-серый фон */
                color: #FFFFFF;  /* Белый текст */
                border: none; /* Убираем рамку */
                padding: 5px;
                font-size: 14px; /* Увеличиваем размер шрифта */
            }
        """)

        # Применяем стили к самой таблице
        grades_table.setStyleSheet("""
            QTableWidget {
                background-color: #333333;  /* Темно-серый фон */
                color: #FFFFFF;  /* Белый текст */
                border: none; /* Убираем рамку */
                font-size: 14px; /* Увеличиваем размер шрифта */
            }
        """)
        # Заполняем таблицу данными
        for row_index, row_data in enumerate(grades_data): # Перебираем строки с данными об оценках
            for col_index, cell_data in enumerate(row_data):  # Перебираем ячейки в строке
                item = QTableWidgetItem(str(cell_data) if cell_data is not None else "")  # Создаем элемент таблицы
                item.setTextAlignment(Qt.AlignCenter)  # Выравниваем текст по центру
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Делаем ячейки нередактируемыми
                grades_table.setItem(row_index, col_index, item)  # Устанавливаем элемент в таблицу

        # Настройка размера столбцов
        header = grades_table.horizontalHeader() # Получаем заголовок таблицы
        header.setSectionResizeMode(QHeaderView.Stretch)  # Автоматическое изменение размера столбцов

        self.grades_layout.addWidget(grades_table)  # Добавляем таблицу с оценками в макет
        grades_table.resizeColumnsToContents() # Подгоняем размер столбцов по содержимому

if __name__ == '__main__':
    app = QApplication(sys.argv) # Создаем экземпляр приложения
    window = StudentInterface("stud1", "1А") # Создаем экземпляр интерфейса студента (укажите логин и класс)
    window.show() # Отображаем окно
    sys.exit(app.exec_()) # Запускаем цикл обработки событий приложения