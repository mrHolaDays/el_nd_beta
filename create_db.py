import sys
import requests
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QFormLayout, QMessageBox, QComboBox, QTabWidget, QListWidget, QListWidgetItem, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# URL сервера Flask
SERVER_URL = "http://127.0.0.1:5000"  # Измените, если ваш сервер работает на другом адресе

class AddTimetableGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить расписание")
        self.setGeometry(100, 100, 400, 300)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Выбор класса
        self.class_name_combo = QComboBox()
        self.load_classes()  # Загружаем доступные классы с сервера
        form_layout.addRow("Класс:", self.class_name_combo)

        # Выбор дня недели
        self.day_combo = QComboBox()
        self.day_combo.addItems(["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"])
        form_layout.addRow("День недели:", self.day_combo)

        # Ввод номера урока
        self.lesson_number_input = QLineEdit()
        self.lesson_number_input.setPlaceholderText("Номер урока (1-15)")
        form_layout.addRow("Номер урока:", self.lesson_number_input)

        # Ввод названия предмета
        self.lesson_name_input = QLineEdit()
        self.lesson_name_input.setPlaceholderText("Название предмета")
        form_layout.addRow("Название предмета:", self.lesson_name_input)

        # Кнопка для добавления записи в расписание
        self.add_timetable_button = QPushButton("Добавить расписание")
        self.add_timetable_button.clicked.connect(self.add_timetable_entry)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.add_timetable_button)
        self.setLayout(main_layout)

    def load_classes(self):
        """Загружает доступные классы с сервера и заполняет выпадающий список."""
        try:
            response = requests.get(f"{SERVER_URL}/classes")
            response.raise_for_status()  # Проверяем на ошибки HTTP
            classes = response.json()
            self.class_name_combo.addItems(classes)

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к серверу: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке классов: {e}")

    def add_timetable_entry(self):
        """Добавляет запись в расписание, отправляя запрос на сервер Flask."""
        class_name = self.class_name_combo.currentText()
        day = self.day_combo.currentText()
        lesson_number = self.lesson_number_input.text()
        lesson_name = self.lesson_name_input.text()

        # Проверяем ввод
        if not all([class_name, day, lesson_number, lesson_name]):
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        try:
            lesson_number = int(lesson_number)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Номер урока должен быть числом.")
            return

        # Подготавливаем данные для отправки
        timetable_data = {
            "class_name": class_name,
            "day": day,
            "lesson_number": lesson_number,
            "lesson_name": lesson_name
        }

        # Отправляем запрос на сервер
        try:
            response = requests.post(f"{SERVER_URL}/time_table_add", json=timetable_data)
            response.raise_for_status()  # Проверяем на ошибки HTTP
            result = response.json()
            QMessageBox.information(self, "Успех", result.get("message", "Расписание успешно добавлено."))

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к серверу: {e}")
        except requests.exceptions.HTTPError as e:
            error_message = response.json().get("message", "Неизвестная ошибка")
            print(f"Ошибка сервера: {error_message}")
            QMessageBox.warning(self, "Ошибка", f"Ошибка: {error_message}")

class AddClassGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить класс")
        self.setGeometry(100, 100, 400, 200)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Поле для ввода названия класса
        self.class_name_input = QLineEdit()
        form_layout.addRow("Название класса:", self.class_name_input)

        # Кнопка для добавления класса
        self.add_class_button = QPushButton("Добавить класс")
        self.add_class_button.clicked.connect(self.add_class)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.add_class_button)
        self.setLayout(main_layout)

    def add_class(self):
        """Добавляет новый класс, отправляя запрос на сервер Flask."""
        class_name = self.class_name_input.text().strip()

        if not class_name:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите название класса.")
            return

        # Отправляем запрос на сервер Flask
        try:
            response = requests.post(f"{SERVER_URL}/add_class", json={"class_name": class_name})
            response.raise_for_status()
            result = response.json()
            QMessageBox.information(self, "Успех", result.get("message", "Класс успешно добавлен."))
            # После успешного добавления класса обновляем списки классов в других вкладках
            self.parent().add_user_tab.load_classes()
            self.parent().add_timetable_tab.load_classes()

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к серверу: {e}")
        except requests.exceptions.HTTPError as e:
            error_message = response.json().get("message", "Неизвестная ошибка")
            print(f"Ошибка сервера: {error_message}")
            QMessageBox.warning(self, "Ошибка", f"Ошибка: {error_message}")

class MainGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление пользователями и классами")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Вкладки для добавления пользователя, класса и расписания
        self.tabs = QTabWidget()

        # Вкладка "Добавить пользователя"
        self.add_user_tab = AddUserGUI(self)
        self.tabs.addTab(self.add_user_tab, "Добавить пользователя")

        # Вкладка "Добавить класс"
        self.add_class_tab = AddClassGUI()
        self.tabs.addTab(self.add_class_tab, "Добавить класс")

        # Вкладка "Добавить расписание"
        self.add_timetable_tab = AddTimetableGUI()
        self.tabs.addTab(self.add_timetable_tab, "Добавить расписание")

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

class AddUserGUI(QWidget):
    def __init__(self, main_gui):
        super().__init__()
        self.setWindowTitle("Добавить пользователя")
        self.setGeometry(100, 100, 600, 400)
        self.main_gui = main_gui
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Вкладки для разных ролей пользователей
        self.tabs = QTabWidget()

        # Вкладка "Администратор"
        self.admin_tab = QWidget()
        self.admin_layout = QFormLayout(self.admin_tab)
        self.admin_login = QLineEdit()
        self.admin_password = QLineEdit()
        self.admin_name = QLineEdit()
        self.admin_layout.addRow("Логин:", self.admin_login)
        self.admin_layout.addRow("Пароль:", self.admin_password)
        self.admin_layout.addRow("Имя:", self.admin_name)

        # Вкладка "Учитель"
        self.teacher_tab = QWidget()
        self.teacher_layout = QFormLayout(self.teacher_tab)
        self.teacher_login = QLineEdit()
        self.teacher_password = QLineEdit()
        self.teacher_surname = QLineEdit()
        self.teacher_name = QLineEdit()
        self.teacher_patronymic = QLineEdit()
        self.teacher_classes = QListWidget()  # Используем QListWidget для выбора нескольких классов
        self.load_classes_teacher()  # Загружаем классы с сервера

        self.teacher_layout.addRow("Логин:", self.teacher_login)
        self.teacher_layout.addRow("Пароль:", self.teacher_password)
        self.teacher_layout.addRow("Фамилия:", self.teacher_surname)
        self.teacher_layout.addRow("Имя:", self.teacher_name)
        self.teacher_layout.addRow("Отчество:", self.teacher_patronymic)
        self.teacher_layout.addRow("Классы:", self.teacher_classes)

        # Вкладка "Ученик"
        self.student_tab = QWidget()
        self.student_layout = QFormLayout(self.student_tab)
        self.student_login = QLineEdit()
        self.student_password = QLineEdit()
        self.student_class = QComboBox()
        self.student_name = QLineEdit()
        self.student_surname = QLineEdit()
        self.student_patronymic = QLineEdit()
        self.load_classes()  # Загружаем классы для вкладки "Ученик"

        self.student_layout.addRow("Логин:", self.student_login)
        self.student_layout.addRow("Пароль:", self.student_password)
        self.student_layout.addRow("Класс:", self.student_class)
        self.student_layout.addRow("Имя:", self.student_name)
        self.student_layout.addRow("Фамилия:", self.student_surname)
        self.student_layout.addRow("Отчество:", self.student_patronymic)

        self.tabs.addTab(self.admin_tab, "Администратор")
        self.tabs.addTab(self.teacher_tab, "Учитель")
        self.tabs.addTab(self.student_tab, "Ученик")

        main_layout.addWidget(self.tabs)

        # Кнопка для добавления пользователя
        self.add_button = QPushButton("Добавить пользователя")
        self.add_button.clicked.connect(self.add_user)
        main_layout.addWidget(self.add_button)

        self.setLayout(main_layout)

    def load_classes_teacher(self):
        """Загружает доступные классы с сервера для списка классов во вкладке учителя."""
        try:
            response = requests.get(f"{SERVER_URL}/classes")
            response.raise_for_status()
            classes = response.json()
            self.teacher_classes.clear()  # Очищаем предыдущие элементы
            for class_name in classes:
                item = QListWidgetItem(class_name)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # Делаем элемент выбираемым
                item.setCheckState(Qt.Unchecked)  # По умолчанию не выбран
                self.teacher_classes.addItem(item)

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к серверу: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке классов: {e}")

    def load_classes(self):
        """Загружает доступные классы с сервера и заполняет выпадающий список для вкладки ученика."""
        try:
            response = requests.get(f"{SERVER_URL}/classes")
            response.raise_for_status()  # Проверяем на ошибки HTTP
            classes = response.json()
            self.student_class.clear()  # Очищаем предыдущие элементы
            self.student_class.addItems(classes)

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к серверу: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке классов: {e}")

    def add_user(self):
        """
        Добавляет пользователя, отправляя данные на сервер Flask.
        """
        current_tab = self.tabs.currentIndex()
        user_data = {}

        if current_tab == 0:  # Администратор
            user_data['role'] = 'admin'
            user_data['login'] = self.admin_login.text()
            user_data['password'] = self.admin_password.text()
            user_data['admin_name'] = self.admin_name.text()

        elif current_tab == 1:  # Учитель
            user_data['role'] = 'teacher'
            user_data['login'] = self.teacher_login.text()
            user_data['password'] = self.teacher_password.text()
            user_data['teacher_surname'] = self.teacher_surname.text()
            user_data['teacher_name'] = self.teacher_name.text()
            user_data['teacher_patronymic'] = self.teacher_patronymic.text()

            # Получаем список выбранных классов
            selected_classes = []
            for i in range(self.teacher_classes.count()):
                item = self.teacher_classes.item(i)
                if item.checkState() == Qt.Checked:
                    selected_classes.append(item.text())

            user_data['classes'] = selected_classes  # Отправляем выбранные классы

        elif current_tab == 2:  # Ученик
            user_data['role'] = 'student'
            user_data['login'] = self.student_login.text()
            user_data['password'] = self.student_password.text()
            user_data['class_name'] = self.student_class.currentText()
            user_data['student_name'] = self.student_name.text()
            user_data['student_surname'] = self.student_surname.text()
            user_data['student_patronymic'] = self.student_patronymic.text()

        else:
            QMessageBox.warning(self, "Ошибка", "Выберите роль пользователя.")
            return

        try:
            response = requests.post(f"{SERVER_URL}/add_user", json=user_data)
            response.raise_for_status()  # Вызываем HTTPError для плохих ответов (4xx или 5xx)
            result = response.json()

            QMessageBox.information(self, "Успех", result.get("message", "Пользователь успешно добавлен."))
            # После успешного добавления класса обновляем списки классов в других вкладках

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к серверу: {e}")
        except requests.exceptions.HTTPError as e:
            error_message = response.json().get("message", "Неизвестная ошибка")
            print(f"Ошибка сервера: {error_message}")
            QMessageBox.warning(self, "Ошибка", f"Ошибка: {error_message}")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Установка стиля для всего приложения
    app.setStyleSheet("""
        QLabel {
            color: #333333;
            font-size: 14px;
        }
        QLineEdit {
            padding: 10px;
            font-size: 14px;
            border: 2px solid #cccccc;
            border-radius: 5px;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QComboBox {
            padding: 5px;
            font-size: 14px;
            border: 1px solid #cccccc;
            border-radius: 3px;
        }
    """)
    gui = MainGUI()
    gui.show()
    sys.exit(app.exec_())