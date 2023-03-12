from PySide6.QtGui import QTextOption, QColor, QPaintEvent, QPainter, QPen, QPalette
from PySide6.QtCore import QRect
from PySide6.QtWidgets import (QComboBox, QDoubleSpinBox, QFrame, QLineEdit,
                               QPlainTextEdit, QPushButton, QScrollArea,
                               QSizePolicy, QSpinBox, QToolButton, QGroupBox,
                               QColorDialog, QDialogButtonBox, QHBoxLayout,
                               QVBoxLayout, QSlider, QWidget)

from czeditor.util import dummyfunction

from typing import List

class QRedButton(QToolButton):

    def __init__(self, parent, text, onpress=dummyfunction, *args, **kwargs):
        super().__init__(parent)
        self.setText(text)
        self.pressedfunction = onpress
        self.pressed.connect(self.pressedevent)
        self.args = args
        self.kwargs = kwargs
        self.setFixedHeight(24)
        self.setBaseSize(24, 24)
        self.setStyleSheet(
            """
        QToolButton { border-image:url(editor:Button.png) 3; border-width: 3; color: rgb(255,192,192);}
        QToolButton:hover {border-image:url(editor:Button Highlighted.png) 3; border-width: 3; color: rgb(255,192,192);}
        QToolButton:pressed {border-image:url(editor:Button Pressed.png) 3; border-width: 3;}
        """
        )

    def pressedevent(self):
        self.pressedfunction(*self.args, **self.kwargs)

    def __del__(self):
        self.pressedfunction = None


class QRedExpandableButton(QPushButton):
    def __init__(self, parent, text, onpress=dummyfunction, *args, **kwargs):
        super().__init__(parent)
        self.state = 0
        self.setText(text)
        self.pressedfunction = onpress
        self.pressed.connect(self.pressedevent)
        self.setFixedHeight(24)
        self.setSizePolicy(QSizePolicy.Policy.Preferred,
                           QSizePolicy.Policy.Preferred)
        self.setStyleSheet(
            """
            QPushButton { border-image:url(editor:Button.png) 3; border-width: 3; color: rgb(255,192,192);}
            QPushButton:hover {border-image:url(editor:Button Highlighted.png) 3; border-width: 3; color: rgb(255,192,192);}
            QPushButton:pressed {border-image:url(editor:Button Pressed.png) 3; border-width: 3;}
        """
        )
        self.args = args
        self.kwargs = kwargs

    def pressedevent(self):
        self.pressedfunction(*self.args, **self.kwargs)


class QRedFrame(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet(
            "border-image:url(editor:Square Frame.png) 2; border-width:2;")


class QRedGroupBox(QGroupBox):
    def __init__(self, text, parent):
        super().__init__(text, parent)
        self.setContentsMargins(2, 16, 2, 2)
        self.setStyleSheet(
            "border-image:url(editor:Square Frame.png) 2; border-width:2;")

class QRedScrollArea(QScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet(
            "border-image:url(editor:Square Frame.png) 2; border-width:2;")


class QRedTextBox(QPlainTextEdit):
    def __init__(self, parent, onchange=dummyfunction):
        super().__init__(parent)
        self.onchange = onchange
        self.setStyleSheet(
            "border-image:url(editor:Text Box.png) 2; border-width:2;")
        self.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        # self.setMaximumHeight(150)
        self.textChanged.connect(self.change)

    def change(self) -> None:
        self.onchange(self.toPlainText())


class QRedTextEntry(QLineEdit):
    def __init__(self, parent, onchange=dummyfunction):
        super().__init__(parent)
        self.onchange = onchange
        self.setStyleSheet(
            "border-image:url(editor:Text Box.png) 2; border-width:2;")
        # self.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        # self.setMaximumHeight(150)
        self.textChanged.connect(self.change)

    def change(self) -> None:
        self.onchange(self.text())


class QRedSpinBox(QSpinBox):
    def __init__(self, parent, onchange=dummyfunction):
        super().__init__(parent)
        self.onchange = onchange
        self.setStyleSheet(
            "border-image:url(editor:Text Box.png) 2; border-width:2;")
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
    def __init__(self, parent, onchange=dummyfunction):
        super().__init__(parent)
        self.onchange = onchange
        self.setStyleSheet(
            "border-image:url(editor:Text Box.png) 2; border-width:2;")
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
    def __init__(self, parent, elements=[], onchange=dummyfunction):
        super().__init__(parent)
        self.onchange = onchange
        # styl = QApplication.style()
        # p = styl.standardIcon(QStyle.SP_ArrowDown)
        # p.pixmap(16,16).save("arrow.png")
        # self.setStyleSheet("border-image:url(editor/Text Box.png) 2; border-width:2;")
        self.setStyleSheet(
            """
            QComboBox { background:none; border-image:url(editor:Text Box.png); border-width:2;}
            QComboBox::drop-down { border-image:url(editor:Button.png); border-width:3; }
            QComboBox::down-arrow { image: url(editor:Arrow Down.png); }
        """
        )
        self.addItems(elements)
        self.currentIndexChanged.connect(self.valuechanged)

    def valuechanged(self, index) -> None:
        self.onchange(self.currentText(), self.currentIndex())


class QRedColorPicker(QPushButton):
    def __init__(self, parent=None, onchange=dummyfunction):
        super().__init__(parent)
        self.onchange = onchange
        self.pressed.connect(self.pressedEvent)
        self.currentColor = QColor(255, 0, 0, 255)
        self.setStyleSheet(
            """
            
            QColorDialog {
                background-color: qradialgradient(spread:pad, cx:4.5, cy:4.5, radius:7, fx:4.5, fy:4.5, stop:0 rgba(255, 0, 0, 255), stop:1 rgba(0, 0, 0, 255)); 
            }
            QFrame { 
                border-image:url(editor:Square Frame.png) 2; 
                border-width:2; 
                background-color: qradialgradient(spread:pad, cx:4.5, cy:4.5, radius:7, fx:4.5, fy:4.5, stop:0 rgba(255, 0, 0, 255), stop:1 rgba(0, 0, 0, 255)); 
            }
            QPushButton { 
                border-image:url(editor:Button.png) 3; 
                border-width: 3; 
                color: rgb(255,192,192);
            }
            QPushButton:hover {
                border-image:url(editor:Button Highlighted.png) 3; 
                border-width: 3; 
                color: rgb(255,192,192);
            }
            QPushButton:pressed {
                border-image:url(editor:Button Pressed.png) 3; 
                border-width: 3;
            }
            QSpinBox {
                border-image:url(editor:Text Box.png) 2;
                border-width:2;
            }
            QSpinBox::up-button {
                border-image:url(editor:Button.png) 3; 
                border-width: 3; 
                color: rgb(255,192,192);
                image: url(editor:Arrow Up.png);
            }
            QSpinBox::up-button:hover {
                border-image:url(editor:Button Highlighted.png) 3; 
                border-width: 3; 
                color: rgb(255,192,192);
            }
            QSpinBox::up-button:pressed {
                border-image:url(editor:Button Pressed.png) 3; 
                border-width: 3;
            }
            QSpinBox::down-button {
                border-image:url(editor:Button.png) 3; 
                border-width: 3; 
                color: rgb(255,192,192);
                image: url(editor:Arrow Down.png);
            }
            QSpinBox::down-button:hover {
                border-image:url(editor:Button Highlighted.png) 3; 
                border-width: 3; 
                color: rgb(255,192,192);
            }
            QSpinBox::down-button:pressed {
                border-image:url(editor:Button Pressed.png) 3; 
                border-width: 3;
            }
            QLineEdit {
                border-image:url(editor:Text Box.png) 2;
                border-width:2;
            }
            QDialogButtonBox {
                border-image:url(editor:Text Box.png) 2;
                border-width:2;
            }
            """)
        self.dialog = None
        self.originalclose = None

    def pressedEvent(self):
        if self.dialog:
            return
        dialog = QColorDialog(self.currentColor, self)
        dialog.currentColorChanged.connect(self.pickColor)
        dialog.finished.connect(self.done)
        dialog.setOptions(QColorDialog.ColorDialogOption.ShowAlphaChannel)
        self.dialog = dialog
        dialog.show()
        dialogButtonBox: QDialogButtonBox = dialog.findChild(QDialogButtonBox)
        buttons: List[QPushButton] = dialogButtonBox.findChildren(QPushButton)
        layout: QHBoxLayout = dialogButtonBox.findChild(QHBoxLayout)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        for button in buttons:
            button.setSizePolicy(QSizePolicy.Policy.Preferred,
                                 QSizePolicy.Policy.MinimumExpanding)
            button.setFixedSize(button.size().width()+8,
                                button.size().height()+4)
        dialog.findChildren(QWidget)[8].setStyleSheet(
            """background: transparent;
        border-image:url(editor:Square Frame.png) 2; 
        border-width:2;""")
        p: QWidget = dialog.findChildren(QWidget)[8]
        palette = p.palette()
        palette.setColor(QPalette.ColorGroup.All,
                         QPalette.ColorRole.Light, QColor(127, 0, 0))
        palette.setColor(QPalette.ColorGroup.All,
                         QPalette.ColorRole.Dark, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorGroup.All,
                         QPalette.ColorRole.Mid, QColor(64, 0, 0))
        p.setPalette(palette)

    def pickColor(self, color: QColor):
        self.currentColor = color
        self.onchange(color)

    def done(self):
        self.dialog = None
        

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        rect = self.rect()
        painter.setPen(QPen(QColor(0, 0, 0), 0))
        painter.setBrush(QColor(127, 0, 0))
        painter.drawRect(rect)
        painter.setPen(QPen(QColor(127, 0, 0), 0))
        painter.setBrush(self.currentColor)
        painter.drawRect(QRect(rect.left()+1, rect.top()+1,
                         rect.width()-2, rect.height()-2))
