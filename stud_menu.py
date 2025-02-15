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
    def __init__(self, login, class_name):
        super().__init__()
        self.login = login
        self.class_name = class_name
        self.current_date = datetime.date.today()
        self.initUI()
        self.update_date_display()
        self.update_schedule_homework()  # Combined update

    def initUI(self):
        # Настройка окна
        self.setWindowTitle('Дневник')
        self.setGeometry(100, 100, 1000, 700)  # Increased size
        self.setStyleSheet("background-color: #222222;")  # Dark background

        # Основной макет
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)

        # Заголовок и иконка флага
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        title_label = QLabel('Дневник', self)
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #FFFFFF; margin-left: 20px;")
        header_layout.addWidget(title_label)

        header_layout.addStretch(1)

        flag_icon = QLabel()
        flag_icon.setPixmap(QIcon("russia_flag_icon.png").pixmap(35, 35))  # Adjust path and size as needed
        header_layout.addWidget(flag_icon)
        header_layout.setContentsMargins(0, 0, 20, 0) # add margin to the right

        main_layout.addLayout(header_layout)

         # Date Layout
        date_layout = QHBoxLayout()
        date_layout.setAlignment(Qt.AlignCenter)
        date_layout.setSpacing(0) # remove spacing between date labels

        self.prev_day_button = QPushButton("<", self)
        self.prev_day_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.prev_day_button.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        self.prev_day_button.setCursor(Qt.PointingHandCursor)
        self.prev_day_button.clicked.connect(self.previous_day)
        date_layout.addWidget(self.prev_day_button)

        self.day_label = QLabel("", self)
        self.day_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.day_label.setStyleSheet("color: #FFFFFF; background-color: #663399; padding: 3px 10px; border-radius: 5px;")
        date_layout.addWidget(self.day_label)

        self.day_number_label = QLabel("", self)
        self.day_number_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.day_number_label.setStyleSheet("color: #FFFFFF; padding: 0 10px; border-radius: 5px;")
        date_layout.addWidget(self.day_number_label)

        self.year_label = QLabel("z", self)
        self.year_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.year_label.setStyleSheet("color: #FFFFFF; padding: 3px 10px; border-radius: 5px;")
        date_layout.addWidget(self.year_label)

        self.next_day_button = QPushButton(">", self)
        self.next_day_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.next_day_button.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        self.next_day_button.setCursor(Qt.PointingHandCursor)
        self.next_day_button.clicked.connect(self.next_day)
        date_layout.addWidget(self.next_day_button)
        
        self.month_label = QLabel("", self)
        self.month_label.setFont(QFont("Arial", 10))
        self.month_label.setStyleSheet("color: #FFFFFF; margin-top: 5px; margin-bottom: 20px;")
        month_layout = QVBoxLayout()
        month_layout.setAlignment(Qt.AlignHCenter)
        month_layout.addLayout(date_layout)
        month_layout.addWidget(self.month_label)
        main_layout.addLayout(month_layout)

        # Tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabWidget::pane { border: none; }")

        # Combined Schedule and Homework Tab
        self.schedule_homework_tab = QWidget()
        self.schedule_homework_layout = QVBoxLayout(self.schedule_homework_tab)

        self.schedule_homework_table = QTableWidget()
        self.schedule_homework_table.setStyleSheet("""
            QTableWidget {
                background-color: #333333;
                color: #FFFFFF;
                border: none;
                font-size: 14px; /* Increase font size */
            }
            QHeaderView::section {
                background-color: #444444;
                color: white;
                border: none;
                padding: 5px;
                font-size: 14px; /* Increase font size */
            }
        """)
        self.schedule_homework_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Auto-size columns
        self.schedule_homework_table.verticalHeader().setVisible(False) # Hide row numbers
        self.schedule_homework_layout.addWidget(self.schedule_homework_table)
        self.tab_widget.addTab(self.schedule_homework_tab, "Расписание и ДЗ")

        # Grades Tab
        self.grades_tab = QWidget()
        self.grades_layout = QVBoxLayout(self.grades_tab)
        self.update_grades()
        self.tab_widget.addTab(self.grades_tab, "Оценки")

        main_layout.addWidget(self.tab_widget)

        self.setLayout(main_layout)

    def update_date_display(self):
        days_week = {
            "Monday": "понедельник",
            "Tuesday": "вторник",
            "Wednesday": "среда",
            "Thursday": "четверг",
            "Friday": "пятница",
            "Saturday": "суббота",
            "Sunday": "воскресенье"
        }

        weekday_name = self.current_date.strftime("%A")
        self.day_label.setText(days_week[weekday_name])
        self.day_number_label.setText(str(self.current_date.day))
        self.year_label.setText(f"{self.current_date.year}г.")
        self.month_label.setText(self.current_date.strftime("%B"))

    def previous_day(self):
        self.current_date -= datetime.timedelta(days=1)
        self.update_date_display()
        self.update_schedule_homework()

    def next_day(self):
        self.current_date += datetime.timedelta(days=1)
        self.update_date_display()
        self.update_schedule_homework()

    def update_schedule_homework(self):
        # Get schedule
        days_week =['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        to_day =self.current_date.weekday()
        way = f"dbs/time_table.db"
        con = sqlite3.connect(way)
        cur = con.cursor()
        cur.execute(f"SELECT {days_week[to_day]} FROM time_table")
        schedule_rows = cur.fetchall()
        schedule = [row[0] for row in schedule_rows]
        schedule = [lesson if lesson else "" for lesson in schedule] # Replace None with empty string
        con.close()

        # Get homework
        date_str = self.current_date.strftime("%Y-%m-%d")
        way = f"dbs/home_works.db"
        con = sqlite3.connect(way)
        cur = con.cursor()
        cur.execute(f"SELECT * FROM home_work WHERE Date = ?", (date_str,))
        homework_data = cur.fetchone()
        con.close()

        # Prepare homework dictionary
        homework = {}
        if homework_data:
            column_names = [description[0] for description in cur.description]
            for i in range(1, len(homework_data)):
                lesson_name = column_names[i]
                homework[lesson_name] = homework_data[i] if homework_data[i] else ""

        # Get grades
        grades = self.get_grades_for_date(date_str)

        # Combine schedule and homework
        num_rows = len(schedule)
        self.schedule_homework_table.setRowCount(num_rows)
        self.schedule_homework_table.setColumnCount(4)  # Add column for grades
        self.schedule_homework_table.setHorizontalHeaderLabels(["№", "Предмет", "Домашнее задание", "Оценка"])
        self.schedule_homework_table.setColumnWidth(0, 50)  # Set width for number column

        for row in range(num_rows):
            lesson_name = schedule[row]

            # Lesson number
            lesson_number_item = QTableWidgetItem(str(row + 1))
            lesson_number_item.setTextAlignment(Qt.AlignCenter)
            lesson_number_item.setFlags(lesson_number_item.flags() & ~Qt.ItemIsEditable)  # Make it non-editable
            self.schedule_homework_table.setItem(row, 0, lesson_number_item)

            # Lesson
            lesson_item = QTableWidgetItem(lesson_name)
            lesson_item.setTextAlignment(Qt.AlignCenter)
            lesson_item.setFlags(lesson_item.flags() & ~Qt.ItemIsEditable)  # Make it non-editable
            self.schedule_homework_table.setItem(row, 1, lesson_item)

            # Homework
            homework_text = homework.get(lesson_name, "")
            homework_item = QTableWidgetItem(homework_text)
            homework_item.setTextAlignment(Qt.AlignCenter)
            homework_item.setFlags(homework_item.flags() & ~Qt.ItemIsEditable)  # Make it non-editable
            self.schedule_homework_table.setItem(row, 2, homework_item)

            # Grade
            grade = grades.get(lesson_name, "")  # Get grade, if any
            grade_item = QTableWidgetItem(str(grade))
            grade_item.setTextAlignment(Qt.AlignCenter)
            grade_item.setFlags(grade_item.flags() & ~Qt.ItemIsEditable)
            self.schedule_homework_table.setItem(row, 3, grade_item)

            # Color the row based on whether there's a lesson
            if lesson_name:
                for col in range(4):
                    self.schedule_homework_table.item(row, col).setBackground(QColor("#333333"))
            else:
                for col in range(4):
                    self.schedule_homework_table.item(row, col).setBackground(QColor("#555555"))


        self.schedule_homework_table.resizeColumnsToContents()

    def get_grades_for_date(self, date_str):
        """Retrieves grades for a specific date from the student's database."""
        grades = {}
        way = f"dbs/{self.login}.db"
        try:
            con = sqlite3.connect(way)
            cur = con.cursor()

            # Get all column names except "Дата"
            cur.execute("PRAGMA table_info(marks)")
            columns_info = cur.fetchall()
            lesson_names = [col[1] for col in columns_info if col[1] != "Дата"]

            # Build query to fetch the specified columns along with the date
            select_columns = ", ".join(lesson_names)
            query = f"SELECT {select_columns} FROM marks WHERE Дата = ?"

            # Execute query
            cur.execute(query, (date_str,))
            grade_data = cur.fetchone()  # Fetch results

            if grade_data:
                # Prepare dictionary with lesson names and grades
                for i, lesson_name in enumerate(lesson_names):
                    grades[lesson_name] = grade_data[i] if grade_data[i] is not None else ""
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            if con:
                con.close()
        return grades

    def update_grades(self):
        # Clear existing grades layout
        for i in reversed(range(self.grades_layout.count())):
            widget = self.grades_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Connect to student's grades database
        way = f"dbs/{self.login}.db"
        con = sqlite3.connect(way)
        cur = con.cursor()

        # Fetch all grades
        cur.execute("SELECT * FROM marks")
        grades_data = cur.fetchall()

        # Get column names
        cur.execute("PRAGMA table_info(marks)")
        columns_info = cur.fetchall()
        column_names = [col[1] for col in columns_info]

        con.close()

        # Create a table to display grades
        grades_table = QTableWidget()
        grades_table.setColumnCount(len(column_names))
        grades_table.setRowCount(len(grades_data))
        grades_table.setHorizontalHeaderLabels(column_names)

        # Apply style to the header
        header = grades_table.horizontalHeader()
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #444444;
                color: #FFFFFF;
                border: none;
                padding: 5px;
                font-size: 14px; /* Increase font size */
            }
        """)
        # Apply style to the table itself
        grades_table.setStyleSheet("""
            QTableWidget {
                background-color: #333333;
                color: #FFFFFF;
                border: none;
                font-size: 14px; /* Increase font size */
            }
        """)

        # Fill the table with data
        for row_index, row_data in enumerate(grades_data):
            for col_index, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data) if cell_data is not None else "") # Replace None
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make cells non-editable
                grades_table.setItem(row_index, col_index, item)
        # Set the stretch property of the horizontal header
        header = grades_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.grades_layout.addWidget(grades_table)
        grades_table.resizeColumnsToContents()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StudentInterface("stud1", "1А") #!!!!
    window.show()
    sys.exit(app.exec_())