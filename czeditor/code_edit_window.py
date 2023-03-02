import PySide6
from PySide6.QtWidgets import QMainWindow, QPushButton

class CodeEditWindow(QMainWindow):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        # So that the window stays on top.
        self.setWindowFlag(PySide6.QtCore.Qt.WindowStaysOnTopHint)

        self.button = QPushButton(text="owo", parent=self)