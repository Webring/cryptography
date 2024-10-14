from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from algorithms.GilbertMooreEncoder import GilbertMooreEncoder


class GilbertMooreTab(QWidget):
    ENCODER = GilbertMooreEncoder
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("У данного алгоритма нет настроек", self)

        layout.addWidget(label)
        self.setLayout(layout)