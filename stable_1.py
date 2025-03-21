import sys
import csv

import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget,
                             QLineEdit, QMessageBox, QComboBox, QTabWidget, QDialog, QFormLayout, QListWidget,
                             QInputDialog)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from datetime import datetime
import matplotlib.pyplot as plt

# Файлы данных
USER_CSV = "users.csv"
TESTS_CSV = "tests.csv"
RESULTS_CSV = "results.csv"
COURSES_CSV = "courses.csv"
SETTINGS_CSV = "settings.csv"


class CreateCourseDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Создание курса")
        self.setGeometry(200, 200, 400, 150)

        layout = QFormLayout()
        self.course_name_input = QLineEdit()
        layout.addRow("Название курса:", self.course_name_input)

        self.create_button = QPushButton("Создать курс")
        self.create_button.clicked.connect(self.create_course)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def create_course(self):
        course_name = self.course_name_input.text().strip()
        if not course_name:
            QMessageBox.warning(self, "Ошибка", "Введите название курса!")
            return

        with open(COURSES_CSV, "a", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([course_name])

        QMessageBox.information(self, "Успех", f"Курс '{course_name}' успешно создан!")
        self.accept()


class AssignStudentsDialog(QDialog):
    def __init__(self, courses, students):
        super().__init__()
        self.setWindowTitle("Закрепление студентов за курсом")
        self.setGeometry(200, 200, 400, 300)

        layout = QFormLayout()

        # Выпадающий список для выбора курса
        self.course_select = QComboBox()
        self.course_select.addItems(courses)
        layout.addRow("Выберите курс:", self.course_select)

        # Список студентов с возможностью множественного выбора
        self.student_select = QListWidget()
        self.student_select.addItems(students)
        self.student_select.setSelectionMode(QListWidget.MultiSelection)  # Множественный выбор
        layout.addRow("Выберите студентов:", self.student_select)

        self.assign_button = QPushButton("Закрепить")
        self.assign_button.clicked.connect(self.assign_students_to_course)
        layout.addWidget(self.assign_button)

        self.setLayout(layout)

    def assign_students_to_course(self):
        selected_course = self.course_select.currentText()
        selected_students = [item.text() for item in self.student_select.selectedItems()]

        if not selected_students:
            QMessageBox.warning(self, "Ошибка", "Не выбраны студенты для закрепления!")
            return

        try:
            with open(COURSES_CSV, "r", encoding="utf-8", newline="") as file:
                reader = csv.reader(file)
                courses_data = list(reader)

            updated_courses_data = []
            for row in courses_data:
                if row and row[0] == selected_course:  # Если курс уже существует
                    for student in selected_students:
                        if student not in row:  # Добавляем студента только если его еще нет в списке
                            row.append(student)
                updated_courses_data.append(row)  # Добавляем обновленную строку

            with open(COURSES_CSV, "w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(updated_courses_data)  # Записываем обновленные данные

            QMessageBox.information(self, "Успех", f"Студенты {', '.join(selected_students)} успешно закреплены за курсом '{selected_course}'!")
            self.accept()

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Произошла ошибка при закреплении студентов: {e}")


class QuizApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система тестирования")
        self.setGeometry(100, 100, 800, 600)

        self.dpi_value = 96  # Значение DPI по умолчанию
        self.load_settings()  # Загружаем настройки из файла
        self.initUI()

    def initUI(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.login_panel = QWidget()
        self.tabs.addTab(self.login_panel, "Вход")

        layout = QVBoxLayout()
        self.label = QLabel("Добро пожаловать! Введите логин и выберите роль:")
        self.label.setFont(QFont("Arial", 14))
        layout.addWidget(self.label)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        layout.addWidget(self.login_input)

        self.teacher_button = QPushButton("Преподаватель")
        self.student_button = QPushButton("Ученик")
        layout.addWidget(self.teacher_button)
        layout.addWidget(self.student_button)

        self.teacher_button.clicked.connect(lambda: self.login("teacher"))
        self.student_button.clicked.connect(lambda: self.login("student"))

        self.login_panel.setLayout(layout)

        # Стилизация с помощью QSS
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #f0f8ff;
                font-family: Arial, sans-serif;
                font-size: {int(14 * self.dpi_value / 96)}px;
            }}
            QPushButton {{
                background-color: #87cefa;
                color: white;
                font-size: {int(14 * self.dpi_value / 96)}px;
                padding: {int(10 * self.dpi_value / 96)}px;
                border-radius: 5px;
            }}
            QLineEdit {{
                padding: {int(10 * self.dpi_value / 96)}px;
                border-radius: 5px;
                font-size: {int(14 * self.dpi_value / 96)}px;
            }}
            QLabel {{
                color: #000080;
                font-size: {int(16 * self.dpi_value / 96)}px;
            }}
            QTabWidget {{
                font-size: {int(14 * self.dpi_value / 96)}px;
            }}
            QComboBox {{
                font-size: {int(14 * self.dpi_value / 96)}px;
            }}
        """)

    def load_settings(self):
        """Загрузка настроек из settings.csv"""
        try:
            with open(SETTINGS_CSV, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                settings = {row[0]: row[1] for row in reader}

            if "dpi" in settings:
                self.dpi_value = int(settings["dpi"])

        except FileNotFoundError:
            # Если файл настроек не найден, используем значение по умолчанию
            self.dpi_value = 96

    def save_settings(self):
        """Сохранение текущих настроек в settings.csv"""
        with open(SETTINGS_CSV, "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["dpi", self.dpi_value])

    def login(self, role):
        self.current_user = self.login_input.text().strip()
        if not self.current_user:
            QMessageBox.warning(self, "Ошибка", "Введите логин!")
            return

        with open(USER_CSV, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            users = {row[0]: row[1] for row in reader}  # логин: роль

        if self.current_user in users and users[self.current_user] == role:
            self.open_main_menu(role)
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или роль")

    def open_main_menu(self, role):
        self.tabs.clear()  # Очистим старые вкладки

        if role == "teacher":
            self.open_teacher_tabs()
        else:
            self.open_student_tabs()

    def open_teacher_tabs(self):
        self.tabs.setTabText(0, "Главное меню")

        self.tabs.addTab(self.create_teacher_test_tab(), "Тесты")
        self.tabs.addTab(self.create_teacher_stats_tab(), "Статистика")
        self.tabs.addTab(self.create_teacher_courses_tab(), "Курсы")
        self.tabs.addTab(self.create_teacher_settings_tab(), "Настройки")

    def open_student_tabs(self):
        self.tabs.setTabText(0, "Главное меню")

        self.tabs.addTab(self.create_student_test_tab(), "Тесты")
        self.tabs.addTab(self.create_student_stats_tab(), "Статистика")
        self.tabs.addTab(self.create_student_courses_tab(), "Курсы")
        self.tabs.addTab(self.create_student_settings_tab(), "Настройки")

    def create_teacher_test_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Поле для ввода вопроса
        self.add_question_input = QLineEdit()
        self.add_question_input.setPlaceholderText("Введите вопрос")
        layout.addWidget(self.add_question_input)

        # Поле для ввода ответа
        self.add_answer_input = QLineEdit()
        self.add_answer_input.setPlaceholderText("Введите правильный ответ")
        layout.addWidget(self.add_answer_input)

        # Выпадающий список для выбора теста
        self.test_select = QComboBox()

        with open(TESTS_CSV, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.reader(csvfile)
            tests = set()
            for row in reader:
                if row:  # Проверяем, что строка не пустая
                    tests.add(row[0])
            self.test_select.addItems(list(tests))

        layout.addWidget(self.test_select)

        # Кнопка для добавления нового теста
        self.create_test_button = QPushButton("Создать новый тест")
        self.create_test_button.clicked.connect(self.create_new_test)
        layout.addWidget(self.create_test_button)

        # Кнопка для добавления вопроса
        self.save_question_button = QPushButton("Добавить вопрос")
        self.save_question_button.clicked.connect(self.save_question)
        layout.addWidget(self.save_question_button)


        tab.setLayout(layout)
        return tab



    def load_tests(self):
        """Загрузка доступных тестов.  Адаптировано для преподавателя и студента."""
        try:
            with open(TESTS_CSV, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                tests = [row[0] for row in reader if row]  # Загружаем только непустые строки
                if not tests:
                    if hasattr(self, 'test_list'): # Проверка наличия атрибута
                        self.test_list.addItem("Нет доступных тестов!")
                    else:
                        self.test_select.addItem("Нет доступных тестов!") # Для преподавателя
                    return
        except FileNotFoundError:
            if hasattr(self, 'test_list'):
                self.test_list.addItem(f"Файл {TESTS_CSV} не найден!")
            else:
                self.test_select.addItem(f"Файл {TESTS_CSV} не найден!")
            return
        except Exception as e:
            if hasattr(self, 'test_list'):
                self.test_list.addItem(f"Ошибка при загрузке тестов: {str(e)}")
            else:
                self.test_select.addItem(f"Ошибка при загрузке тестов: {str(e)}")
            return

        if hasattr(self, 'test_list'): # Если это студент
            self.test_list.clear()
            for test in tests:
                self.test_list.addItem(test)
            self.start_test_button.setEnabled(True)
        else: # Если это преподаватель
            self.test_select.clear()
            for test in tests:
                self.test_select.addItem(test)


    def start_test(self):
        """Начать прохождение выбранного теста"""
        selected_test = self.test_list.currentItem().text()
        if not selected_test:
            QMessageBox.warning(self, "Ошибка", "Выберите тест для начала!")
            return

        self.selected_test = selected_test  # Сохраняем выбранный тест
        print(
            f"Выбран тест: {self.selected_test}")  # Отладочное сообщение

        # Загружаем вопросы выбранного теста
        questions = self.load_test_questions(self.selected_test)

        if not questions:
            QMessageBox.warning(
                self, "Ошибка", "Не удалось загрузить вопросы для выбранного теста.")
            return

        self.display_test(questions)

    def load_test_questions(self, test_name):
        """Загрузка вопросов для выбранного теста"""
        questions = []
        try:
            with open(TESTS_CSV, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row and row[0] == test_name:  # Если это нужный тест
                        questions.append(
                            (row[1], row[2]))  # Вопрос и правильный ответ
        except FileNotFoundError:
            QMessageBox.warning(self, "Ошибка", f"Файл {TESTS_CSV} не найден!")
            return []

        return questions

    def display_test(self, questions):
        """Отображение вопросов для прохождения теста"""
        self.test_form_layout = QFormLayout()

        # Сохраняем вопросы в атрибуте для доступа после заполнения
        self.questions = questions
        self.answers = []

        # Добавляем вопросы на форму
        for i, (question, correct_answer) in enumerate(self.questions):
            question_label = QLabel(question)
            self.test_form_layout.addRow(question_label)

            # Добавляем поле для ответа
            answer_input = QLineEdit()
            answer_input.setPlaceholderText("Введите ваш ответ")
            self.test_form_layout.addRow(answer_input)

            self.answers.append(
                (answer_input, correct_answer))  # Сохраняем поле ответа и правильный ответ

        # Кнопка для отправки теста
        self.submit_button = QPushButton("Отправить тест")
        self.submit_button.clicked.connect(self.submit_test)
        self.test_form_layout.addRow(self.submit_button)

        # Создаем новый виджет для отображения вопросов
        test_form_widget = QWidget()
        test_form_widget.setLayout(self.test_form_layout)

        # Добавляем виджет на вкладку
        self.test_tab = QWidget()
        self.test_tab.setLayout(self.test_form_layout)
        self.tabs.addTab(self.test_tab, "Тест")

        # Выводим отладочную информацию
        print("Тест с вопросами успешно отображен")

    def submit_test(self):
        """Обработка результатов теста и запись в файл."""
        score = 0
        total_questions = len(self.answers)

        for answer_input, correct_answer in self.answers:
            if answer_input.text().strip().lower() == correct_answer.lower():
                score += 1

        QMessageBox.information(self, "Результат", f"Вы набрали {score} из {total_questions} баллов!")

        # Запись результатов в файл
        try:
            with open(RESULTS_CSV, "a", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Добавляем отметку времени
                writer.writerow([self.current_user, self.selected_test, score, timestamp]) # Добавляем тест и время
            print(f"Результат теста записан в {RESULTS_CSV}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось записать результат в файл: {str(e)}")

        self.tabs.removeTab(self.tabs.indexOf(self.test_tab))
        print(f"Тест завершен, результат: {score}/{total_questions}")


    def load_courses(self):
        """Загрузка доступных курсов для студента"""
        try:
            with open(COURSES_CSV, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                courses = [row[0] for row in reader if row]  # Загружаем только непустые строки
                if not courses:
                    self.courses_list.addItem("Нет доступных курсов!")
                    return
        except FileNotFoundError:
            self.courses_list.addItem(f"Файл {COURSES_CSV} не найден!")
            return
        except Exception as e:
            self.courses_list.addItem(
                f"Ошибка при загрузке курсов: {str(e)}")
            return

        self.courses_list.clear()  # Очищаем список перед добавлением новых данных
        for course in courses:
            self.courses_list.addItem(course)  # Добавляем каждый курс в список

    def create_new_test(self):
        """Создание нового теста и добавление его в файл и список"""
        test_name, ok = QInputDialog.getText(
            self, "Новый тест", "Введите название нового теста:")

        if ok and test_name.strip():
            # Добавляем новый тест в файл
            with open(TESTS_CSV, "a", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [test_name.strip(), "", ""])  # Сохраняем тест в формате CSV (например, пустые вопросы и ответы)


            QMessageBox.information(
                self, "Успех", f"Тест '{test_name.strip()}' успешно создан!")
        else:
            QMessageBox.warning(self, "Ошибка", "Введите корректное название теста.")


        # Обновляем список тестов в выпадающем списке
        self.test_select.clear()
        with open(TESTS_CSV, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.reader(csvfile)
            tests = set()
            for row in reader:
                if row:  # Проверяем, что строка не пустая
                    tests.add(row[0])
            self.test_select.addItems(list(tests))

    def create_teacher_stats_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # График статистики
        self.view_stats_button = QPushButton("Просмотр статистики")
        self.view_stats_button.clicked.connect(self.view_teacher_stats)
        layout.addWidget(self.view_stats_button)

        tab.setLayout(layout)
        return tab

    def create_teacher_courses_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.create_course_button = QPushButton("Создать курс")
        self.create_course_button.clicked.connect(self.create_course)
        layout.addWidget(self.create_course_button)

        self.assign_students_button = QPushButton(
            "Закрепить студентов за курсами")
        self.assign_students_button.clicked.connect(self.assign_students)
        layout.addWidget(self.assign_students_button)

        tab.setLayout(layout)
        return tab

    def create_teacher_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.dpi_label = QLabel("Настройка DPI интерфейса:")
        layout.addWidget(self.dpi_label)

        self.dpi_input = QLineEdit()
        self.dpi_input.setPlaceholderText(
            "Введите значение DPI (например, 96, 120, 144)")
        layout.addWidget(self.dpi_input)

        self.save_dpi_button = QPushButton("Сохранить DPI")
        self.save_dpi_button.clicked.connect(self.save_dpi)
        layout.addWidget(self.save_dpi_button)

        tab.setLayout(layout)
        return tab

    def create_student_test_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Кнопка для загрузки доступных тестов
        self.load_tests_button = QPushButton("Загрузить доступные тесты")
        self.load_tests_button.clicked.connect(self.load_tests)
        layout.addWidget(self.load_tests_button)

        # Список доступных тестов
        self.test_list_label = QLabel("Доступные тесты:")
        layout.addWidget(self.test_list_label)

        self.test_list = QListWidget()
        layout.addWidget(self.test_list)

        # Кнопка для начала теста
        self.start_test_button = QPushButton("Начать тест")
        self.start_test_button.setEnabled(
            False)  # Отключаем кнопку, пока не выбран тест
        self.start_test_button.clicked.connect(self.start_test)
        layout.addWidget(self.start_test_button)

        # Загружаем тесты при открытии вкладки
        self.load_tests()

        tab.setLayout(layout)
        return tab

    def create_student_stats_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.view_stats_button = QPushButton("Просмотр своей статистики")
        self.view_stats_button.clicked.connect(self.view_student_stats)
        layout.addWidget(self.view_stats_button)

        tab.setLayout(layout)
        return tab

    def create_student_courses_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Список доступных курсов
        self.courses_list_label = QLabel("Доступные курсы:")
        layout.addWidget(self.courses_list_label)

        self.courses_list = QListWidget()
        layout.addWidget(self.courses_list)

        # Загружаем курсы при открытии вкладки
        self.load_courses()

        tab.setLayout(layout)
        return tab

    def create_student_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.dpi_label = QLabel("Настройка DPI интерфейса:")
        layout.addWidget(self.dpi_label)

        self.dpi_input = QLineEdit()
        self.dpi_input.setPlaceholderText(
            "Введите значение DPI (например, 96, 120, 144)")
        layout.addWidget(self.dpi_input)

        self.save_dpi_button = QPushButton("Сохранить DPI")
        self.save_dpi_button.clicked.connect(self.save_dpi)
        layout.addWidget(self.save_dpi_button)

        tab.setLayout(layout)
        return tab

    def save_question(self):
        question = self.add_question_input.text().strip()
        answer = self.add_answer_input.text().strip()
        if not question or not answer:
            QMessageBox.warning(self, "Ошибка", "Введите вопрос и ответ!")
            return

        test_name = self.test_select.currentText()

        with open(TESTS_CSV, "a", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([test_name, question, answer])

        QMessageBox.information(self, "Успех", "Вопрос добавлен!")
        self.add_question_input.clear()
        self.add_answer_input.clear()

    def save_dpi(self):
        dpi_value = self.dpi_input.text().strip()
        if dpi_value.isdigit():
            self.dpi_value = int(dpi_value)
            self.setGeometry(100, 100, 800 * self.dpi_value //
                            96, 600 * self.dpi_value // 96)
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: #f0f8ff;
                    font-family: Arial, sans-serif;
                    font-size: {int(14 * self.dpi_value / 96)}px;
                }}
                QPushButton {{
                    background-color: #87cefa;
                    color: white;
                    font-size: {int(14 * self.dpi_value / 96)}px;
                    padding: {int(10 * self.dpi_value / 96)}px;
                    border-radius: 5px;
                }}
                QLineEdit {{
                    padding: {int(10 * self.dpi_value / 96)}px;
                    border-radius: 5px;
                    font-size: {int(14 * self.dpi_value / 96)}px;
                }}
                QLabel {{
                    color: #000080;
                    font-size: {int(16 * self.dpi_value / 96)}px;
                }}
                QTabWidget {{
                    font-size: {int(14 * self.dpi_value / 96)}px;
                }}
                QComboBox {{
                    font-size: {int(14 * self.dpi_value / 96)}px;
                }}
            """)
            self.save_settings()  # Сохраняем новые настройки
            QMessageBox.information(
                self, "Успех", f"DPI изменено на {self.dpi_value}")
        else:
            QMessageBox.warning(self, "Ошибка", "Введите корректное значение DPI")

    def view_teacher_stats(self):
        try:
            with open(RESULTS_CSV, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                # next(reader)  # Не нужно пропускать заголовок, если его нет
                results = [row for row in reader if row]  # Пропускаем пустые строки

            if not results:
                QMessageBox.information(self, "Статистика", "Нет данных для отображения.")
                return

            students = sorted(
                list(set([row[0] for row in results])))  # Уникальные студенты, отсортированные по алфавиту

            student_scores = {}
            for student in students:
                student_scores[student] = []  # Инициализируем список баллов для каждого студента

            for row in results:
                student = row[0]
                try:
                    score = int(row[2])  # Баллы теперь в третьем столбце
                    student_scores[student].append(score)
                except (ValueError, IndexError) as e:
                    print(f"Ошибка в данных для студента {student}: {e}")  # Выводим ошибку в консоль для отладки
                    continue  # Пропускаем некорректную строку

            x = np.arange(len(students))
            width = 0.5

            fig, ax = plt.subplots()

            for i, student in enumerate(students):
                scores = student_scores[student]
                if scores:  # Если есть баллы для студента
                    ax.bar(x[i], np.mean(scores), width, label=student if i == 0 else "",
                           color=plt.cm.get_cmap('hsv', len(students))(i))  # Разные цвета для каждого студента

            ax.set_ylabel('Средний балл')
            ax.set_title('Статистика по результатам тестов (средние баллы)')
            ax.set_xticks(x)
            ax.set_xticklabels(students, rotation=45, ha='right')
            ax.legend()

            fig.tight_layout()
            plt.show()

        except FileNotFoundError:
            QMessageBox.warning(self, "Ошибка", f"Файл {RESULTS_CSV} не найден.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def view_student_stats(self):
        try:
            with open(RESULTS_CSV, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                results = [row for row in reader if row and row[0] == self.current_user]  # Фильтруем результаты текущего студента, проверяем на пустые строки

            if not results:
                QMessageBox.information(self, "Статистика", "Нет данных для отображения.")
                return

            tests = [row[1] for row in results]  # Название теста
            scores = [int(row[2]) for row in results]  # Баллы

            x = np.arange(len(tests))
            width = 0.5

            fig, ax = plt.subplots()
            rects = ax.bar(x, scores, width, label='Баллы')

            ax.set_ylabel('Баллы')
            ax.set_title(f'Результаты студента {self.current_user}')
            ax.set_xticks(x)
            ax.set_xticklabels(tests, rotation=45, ha='right')
            ax.legend()

            for rect in rects:
                height = rect.get_height()
                ax.annotate(f'{height}',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom')

            fig.tight_layout()
            plt.show()

        except FileNotFoundError:
            QMessageBox.warning(self, "Ошибка", f"Файл {RESULTS_CSV} не найден.")
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Неверный формат данных в файле результатов. Убедитесь, что баллы представлены числами.")
        except IndexError:  # Обработка IndexError, если строка не содержит достаточно элементов
            QMessageBox.warning(self, "Ошибка", "Неверный формат данных в файле результатов. Проверьте количество столбцов в каждой строке.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")


    def create_course(self):
        dialog = CreateCourseDialog()
        dialog.exec()

    def assign_students(self):
        # Получаем список курсов и студентов
        with open(COURSES_CSV, "r", encoding="utf-8") as file:
            courses = [row[0] for row in csv.reader(file)]

        with open(USER_CSV, "r", encoding="utf-8") as file:
            students = [row[0] for row in csv.reader(
                file) if row and row[1] == "student"]

        dialog = AssignStudentsDialog(courses, students)
        dialog.exec()


app = QApplication(sys.argv)
window = QuizApp()
window.show()
sys.exit(app.exec_())