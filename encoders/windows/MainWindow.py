import csv
import re

# Импорт необходимых модулей из библиотеки PyQt5
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QTabWidget, QAction, QMessageBox, \
    QFileDialog, QLineEdit, QPushButton, QVBoxLayout, QTextEdit

from widgets.CaezarTab import CaezerTab
# Импортируем класс GilbertMooreEncoder для работы с алгоритмом кодирования
from widgets.GilbertMooreTab import GilbertMooreTab
from widgets.GilbertMooreWithCheckTab import GilbertMooreWithCheckersTab
from widgets.HammingTab import HammingTab
# Импортируем окно "О программе" из другого модуля
from windows.AboutWindow import AboutWindow


def prepare_additional_text(encoder, input=None, output=None):
    # Подготовка строки для вывода дополнительной информации с вводом и выводом
    result = str(encoder)  # Преобразуем объект encoder в строку
    if input is not None and output is not None:  # Если вход и выход заданы, добавляем их к результату
        result += "\n" + ("-" * 50) + "\n"  # Добавляем разделитель
        result += f"Ввод: {input}\n"  # Добавляем строку с входными данными
        result += f"Вывод: {output}\n"  # Добавляем строку с выходными данными
    return result  # Возвращаем итоговую строку


class MainWindow(QMainWindow):
    def __init__(self):
        # Инициализация главного окна
        super().__init__()

        self.probabilities = dict()  # Словарь для хранения вероятностей символов
        # self.encoder = None  # Объект для работы с кодировщиком

        # Настройка параметров окна
        self.setWindowTitle("Криптография")  # Устанавливаем заголовок окна
        self.setWindowIcon(QtGui.QIcon('icon.png'))  # Устанавливаем иконку окна
        self.initUI()  # Инициализируем пользовательский интерфейс
        self.create_menu()  # Создаем меню

    def initUI(self):
        # Создание основного виджета и его компоновки
        central_widget = QWidget()  # Основной виджет окна
        layout = QHBoxLayout()  # Горизонтальная компоновка элементов

        lines_layout = QVBoxLayout()

        # Поле ввода для последовательности
        sequence_line = QHBoxLayout()
        self.sequence_input = QLineEdit()  # Поле для ввода последовательности
        self.sequence_input.setDisabled(True)  # Изначально поле отключено
        self.sequence_input.setPlaceholderText("Введите последовательность")  # Текст подсказки
        sequence_line.addWidget(self.sequence_input)

        # Кнопка "Кодировать"
        self.encode_button = QPushButton("Кодировать")  # Создаем кнопку "Кодировать"
        self.encode_button.setDisabled(True)  # Изначально кнопка отключена
        self.encode_button.clicked.connect(self.encode)  # Подключаем функцию кодирования
        sequence_line.addWidget(self.encode_button)
        lines_layout.addLayout(sequence_line)

        decoded_sequence_line = QHBoxLayout()

        # Поле ввода для закодированной последовательности
        self.encoded_sequence_input = QLineEdit()  # Поле для ввода закодированной последовательности
        self.encoded_sequence_input.setDisabled(True)  # Изначально поле отключено
        self.encoded_sequence_input.setPlaceholderText("Введите закодированную последовательность")  # Текст подсказки

        # Регулярное выражение для проверки корректности ввода (допускаются только '1' и '0', и ';' в конце)
        regex_pattern = f"^[10]+;"
        regexp = QtCore.QRegExp(regex_pattern)  # Создаем объект регулярного выражения
        validator = QtGui.QRegExpValidator(regexp)  # Создаем валидатор для проверки ввода по регулярному выражению
        self.encoded_sequence_input.setValidator(validator)  # Присваиваем валидатор полю
        decoded_sequence_line.addWidget(self.encoded_sequence_input)

        # Кнопка "Декодировать"
        self.decode_button = QPushButton("Декодировать")  # Создаем кнопку "Декодировать"
        self.decode_button.setDisabled(True)  # Изначально кнопка отключена
        self.decode_button.clicked.connect(self.decode)  # Подключаем функцию декодирования
        decoded_sequence_line.addWidget(self.decode_button)
        lines_layout.addLayout(decoded_sequence_line)

        # Создание вкладочного виджета и добавление вкладки
        self.tab_widget = QTabWidget()
        gilbert_moore_tab = GilbertMooreTab(self)
        gilbert_moore_with_check_tab = GilbertMooreWithCheckersTab(self)
        hamming_tab = HammingTab(self)
        caezar_tab = CaezerTab(self)
        self.tab_widget.addTab(gilbert_moore_tab, "Гильберт-Мур")  # Вкладка для алгоритма Гильберта-Мура
        self.tab_widget.addTab(gilbert_moore_with_check_tab, "Гильберт-Мур с проверкой")
        self.tab_widget.addTab(hamming_tab, "Хэмминг")
        self.tab_widget.addTab(caezar_tab, "Цезарь")
        self.tab_widget.currentChanged.connect(self.update_encoder)
        layout.addWidget(self.tab_widget)

        # Поле для вывода дополнительной информации
        self.additional_info_field = QTextEdit()  # Поле для вывода информации
        self.additional_info_field.setText(
            "Инструкция:\n1. Выберите файл алфавита и вероятностей\n2. Введите последовательность\n3. нажмите на кодировать или декодировать")
        self.additional_info_field.setReadOnly(True)  # Поле только для чтения
        layout.addWidget(self.additional_info_field)

        lines_layout.addLayout(layout)
        # Устанавливаем компоновку для центрального виджета
        central_widget.setLayout(lines_layout)
        self.setCentralWidget(central_widget)  # Устанавливаем центральный виджет
        self.statusBar().showMessage("Выберете файл алфавита и вероятностей")  # Сообщение в статусной строке

    def create_menu(self):
        # Создание меню в верхней части окна
        menubar = self.menuBar()

        # Создание меню "Файл"
        file_menu = menubar.addMenu("Файл")

        # Добавление пунктов в меню "Файл"
        import_probs_action = QAction("Импортировать алфавит и вероятности", self)
        import_sequence_action = QAction("Импортировать последовательностей", self)
        self.export_answer_action = QAction("Экспортировать ответ", self)
        self.export_answer_action.setDisabled(True)  # Изначально кнопка экспорта отключена

        # Присваиваем действия пунктам меню
        import_probs_action.triggered.connect(self.import_probabilities)
        self.export_answer_action.triggered.connect(self.export_answer)
        import_sequence_action.triggered.connect(self.import_sequence)

        # Добавляем пункты в меню "Файл"
        file_menu.addAction(import_probs_action)
        file_menu.addAction(import_sequence_action)
        file_menu.addSeparator()  # Разделитель
        file_menu.addAction(self.export_answer_action)

        # Создание меню "О программе"
        about_menu = menubar.addMenu("О программе")
        about_action = QAction("*клик*", self)
        about_menu.addAction(about_action)

        # Подключаем окно "О программе"
        about_action.triggered.connect(self.show_about_window)

    def decode(self):
        # Процедура декодирования последовательности
        try:
            text = self.encoded_sequence_input.text()  # Получаем текст из поля ввода
            decoded_message = self.encoder.decode(text)  # Декодируем текст
            # Обновляем поле с информацией о процессе декодирования
            self.additional_info_field.setText(prepare_additional_text(self.encoder, text, decoded_message))
            self.sequence_input.setText(decoded_message)  # Выводим декодированное сообщение
        except Exception as e:
            # Отображаем сообщение об ошибке
            QMessageBox.critical(self, "Ошибка декодирования!", f"Во время декодирования произошла ошибка '{e}'")

    def encode(self):
        # Процедура кодирования последовательности
        try:
            text = self.sequence_input.text()  # Получаем текст из поля ввода
            encoded_message = self.encoder.encode(text)  # Кодируем текст
            # Обновляем поле с информацией о процессе кодирования
            self.additional_info_field.setText(prepare_additional_text(self.encoder, text, encoded_message))
            self.encoded_sequence_input.setText(encoded_message)  # Выводим закодированное сообщение
        except Exception as e:
            # Отображаем сообщение об ошибке
            QMessageBox.critical(self, "Ошибка кодирования!", f"Во время кодирования произошла ошибка '{e}'")

    @property
    def encoder(self):
        return self.tab_widget.currentWidget().encoder

    def update_encoder(self):
        try:
            self.tab_widget.currentWidget().update_encoder(self.probabilities)
            regex_pattern = f"^[{''.join(map(re.escape, self.encoder.output_alphabet))}]+;"
            regexp = QtCore.QRegExp(regex_pattern)
            validator = QtGui.QRegExpValidator(regexp)
            self.encoded_sequence_input.setValidator(validator)
            self.additional_info_field.setText(str(self.encoder))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка смены алгоритма!", f"Во время смены алгоритма произошла ошибка '{e}'")

    def import_probabilities(self):
        # Импорт вероятностей символов из файла
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите файл с вероятностями", "",
                                                   "Text Files (*.csv)")
        if file_name:
            try:
                with open(file_name, mode="r") as file:  # Открываем файл
                    reader = csv.reader(file, delimiter=';')  # Читаем CSV файл
                    for row in reader:
                        symbol, prob = row  # Считываем символ и его вероятность
                        self.probabilities[symbol] = prob  # Добавляем в словарь вероятностей
                self.statusBar().showMessage(f"Вероятности успешно импортированы из {file_name}.")  # Обновляем статус
                # Активируем ввод и кнопки после успешного импорта
                self.sequence_input.setDisabled(False)
                self.encoded_sequence_input.setDisabled(False)
                self.encode_button.setDisabled(False)
                self.decode_button.setDisabled(False)
                self.export_answer_action.setDisabled(False)

                # Обновляем валидатор для последовательности на основе импортированных символов
                regex_pattern = f"^[{''.join(map(re.escape, self.probabilities.keys()))}]+;"
                regexp = QtCore.QRegExp(regex_pattern)
                validator = QtGui.QRegExpValidator(regexp)
                self.sequence_input.setValidator(validator)

                # Создаем новый объект кодировщика на основе импортированных вероятностей
                self.update_encoder()
                # Обновляем поле дополнительной информации
                self.additional_info_field.setText(prepare_additional_text(self.encoder))
            except Exception as e:
                # Отображаем сообщение об ошибке
                QMessageBox.critical(self, "Ошибка импорта!", f"Во время импорта произошла ошибка '{e}'")

    def import_sequence(self):
        # Импорт последовательности из файла
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите файл c последовательностью", "",
                                                   "Text Files (*.txt)")
        if file_name:
            try:
                with open(file_name, mode="r") as file:
                    self.sequence_input.setText(file.readline().strip())  # Считываем строку из файла
                self.statusBar().showMessage(
                    f"Последовательность успешно импортирована из {file_name}.")  # Обновляем статус
            except Exception as e:
                # Отображаем сообщение об ошибке
                QMessageBox.critical(self, "Ошибка импорта!", f"Во время импорта произошла ошибка '{e}'")

    def export_answer(self):
        # Экспорт закодированного/декодированного сообщения в файл
        file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить ответ", "", "Text Files (*.txt)")
        if file_name:
            try:
                with open(file_name, mode="w", encoding="utf-8") as file:
                    print(self.additional_info_field.toPlainText(), file=file)  # Сохраняем текст
                self.statusBar().showMessage(f"Ответ успешно экспортирован в {file_name}.")  # Обновляем статус
            except Exception as e:
                # Отображаем сообщение об ошибке
                QMessageBox.critical(self, "Ошибка импорта!", f"Во время импорта произошла ошибка '{e}'")

    def show_about_window(self):
        # Открытие окна "О программе"
        self.about_window = AboutWindow()
        self.about_window.show()  # Показываем окно
