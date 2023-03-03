import PySide6
from PySide6.QtWidgets import QMainWindow, QPushButton

class CodeEditWindow(QMainWindow):
    def __init__(self, property, parent) -> None:
        super().__init__(parent)

        # So that the window stays on top.
        self.setWindowFlag(PySide6.QtCore.Qt.WindowStaysOnTopHint)

        # TODO: Add code input.
        # TODO: Save to value upon exit and run property update method.