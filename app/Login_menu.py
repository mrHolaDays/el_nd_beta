import sys
import sqlite3 as sq
import requests
import os
import zipfile
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QFormLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from stud_menu import StudentInterface  # Импортируем интерфейс студента
from teach_menu import TeacherInterface  # Импортируем интерфейс учителя

SERVER_URL = "http://127.0.0.1:5000/process"  # URL-адрес сервера для обработки запросов

class LoginWindow(QWidget):
    """
    Класс окна входа в систему.
    """
    def __init__(self):
        """
        Инициализация окна входа.
        """
        super().__init__()
        self.initUI()
        self.login = None  # Добавляем атрибут для хранения логина пользователя

    def initUI(self):
        """
        Инициализация пользовательского интерфейса.
        """
        self.setWindowTitle('Электронный дневник')  # Устанавливаем заголовок окна
        self.setGeometry(100, 100, 400, 300)  # Устанавливаем размеры и положение окна
        self.setStyleSheet("background-color: #f0f0f0;")  # Устанавливаем цвет фона окна

        # Определяем шрифты для разных элементов интерфейса
        title_font = QFont("Arial", 18, QFont.Bold)
        label_font = QFont("Arial", 12)
        button_font = QFont("Arial", 12, QFont.Bold)

        self.title_label = QLabel('Вход в систему', self)  # Создаем метку заголовка
        self.title_label.setFont(title_font)  # Устанавливаем шрифт заголовка
        self.title_label.setAlignment(Qt.AlignCenter)  # Выравниваем текст заголовка по центру
        self.title_label.setStyleSheet("color: #333333; margin-bottom: 20px;")  # Устанавливаем стили заголовка

        self.login_input = QLineEdit(self)  # Создаем поле ввода для логина
        self.login_input.setPlaceholderText("Введите логин")  # Устанавливаем текст-подсказку для поля ввода логина
        self.login_input.setStyleSheet(
            "padding: 10px; font-size: 14px; border: 2px solid #cccccc; border-radius: 5px;"
        )  # Устанавливаем стили для поля ввода логина

        self.password_input = QLineEdit(self)  # Создаем поле ввода для пароля
        self.password_input.setPlaceholderText("Введите пароль")  # Устанавливаем текст-подсказку для поля ввода пароля
        self.password_input.setEchoMode(QLineEdit.Password)  # Устанавливаем режим отображения пароля (скрытый ввод)
        self.password_input.setStyleSheet(
            "padding: 10px; font-size: 14px; border: 2px solid #cccccc; border-radius: 5px;"
        )  # Устанавливаем стили для поля ввода пароля

        self.login_button = QPushButton('Войти', self)  # Создаем кнопку для входа
        self.login_button.setFont(button_font)  # Устанавливаем шрифт для кнопки
        self.login_button.setStyleSheet(
            """
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
            """
        )  # Устанавливаем стили для кнопки
        self.login_button.clicked.connect(self.on_login)  # Привязываем обработчик события нажатия кнопки

        # Создаем вертикальный макет для размещения элементов интерфейса
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)  # Добавляем заголовок в макет

        # Создаем макет формы для логина и пароля
        form_layout = QFormLayout()
        form_layout.addRow("Логин:", self.login_input)  # Добавляем поле ввода логина в макет формы
        form_layout.addRow("Пароль:", self.password_input)  # Добавляем поле ввода пароля в макет формы
        layout.addLayout(form_layout)  # Добавляем макет формы в основной макет

        layout.addWidget(self.login_button)  # Добавляем кнопку в макет
        self.setLayout(layout)  # Устанавливаем макет для окна

    def on_login(self):
        """
        Обработчик события нажатия кнопки "Войти".
        Выполняет аутентификацию пользователя и скачивание файлов с сервера.
        """
        login = self.login_input.text()  # Получаем логин из поля ввода
        password = self.password_input.text()  # Получаем пароль из поля ввода
        self.login = login  # Сохраняем логин пользователя

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Логин и пароль не могут быть пустыми!")  # Выводим сообщение об ошибке, если логин или пароль пустые
            return

        try:
            print(f"Отправка данных на сервер: логин={login}, пароль={password}")
            # Отправляем POST-запрос на сервер для аутентификации
            response = requests.post(
                SERVER_URL,
                json={"message": [login, password]},
                timeout=5  # Устанавливаем тайм-аут для запроса
            )

            if response.status_code == 200:
                print("Авторизация успешна. Скачивание файла...")

                # Формируем путь для сохранения скачанного ZIP-архива
                download_path = os.path.join(os.getcwd(), "dbs", f"{login}_files.zip")
                os.makedirs(os.path.dirname(download_path), exist_ok=True)  # Создаем директорию для сохранения файла, если она не существует

                # Скачиваем файл с сервера и сохраняем его
                with open(download_path, "wb") as file:
                    file.write(response.content)
                print(f"ZIP-архив успешно скачан и сохранён как {download_path}")

                # Определяем путь для распаковки ZIP-архива
                extract_to = os.path.join(os.getcwd(), "dbs")
                os.makedirs(extract_to, exist_ok=True)  # Создаем директорию для распаковки, если она не существует

                # Распаковываем ZIP-архив
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)

                print(f"Файлы распакованы в {extract_to}")

                # Получаем роль пользователя
                role = self.get_user_role(login)
                if role == "student":
                    # Запускаем интерфейс студента
                    self.open_student_interface(login)
                elif role == "teacher":
                    # Запускаем интерфейс учителя
                    self.open_teacher_interface(login)
                elif role == "admin":
                    # Запускаем интерфейс администратора (если есть)
                    self.open_admin_interface(login)
                else:
                    QMessageBox.warning(self, "Ошибка", "Неизвестная роль пользователя.")

            else:
                # Получаем сообщение об ошибке из ответа сервера
                error_message = response.json().get("message", "Неизвестная ошибка")
                print(f"Ошибка сервера: {error_message}")
                QMessageBox.warning(self, "Ошибка", f"Ошибка: {error_message}")  # Выводим сообщение об ошибке

        except requests.exceptions.RequestException as e:
            # Обрабатываем исключения, связанные с запросами к серверу
            print(f"Ошибка подключения к серверу: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к серверу: {e}")  # Выводим сообщение об ошибке подключения

    def get_user_role(self, login):
        """
        Получает роль пользователя из базы данных.
        """
        try:
            conn = sq.connect('logins.db')
            cur = conn.cursor()
            cur.execute("SELECT role FROM users WHERE login = ?", (login,))
            role = cur.fetchone()[0]
            return role
        except sq.Error as e:
            print(f"Ошибка базы данных: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def open_student_interface(self, login):
        """
        Запускает интерфейс студента.
        """
        class_name = self.get_user_class(login)
        if class_name:
            self.close()  # Закрываем окно входа
            self.student_interface = StudentInterface(login, class_name)  # Создаем экземпляр интерфейса студента
            self.student_interface.show()  # Отображаем интерфейс студента
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось определить класс студента.")

    def open_teacher_interface(self, login):
        """
        Запускает интерфейс учителя.
        """
        class_name = self.get_user_class(login)
        if class_name:
            self.close()  # Закрываем окно входа
            self.teacher_interface = TeacherInterface(login, class_name)  # Создаем экземпляр интерфейса учителя
            self.teacher_interface.show()  # Отображаем интерфейс учителя
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось определить класс учителя.")

    def open_admin_interface(self, login):
        """
        Запускает интерфейс администратора.
        """
        # Здесь можно добавить код для открытия интерфейса администратора
        QMessageBox.information(self, "Информация", "Интерфейс администратора пока не реализован.")

    def get_user_class(self, login):
        """
        Получает класс пользователя из базы данных.
        """
        try:
            conn = sq.connect('logins.db')
            cur = conn.cursor()
            cur.execute("SELECT info FROM users WHERE login = ?", (login,))
            info = cur.fetchone()[0]
            return info  # Предполагаем, что info содержит название класса
        except sq.Error as e:
            print(f"Ошибка базы данных: {e}")
            return None
        finally:
            if conn:
                conn.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)  # Создаем экземпляр приложения PyQt

    # Устанавливаем глобальные стили для приложения
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
    """)

    window = LoginWindow()  # Создаем экземпляр окна входа
    window.show()  # Отображаем окно
    sys.exit(app.exec_())