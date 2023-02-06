from PySide6.QtWidgets import QToolButton,QPushButton,QSpinBox,QSizePolicy,QFrame,QPlainTextEdit,QLineEdit,QScrollArea,QComboBox,QDoubleSpinBox
from PySide6.QtGui import QTextOption
from util import dummyfunction

class QRedButton(QToolButton):

    def __init__(self,parent,text,onpress = dummyfunction,*args,**kwargs):
        super().__init__(parent)
        self.setText(text)
        self.pressedfunction = onpress
        self.pressed.connect(self.pressedevent)
        self.args = args
        self.kwargs = kwargs
        self.setFixedHeight(24)
        self.setBaseSize(24,24)
        self.setStyleSheet("QToolButton { border-image:url(editor/Button.png) 3; border-width: 3; color: rgb(255,192,192);} QToolButton:hover {border-image:url(editor/Button Highlighted.png) 3; border-width: 3; color: rgb(255,192,192);} QToolButton:pressed {border-image:url(editor/Button Pressed.png) 3; border-width: 3;}")
    def pressedevent(self):
        self.pressedfunction(*self.args,**self.kwargs)
    def __del__(self):
        self.pressedfunction = None

class QRedExpandableButton(QPushButton):
    def __init__(self,parent,text,onpress = dummyfunction,*args,**kwargs):
        super().__init__(parent)
        self.state = 0
        self.setText(text)
        self.pressedfunction = onpress
        self.pressed.connect(self.pressedevent)
        self.setFixedHeight(24)
        self.setSizePolicy(QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Preferred)
        self.setStyleSheet("QPushButton { border-image:url(editor/Button.png) 3; border-width: 3; color: rgb(255,192,192);} QPushButton:hover {border-image:url(editor/Button Highlighted.png) 3; border-width: 3; color: rgb(255,192,192);} QPushButton:pressed {border-image:url(editor/Button Pressed.png) 3; border-width: 3;}")
        self.args = args
        self.kwargs = kwargs
    def pressedevent(self):
        self.pressedfunction(*self.args,**self.kwargs)
class QRedFrame(QFrame):
    def __init__(self,parent):
        super().__init__(parent)
        self.setStyleSheet("border-image:url(editor/Square Frame.png) 2; border-width:2;")

class QRedScrollArea(QScrollArea):
    def __init__(self,parent):
        super().__init__(parent)
        self.setStyleSheet("border-image:url(editor/Square Frame.png) 2; border-width:2;")

class QRedTextBox(QPlainTextEdit):
    def __init__(self,parent,onchange=dummyfunction):
        super().__init__(parent)
        self.onchange = onchange
        self.setStyleSheet("border-image:url(editor/Text Box.png) 2; border-width:2;")
        self.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        #self.setMaximumHeight(150)
        self.textChanged.connect(self.change)
    def change(self) -> None:
        self.onchange(self.toPlainText())

class QRedTextEntry(QLineEdit):
    def __init__(self,parent,onchange=dummyfunction):
        super().__init__(parent)
        self.onchange = onchange
        self.setStyleSheet("border-image:url(editor/Text Box.png) 2; border-width:2;")
        #self.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        #self.setMaximumHeight(150)
        self.textChanged.connect(self.change)
    def change(self) -> None:
        self.onchange(self.text())   
class QRedSpinBox(QSpinBox):
    def __init__(self,parent,onchange=dummyfunction):
        super().__init__(parent)
        self.onchange = onchange
        self.setStyleSheet("border-image:url(editor/Text Box.png) 2; border-width:2;")
        self.setMaximum(50000)
        self.setMinimum(-50000)
        self.valueChanged.connect(self.change)
    def change(self) -> None:
        self.onchange(self.value()) 
    def setValueBypass(self, value):
        self.blockSignals(True)
        self.setValue(value)
        self.blockSignals(False)
class QRedDecimalSpinBox(QDoubleSpinBox):
    def __init__(self,parent,onchange=dummyfunction):
        super().__init__(parent)
        self.onchange = onchange
        self.setStyleSheet("border-image:url(editor/Text Box.png) 2; border-width:2;")
        self.setMaximum(50000)
        self.setMinimum(-50000)
        self.setDecimals(3)
        self.valueChanged.connect(self.change)
    def change(self) -> None:
        self.onchange(self.value()) 
    def setValueBypass(self, value):
        self.blockSignals(True)
        self.setValue(value)
        self.blockSignals(False)
class QRedComboBox(QComboBox):
    def __init__(self,parent,elements=[],onchange=dummyfunction):
        super().__init__(parent)
        self.onchange = onchange
        #styl = QApplication.style()
        #p = styl.standardIcon(QStyle.SP_ArrowDown)
        #p.pixmap(16,16).save("arrow.png")
        #self.setStyleSheet("border-image:url(editor/Text Box.png) 2; border-width:2;")
        self.setStyleSheet("QComboBox { background:none; border-image:url(editor/Text Box.png); border-width:2;} QComboBox::drop-down { border-image:url(editor/Button.png); border-width:3; } QComboBox::down-arrow { image: url(editor/Arrow Down.png); }")
        self.addItems(elements)
        self.currentIndexChanged.connect(self.valuechanged)
    def valuechanged(self,index) -> None:
        self.onchange(self.currentText(),self.currentIndex()) 