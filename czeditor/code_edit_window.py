import PySide6
from PySide6.QtWidgets import QMainWindow, QPushButton

from czeditor.property_widgets import StringPropertyWidget

class CodeEditWindow(QMainWindow):
    def __init__(self, property, parent) -> None:
        super().__init__(parent)

        # So that the window stays on top.
        self.setWindowFlag(PySide6.QtCore.Qt.WindowStaysOnTopHint)

        self.code_input = StringPropertyWidget(property, self)