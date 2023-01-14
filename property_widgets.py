from base_ui import QRedFrame,QRedSpinBox,QPlainTextEdit
from PySide6.QtWidgets import QHBoxLayout,QSizePolicy

class IntPropertyWidget(QRedFrame):
    def __init__(self,property):
        super().__init__(None)
        self.theproperty = property
        #self.widgets = QHBoxLayout()
        self.spinbox = QRedSpinBox(self,self.updateproperty)
        self.spinbox.setValue(self.theproperty._val)
        #self.widgets.addWidget(self.textbox)
        #self.setLayout(self.widgets)
        self.setStyleSheet("border-width:0px;")
    def updateproperty(self, value):
        self.theproperty._val = value
    def updateself(self):
        self.spinbox.setValue(self.theproperty._val)

class StringPropertyWidget(QRedFrame):
    def __init__(self,property):
        super().__init__(None)
        self.theproperty = property
        self.widgets = QHBoxLayout()
        self.textbox = QPlainTextEdit(self)
        self.textbox.textChanged.connect(self.updateproperty)
        self.textbox.setPlainText(self.theproperty._val)
        #self.setFixedHeight(self.textbox.sizeHint().height())
        #self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.widgets.addWidget(self.textbox)
        self.setLayout(self.widgets)
        self.setStyleSheet("border-image:url(editor/Text Box.png) 2; border-width:2;")
    def updateproperty(self):
        self.theproperty._val = self.textbox.toPlainText()
    def updateself(self):
        self.textbox.setPlainText(self.theproperty._val)