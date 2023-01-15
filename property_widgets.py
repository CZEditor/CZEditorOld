from base_ui import QRedFrame,QRedSpinBox,QRedTextBox,QRedButton
from PySide6.QtWidgets import QHBoxLayout,QSizePolicy,QFileDialog

class IntPropertyWidget(QRedFrame):
    def __init__(self,property):
        super().__init__(None)
        self.theproperty = property
        self.widgets = QHBoxLayout()
        self.spinbox = QRedSpinBox(self,self.updateproperty)
        self.spinbox.setValue(self.theproperty._val)
        self.widgets.addWidget(self.spinbox)
        self.setLayout(self.widgets)
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
        self.textbox = QRedTextBox(self)
        self.textbox.textChanged.connect(self.updateproperty)
        self.textbox.setPlainText(self.theproperty._val)
        #self.setFixedHeight(self.textbox.sizeHint().height())
        #self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.widgets.addWidget(self.textbox)
        self.setLayout(self.widgets)
        #self.setStyleSheet("border-image:url(editor/Square Frame.png) 2; border-width:2;")
        self.setStyleSheet("border-width:0px;")
    def updateproperty(self):
        self.theproperty._val = self.textbox.toPlainText()
    def updateself(self):
        self.textbox.setPlainText(self.theproperty._val)

class FilePropertyWidget(QRedFrame):
    def __init__(self,property):
        super().__init__(None)
        self.theproperty = property
        self.widgets = QHBoxLayout()
        self.textbox = QRedTextBox(self)
        self.textbox.textChanged.connect(self.updateproperty)
        self.textbox.setPlainText(self.theproperty._val)
        self.button = QRedButton(self,"Browse...",self.browse)

        #self.setFixedHeight(self.textbox.sizeHint().height())
        #self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.widgets.addWidget(self.textbox)
        self.widgets.addWidget(self.button)
        self.setLayout(self.widgets)
        #self.setStyleSheet("border-image:url(editor/Square Frame.png) 2; border-width:2;")
        self.setStyleSheet("border-width:0px;")
    def updateproperty(self):
        self.theproperty._val = self.textbox.toPlainText()
    def updateself(self):
        self.textbox.setPlainText(self.theproperty._val)
    def browse(self):
        self.textbox.setPlainText(QFileDialog.getOpenFileUrl(self,"Open File")[0].path()[1:])
