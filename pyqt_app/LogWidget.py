import sys
import logging
from PyQt6.QtWidgets import QMainWindow, QTextEdit, QMenuBar, QApplication, QPlainTextEdit
from PyQt6.QtCore import QObject
from PyQt6.QtCore import pyqtSignal, pyqtBoundSignal

class QTextEditLogger(logging.Handler, QObject):
    appendPlainText: pyqtBoundSignal = pyqtSignal(str) # инициализация сигнала вместо дефолтного

    def __init__(self, parent):
        super().__init__()
        QObject.__init__(self)
        self.widget = QPlainTextEdit(parent)  # создание виджета пустого окна
        self.widget.setReadOnly(True)
        self.appendPlainText.connect(self.widget.appendPlainText)  #  вызов функции, которая добавляет текст в пустой виджет.

    def emit(self, record):
        msg = self.format(record)
        self.appendPlainText.emit(msg)  # добавление в сигнал строки, которая передается в исполняемую функцию