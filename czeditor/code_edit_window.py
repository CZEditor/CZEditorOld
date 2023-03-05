import PySide6
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from czeditor.base_ui import QRedTextBox
from czeditor.properties import OpenWindowButtonProperty

class CodeEditWindow(QMainWindow):
    def __init__(self, property:OpenWindowButtonProperty, parent) -> None:
        super().__init__(parent)
        self.the_property = property

        # So that the window stays on top.
        self.setWindowFlag(PySide6.QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle(property.btn_name)

        # Text Box
        # ----------
        layout = QVBoxLayout() # Using layout here as I will add more widgets here in the future.

        self.text_box = QRedTextBox(self)
        self.text_box.textChanged.connect(self.updateproperty)
        self.text_box.setPlainText(self.the_property._val)

        layout.addWidget(self.text_box)
        

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.setStyleSheet("border-width:0px;")

    def updateproperty(self):
        self.the_property._val = self.text_box.toPlainText()

    def updateself(self):
        self.text_box.setPlainText(self.the_property._val)