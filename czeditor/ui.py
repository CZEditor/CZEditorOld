from PySide6.QtCore import QLine, QMimeData, QPoint, QRectF, QSize, Qt
from PySide6.QtGui import (QColor, QDrag, QDragEnterEvent, QDragMoveEvent,
                           QDropEvent, QFont, QKeyEvent, QMouseEvent, QPainter,
                           QPen, QRadialGradient, QResizeEvent, QWheelEvent,
                           QLinearGradient, QPainterPath)
from PySide6.QtWidgets import (QFormLayout, QGraphicsItem, QGraphicsScene,
                               QGraphicsView, QGridLayout, QSizePolicy,
                               QWidget, QGraphicsItemGroup, QGraphicsSceneMouseEvent,
                               QGraphicsSceneHoverEvent)

from czeditor.base_ui import *
from czeditor.effectfunctions import *
from czeditor.generate import *
from czeditor.sourcefunctions import *
from czeditor.keyframes import *
from czeditor.actionfunctions import *
from czeditor.util import *
from czeditor.animation_keyframes import *
from czeditor.util.params_operations import *

from typing import Union

playbackframe = 100


class QRedSelectableProperty(QRedFrame):
    def __init__(self, parent, param: Selectable, parentclass, override=None):
        super().__init__(parent)
        self.parentclass = parentclass
        if override == None:
            override = self.updateproperty
        self.param = param
        self.widgets = QHBoxLayout()
        self.combobox = QRedComboBox(self, self.param.names)
        self.combobox.setCurrentIndex(self.param.index)
        self.combobox.onchange = override
        self.widgets.addWidget(self.combobox)

        self.setLayout(self.widgets)
        self.setStyleSheet("border-width:0px;")

    def updateproperty(self, name, index):
        # print("setting:",value)
        self.param.index = index
        self.parentclass.updateviewport()

    def updateself(self):
        self.combobox.onchange = dummyfunction
        self.combobox.setCurrentIndex(self.param.index)
        self.combobox.onchange = self.updateproperty


class QRedTextEntryListProperty(QRedFrame):
    def __init__(self, parent, param: Params, index, parentclass):
        super().__init__(parent)
        self.param = param
        self.widgets = QHBoxLayout()
        self.index = index
        self.textbox = QRedTextEntry(self, self.updateproperty)
        self.textbox.setText(param[index])
        self.widgets.addWidget(self.textbox)
        self.setLayout(self.widgets)
        self.setStyleSheet("border-width:0px;")
        self.parentclass = self.parentclass

    def updateproperty(self, value: str):
        # print("setting:",value)
        self.param[self.index] = value
        self.parentclass.updateviewport()

    def updateself(self):
        self.textbox.onchange = dummyfunction
        self.textbox.setText(self.param[self.index])
        self.textbox.onchange = self.updateproperty
        self.parentclass.updateviewport()


class QRedTextListProperty(QRedFrame):
    def __init__(self, parent, thelist, parentclass):
        super().__init__(parent)
        self.parentclass = parentclass
        self.whole = QVBoxLayout(self)
        self.collapseButton = QRedExpandableButton(
            None, "expand", self.collapse)
        self.collapseButton.sizePolicy().setHorizontalPolicy(
            QSizePolicy.Policy.MinimumExpanding)
        self.collapseButton.setMinimumWidth(60)
        self.mainView = QRedFrame(self)
        self.withbuttons = QGridLayout()
        self.widgets = QFormLayout()
        self.thelist = thelist
        self.entries = []
        self.widgetbuttons = QGridLayout()
        for i in range(len(self.thelist)):
            self.entries.append(
                QRedTextEntryListProperty(None, self.thelist, i))
            arow = QHBoxLayout()
            arow.addWidget(self.entries[i])
            arow.addWidget(QRedButton(
                None, "/\\", 0, 0, self.moveup, False, arow))
            arow.addWidget(QRedButton(None, "\\/", 0, 0,
                           self.movedown, False, arow))
            arow.addWidget(QRedButton(
                None, "-", 0, 0, self.remove, False, arow))
            self.widgets.addRow("", arow)
        self.withbuttons.addLayout(self.widgets, 0, 0)
        self.withbuttons.addLayout(self.widgetbuttons, 0, 1)
        self.withbuttons.addWidget(
            QRedExpandableButton(None, "+", self.add), 1, 0)
        self.mainView.setLayout(self.withbuttons)
        self.mainView.sizePolicy().setVerticalPolicy(QSizePolicy.Policy.Minimum)
        self.mainView.sizePolicy().setHorizontalPolicy(
            QSizePolicy.Policy.MinimumExpanding)
        self.whole.addWidget(self.collapseButton)
        self.whole.addWidget(self.mainView)
        # self.whole.addWidget(QRedExpandableButton(None,"+",self.add))
        self.setLayout(self.whole)
        self.collapsed = False
        self.whole.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.whole.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        # print(self.mainView.maximumHeight())
        # self.setMaximumHeight(200)
        self.mainView.setStyleSheet("border-width:0px; background:none;")

    def collapse(self):
        if self.collapsed:
            self.mainView.setMaximumHeight(9999)
            self.collapsed = False
        else:
            self.mainView.setMaximumHeight(0)
            self.collapsed = True

    def moveup(self, arow):
        index = self.widgets.getLayoutPosition(arow)[0]
        if index == 0:
            return
        self.thelist[index], self.thelist[index -
                                          1] = self.thelist[index-1], self.thelist[index]
        self.entries[index].updatetextbox()
        self.entries[index-1].updatetextbox()
        self.parentclass.updateviewport()

    def movedown(self, arow):
        index = self.widgets.getLayoutPosition(arow)[0]
        if index == len(self.thelist)-1:
            return
        self.thelist[index], self.thelist[index +
                                          1] = self.thelist[index+1], self.thelist[index]
        self.entries[index].updatetextbox()
        self.entries[index+1].updatetextbox()
        self.parentclass.updateviewport()

    def remove(self, arow):
        # no idea why it has to be [0]. it returns a tuple that looks like this (4, <ItemRole.FieldRole: 1>)
        index = self.widgets.getLayoutPosition(arow)[0]
        self.thelist.pop(index)
        self.widgets.removeRow(index)
        self.entries.pop(index)
        self.parentclass.updateviewport()

    def add(self):
        self.thelist.append("")
        i = len(self.thelist)-1
        self.entries.append(QRedTextEntryListProperty(None, self.thelist, i))
        arow = QHBoxLayout()
        arow.addWidget(self.entries[i])
        arow.addWidget(QRedButton(None, "/\\", 0, 0, self.moveup, False, arow))
        arow.addWidget(QRedButton(None, "\\/", 0, 0,
                       self.movedown, False, arow))
        arow.addWidget(QRedButton(None, "-", 0, 0, self.remove, False, arow))
        self.widgets.addRow("button", arow)
        self.parentclass.updateviewport()


class QRedDropDownFrame(QRedFrame):
    def __init__(self, parent, name):
        super().__init__(parent)

        self.whole = QVBoxLayout(self)
        self.collapseButton = QRedExpandableButton(None, name, self.collapse)
        self.mainView = QRedFrame(self)
        self.widgets = QFormLayout(self.mainView)

        self.mainView.setLayout(self.widgets)
        self.mainView.sizePolicy().setVerticalPolicy(QSizePolicy.Policy.Minimum)
        self.mainView.sizePolicy().setHorizontalPolicy(QSizePolicy.Policy.Preferred)
        self.whole.addWidget(self.collapseButton)
        self.whole.addWidget(self.mainView)
        self.setLayout(self.whole)
        self.collapsed = False
        self.whole.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.whole.setSizeConstraint(
            QVBoxLayout.SizeConstraint.SetNoConstraint)
        # print(self.mainView.maximumHeight())
        # self.setMaximumHeight(200)
        self.mainView.setStyleSheet("border-width:0px; background:none;")

    def collapse(self):
        if self.collapsed:
            self.mainView.setMaximumHeight(9999)
            self.collapsed = False
        else:
            self.mainView.setMaximumHeight(0)
            self.collapsed = True


class CzeKeyframeOptionCategory(QRedDropDownFrame):
    def __init__(self, parent, name: str, params: Params, parentclass):
        super().__init__(parent, name)
        self.parentclass = parentclass
        self.params = params
        if (params.function):
            self.whole.insertWidget(0, QRedSelectableProperty(
                None, params.function, self.parentclass, self.rebuild))
        self.iterate(self.params.params)
        self.parentclass.timeline.createKeyframeItem(
            self.parentclass.selectedframe, params)

    def rebuild(self, name, index):

        self.parentclass.timeline.deleteKeyframeItem(
            self.parentclass.selectedframe, self.params)
        self.params.function.index = index
        for i in range(self.widgets.rowCount()):
            self.widgets.removeRow(0)
        self.params.params = self.params.function().params.copy()
        if self.parentclass.selectedframe:
            paramsAssociateKeyframe(
                self.params.params, self.parentclass.selectedframe)
        if self.parentclass.selectedAnimationFrame:
            self.parentclass.triggerEvent("UpdateAnimationKeyframeTracks")
            self.parentclass.triggerEvent("UpdateAnimationKeyframe")
        self.iterate(self.params.params)
        self.parentclass.timeline.createKeyframeItem(
            self.parentclass.selectedframe, self.params)
        self.parentclass.updateviewport()

    def updateParam(self):
        for i in range(self.widgets.rowCount()):
            self.widgets.itemAt(i, QFormLayout.FieldRole).widget().updateself()

    def regenerate(self, params):
        if (params.function):
            toremove = self.whole.itemAt(0).widget()
            self.whole.removeItem(self.whole.itemAt(0))
            toremove.setParent(None)
            toremove.destroy()
            self.whole.insertWidget(0, QRedSelectableProperty(
                None, params.function, self.parentclass, self.rebuild))
        for i in range(self.widgets.rowCount()):
            self.widgets.removeRow(0)
        self.params = params
        if self.parentclass.selectedframe:
            paramsAssociateKeyframe(
                self.params.params, self.parentclass.selectedframe)
        if self.parentclass.selectedAnimationFrame:
            self.parentclass.triggerEvent("UpdateAnimationKeyframeTracks")
            self.parentclass.triggerEvent("UpdateAnimationKeyframe")
        self.iterate(self.params.params)
        self.parentclass.updateviewport()

    def iterate(self, params):
        for key in vars(params).keys():
            param = params[key]
            if (hasattr(param, "widget")):
                self.widgets.addRow(key, param.widget(self.parentclass))


class CzeKeyframeOptionCategoryList(QRedFrame):
    def __init__(self, parent, thelist, baseparam, parentclass):
        super().__init__(parent)
        self.parentclass = parentclass
        self.baseparam = baseparam
        self.whole = QVBoxLayout(self)
        self.whole.setSpacing(2)
        self.whole.setContentsMargins(2, 2, 2, 2)
        self.collapseButton = QRedExpandableButton(
            None, "expand", self.collapse)
        self.collapseButton.sizePolicy().setHorizontalPolicy(
            QSizePolicy.Policy.MinimumExpanding)
        self.collapseButton.setMinimumWidth(60)
        self.mainView = QRedFrame(self)
        self.withbuttons = QGridLayout()
        self.withbuttons.setSpacing(2)
        self.withbuttons.setContentsMargins(2, 2, 2, 2)
        self.widgets = QFormLayout()
        self.widgets.setSpacing(2)
        self.widgets.setContentsMargins(2, 2, 2, 2)
        self.thelist = thelist
        self.entries = []
        self.widgetbuttons = QGridLayout()
        for i in range(len(self.thelist)):
            self.entries.append(CzeKeyframeOptionCategory(
                None, "expand/collapse", self.thelist[i], parentclass))
            arow = QHBoxLayout()
            arow.addWidget(self.entries[i])
            buttons = QVBoxLayout()
            buttons.addWidget(QRedButton(None, "/\\", self.moveup, arow))
            buttons.addWidget(QRedButton(None, "\\/", self.movedown, arow))
            buttons.addWidget(QRedButton(None, "-", self.remove, arow))
            arow.addLayout(buttons)
            self.widgets.addRow("", arow)
        self.withbuttons.addLayout(self.widgets, 0, 0)
        self.withbuttons.addLayout(self.widgetbuttons, 0, 1)
        self.withbuttons.addWidget(
            QRedExpandableButton(None, "+", self.add), 1, 0)
        self.mainView.setLayout(self.withbuttons)
        self.mainView.sizePolicy().setVerticalPolicy(QSizePolicy.Policy.Minimum)
        self.mainView.sizePolicy().setHorizontalPolicy(QSizePolicy.Policy.Preferred)
        self.whole.addWidget(self.collapseButton)
        self.whole.addWidget(self.mainView)
        # self.whole.addWidget(QRedExpandableButton(None,"+",self.add))
        self.setLayout(self.whole)
        self.collapsed = False
        self.whole.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.whole.setSizeConstraint(
            QVBoxLayout.SizeConstraint.SetNoConstraint)
        # print(self.mainView.maximumHeight())
        # self.setMaximumHeight(200)
        self.mainView.setStyleSheet("border-width:0px; background:none;")

    def updateParam(self):
        for widget in self.entries:
            widget.updateParam()

    def regenerate(self, thelist, baseparam):
        self.baseparam = baseparam
        self.thelist = thelist
        i = 0

        for element in thelist:
            if (i >= len(self.entries)):
                self.entries.append(CzeKeyframeOptionCategory(
                    None, "expand/collapse", element, self.parentclass))
                arow = QHBoxLayout()
                arow.addWidget(self.entries[i])
                buttons = QVBoxLayout()
                buttons.addWidget(QRedButton(None, "/\\", self.moveup, arow))
                buttons.addWidget(QRedButton(None, "\\/", self.movedown, arow))
                buttons.addWidget(QRedButton(None, "-", self.remove, arow))
                arow.addLayout(buttons)
                self.widgets.addRow("", arow)
            else:
                self.entries[i].regenerate(element)
            i += 1

        initialLength = len(self.entries)

        if (len(thelist) < initialLength):
            while i < initialLength:
                self.widgets.removeRow(len(thelist))
                self.entries.pop(len(thelist))
                i += 1

    def collapse(self):
        if self.collapsed:
            self.mainView.setMaximumHeight(9999)
            self.collapsed = False
        else:
            self.mainView.setMaximumHeight(0)
            self.collapsed = True

    def moveup(self, arow):
        index = self.widgets.getLayoutPosition(arow)[0]
        if index == 0:
            return
        self.thelist[index], self.thelist[index -
                                          1] = self.thelist[index-1], self.thelist[index]
        self.entries[index].regenerate(self.thelist[index])
        self.entries[index-1].regenerate(self.thelist[index-1])
        self.parentclass.updateviewport()

    def movedown(self, arow):
        index = self.widgets.getLayoutPosition(arow)[0]
        if index == len(self.thelist)-1:
            return
        self.thelist[index], self.thelist[index +
                                          1] = self.thelist[index+1], self.thelist[index]
        self.entries[index].regenerate(self.thelist[index])
        self.entries[index+1].regenerate(self.thelist[index+1])
        self.entries[index].updatetextbox()
        self.entries[index+1].updatetextbox()
        self.parentclass.updateviewport()

    def remove(self, arow):
        # no idea why it has to be [0]. it returns a tuple that looks like this (4, <ItemRole.FieldRole: 1>)
        index = self.widgets.getLayoutPosition(arow)[0]
        self.thelist.pop(index)
        self.widgets.removeRow(index)
        self.entries.pop(index)
        self.parentclass.updateviewport()

    def add(self):

        self.thelist.append(self.baseparam.copy())
        i = len(self.thelist)-1
        self.entries.append(CzeKeyframeOptionCategory(
            None, "expand/collapse", self.thelist[i], self.parentclass))
        # print([self.thelist[i].params],[self.baseparam.params])
        arow = QHBoxLayout()
        arow.addWidget(self.entries[i])
        buttons = QVBoxLayout()
        buttons.addWidget(QRedButton(None, "/\\", self.moveup, arow))
        buttons.addWidget(QRedButton(None, "\\/", self.movedown, arow))
        buttons.addWidget(QRedButton(None, "-", self.remove, arow))
        arow.addLayout(buttons)
        self.widgets.addRow("button", arow)
        self.parentclass.updateviewport()


class CzeKeyframeOptions(QRedScrollArea):
    baseparams = Params({  # BAD!!! TODO : While we wont support anything else than sources, effects and actions, but we can still generalize this.
        "source": {
            "function": Selectable(0, sourcefunctionsdropdown),
            "params": Selectable(0, sourcefunctionsdropdown)().params.copy()
        },
        "actions": {
            "function": Selectable(0, actionfunctionsdropdown),
            "params": Selectable(0, actionfunctionsdropdown)().params.copy()
        },
        "effects": {
            "function": Selectable(0, effectfunctionsdropdown),
            "params": Selectable(0, effectfunctionsdropdown)().params.copy()
        }
    })

    def __init__(self, parent, parentclass):
        self.params = Params({})

        super().__init__(parent)

        self.parentclass = parentclass
        self.viewframe = QRedFrame(None)

        # self.whole = QVBoxLayout()

        # self.whole.addWidget(self.keyframeNameWidget)

        self.widgets = QVBoxLayout()
        self.widgets.setSpacing(2)
        self.widgets.setContentsMargins(2, 2, 2, 2)

        self.iterate(self.params)

        # self.whole.addLayout(self.widgets)

        self.viewframe.setLayout(self.widgets)

        self.widgets.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setWidget(self.viewframe)

        self.setSizePolicy(QSizePolicy.Policy.Maximum,
                           QSizePolicy.Policy.Expanding)

        self.setWidgetResizable(True)

    def sizeHint(self):
        return QSize(400, 720)

    """def changeEvent(self, arg__1) -> None:
        if(hasattr(self,"viewframe")):
            self.setMaximumWidth(self.viewframe.contentsRect().width()+self.verticalScrollBar().width())
        return super().changeEvent(arg__1)

    def resizeEvent(self, arg__1) -> None:
        if(hasattr(self,"viewframe")):
            self.setMaximumWidth(self.viewframe.contentsRect().width()+self.verticalScrollBar().width())
        return super().resizeEvent(arg__1)"""

    def iterate(self, params):
        for key in vars(params).keys():
            param = params[key]
            if isinstance(param, Params):
                self.widgets.addWidget(CzeKeyframeOptionCategory(
                    None, "Expand/Collapse", param, self.parentclass))  # Make it display the actual name!
            elif isinstance(param, list):
                self.widgets.addWidget(CzeKeyframeOptionCategoryList(
                    None, param, self.baseparams[key], self.parentclass))

    def iterateUpdate(self, params):
        i = 0
        for key in vars(params).keys():
            param = params[key]
            if isinstance(param, Params):
                self.widgets.itemAt(i).widget().updateParam()
            elif isinstance(param, list):
                self.widgets.itemAt(i).widget().updateParam()

            i += 1

    def iterateRegenerate(self, params):
        if (self.widgets.count() == 0):
            self.params = params
            self.rebuild(params)
            return
        i = 0
        for key in vars(params).keys():
            param = params[key]
            if isinstance(param, Params):
                self.widgets.itemAt(i).widget().regenerate(param)
            elif isinstance(param, list):
                self.widgets.itemAt(i).widget().regenerate(
                    param, self.baseparams[key])

            i += 1
        self.setMaximumWidth(self.viewframe.contentsRect(
        ).width()+self.verticalScrollBar().width())

    def rebuild(self, params=None):
        if params:
            self.params = params
            for i in range(self.widgets.count()):
                self.widgets.itemAt(0).widget().deleteLater()
                self.widgets.takeAt(0)
            self.iterate(self.params)
        elif self.parentclass.selectedframe:
            self.params = self.parentclass.selectedframe.params
            for i in range(self.widgets.count()):
                self.widgets.itemAt(0).widget().deleteLater()
                self.widgets.takeAt(0)
            self.iterate(self.params)
        else:
            for i in range(self.widgets.count()):
                self.widgets.itemAt(0).widget().deleteLater()
                self.widgets.takeAt(0)
        self.setMaximumWidth(self.viewframe.contentsRect(
        ).width()+self.verticalScrollBar().width())

    def update(self):
        if self.parentclass.selectedframe:
            self.params = self.parentclass.selectedframe.params
            self.iterateUpdate(self.params)
        else:
            for i in range(self.widgets.count()):
                self.widgets.itemAt(0).widget().deleteLater()
                self.widgets.takeAt(0)

    def regenerate(self, keyframe=None):
        if keyframe:
            self.params = keyframe.params
            self.iterateRegenerate(self.params)
        elif self.parentclass.selectedframe:
            self.params = self.parentclass.selectedframe.params
            self.iterateRegenerate(self.params)
        else:
            for i in range(self.widgets.count()):
                self.widgets.itemAt(0).widget().deleteLater()
                self.widgets.takeAt(0)
        self.setMaximumWidth(self.viewframe.contentsRect(
        ).width()+self.verticalScrollBar().width())


class QGraphicsViewEvent(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.onpress = dummyfunction
        self.onmove = dummyfunction
        self.onrelease = dummyfunction
        self.ondoubleclick = dummyfunction
        self.onscroll = dummyfunction
        self.dragenter = dummyfunction
        self.dragmove = dummyfunction
        self.dragdrop = dummyfunction
        self.setMouseTracking(True)
        self.previousmouse = QPoint(0, 0)

    def mousePressEvent(self, event) -> None:
        # print(event)
        self.onpress(event)
        self.previousmouse = event.pos()
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self.onrelease(event)
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.onmove(event, self.previousmouse)
        self.previousmouse = event.pos()
        return super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:

        self.ondoubleclick(event)
        self.previousmouse = event.pos()
        return super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event) -> None:
        self.onscroll(event)
        return super().wheelEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        self.dragenter(event)

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        self.dragmove(event)

    def dropEvent(self, event: QDropEvent) -> None:
        self.dragdrop(event)


class CzeTimelineKeyframeShape(QGraphicsItem):
    coolgradient = QRadialGradient(50, 50, 90)
    coolgradient.setColorAt(1, QColor(255, 255, 255))
    coolgradient.setColorAt(0, QColor(255, 0, 0))
    selectedcoolgradient = QRadialGradient(30, 30, 60)
    selectedcoolgradient.setColorAt(1, QColor(255, 127, 127))
    selectedcoolgradient.setColorAt(0, QColor(255, 0, 0))

    def __init__(self, keyframe):
        super().__init__()
        self.keyframe = keyframe
        self.currentBrush = self.coolgradient
        self.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)

    def boundingRect(self):
        return QRectF(-10, -10, 20, 20)

    def paint(self, painter: QPainter, option, widget) -> None:
        painter.setPen(QPen(QColor(0, 0, 0), 0))
        painter.setBrush(self.currentBrush)
        painter.drawPolygon(
            [QPoint(-10, 0), QPoint(0, -10), QPoint(10, 0), QPoint(0, 10)])

    def setBrush(self, brush):
        self.currentBrush = brush


class CzeTimelineKeyframeText(QGraphicsItem):

    def __init__(self, keyframe):
        super().__init__()
        self.keyframe = keyframe
        self.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)

    def boundingRect(self):
        return QRectF(-30, 10, 60, 32)

    def paint(self, painter: QPainter, option, widget) -> None:
        painter.setPen(QPen(QColor(255, 255, 255), 0))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(QRectF(-30, 10, 60, 32), self.keyframe.params.properties.params.name(),
                         Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)


class CzeTimelineKeyframeItem(QGraphicsItemGroup):
    coolgradient = QRadialGradient(50, 50, 90)
    coolgradient.setColorAt(1, QColor(255, 255, 255))
    coolgradient.setColorAt(0, QColor(255, 0, 0))
    selectedcoolgradient = QRadialGradient(30, 30, 60)
    selectedcoolgradient.setColorAt(1, QColor(255, 127, 127))
    selectedcoolgradient.setColorAt(0, QColor(255, 0, 0))

    def __init__(self, keyframe):
        super().__init__()
        self.keyframe = keyframe
        self.currentBrush = self.coolgradient
        self.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        self.keyframeshape = CzeTimelineKeyframeShape(self.keyframe)
        self.addToGroup(self.keyframeshape)
        self.addToGroup(CzeTimelineKeyframeText(self.keyframe))

    def setBrush(self, brush):
        self.currentBrush = brush
        self.keyframeshape.setBrush(brush)


class CzeTimelineAnimationKeyframeShape(QGraphicsItem):
    coolgradient = QRadialGradient(50, 50, 90)
    coolgradient.setColorAt(1, QColor(255, 255, 255))
    coolgradient.setColorAt(0, QColor(255, 0, 0))
    selectedcoolgradient = QRadialGradient(30, 30, 60)
    selectedcoolgradient.setColorAt(1, QColor(255, 127, 127))
    selectedcoolgradient.setColorAt(0, QColor(255, 0, 0))

    def __init__(self, keyframe: AnimationKeyframe, track, isInput):
        super().__init__()
        self.keyframe = keyframe
        self.track = track
        self.currentBrush = self.coolgradient
        self.isInput = isInput
        self.connectTop = 0
        self.connectBottom = 0
        self.getNeighboringTracks()

    def boundingRect(self):
        top = min(0, self.connectTop*10+7)
        bottom = max(0, self.connectBottom*10-7)
        if self.isInput:
            return self.keyframe.params.outputter.function().getInputRect(self.keyframe.params.outputter.params, self.track,bottom,top, self.keyframe)
        return self.keyframe.params.outputter.function().getOutputRect(self.keyframe.params.outputter.params, self.track,bottom,top, self.keyframe)

    def getNeighboringTracks(self):
        if self.isInput:
            # closest top track from current track
            mintrack = min(self.keyframe.inputTracks)
            # closest bottom track from current track
            maxtrack = max(self.keyframe.inputTracks)
            thistrack = self.keyframe.inputTracks[self.track]
            for track in self.keyframe.inputTracks:
                if track > thistrack:
                    maxtrack = min(maxtrack, track)
                elif track < thistrack:
                    mintrack = max(mintrack, track)
            self.connectTop = mintrack-thistrack
            self.connectBottom = maxtrack-thistrack
        else:
            # closest top track from current track
            mintrack = min(self.keyframe.outputTracks)
            # closest bottom track from current track
            maxtrack = max(self.keyframe.outputTracks)
            thistrack = self.keyframe.outputTracks[self.track]
            for track in self.keyframe.outputTracks:
                if track > thistrack:
                    maxtrack = min(maxtrack, track)
                elif track < thistrack:
                    mintrack = max(mintrack, track)
            self.connectTop = mintrack-thistrack
            self.connectBottom = maxtrack-thistrack

    def paint(self, painter: QPainter, option, widget) -> None:
        painter.setPen(QPen(QColor(0, 0, 0), 0))
        painter.setBrush(self.currentBrush)

        top = min(0, self.connectTop*10+7)
        bottom = max(0, self.connectBottom*10-7)
        if self.isInput:
            # painter.drawPolygon(
            #    [QPoint(-3, 0), QPoint(-7, -4), QPoint(-7, -7+top), QPoint(-3, -7+top), QPoint(-3,-7), QPoint(0,-7), QPoint(0,7), QPoint(-3,7), QPoint(-3, 7+bottom), QPoint(-7, 7+bottom), QPoint(-7, 4)])
            #    #   CENTER           GO ↙️       ⬇️ to connect         ➡️ by 4           ⬆️ back         ➡️            ⬆️           ⬅️            ⬆️ to connect         ⬅️ by 4            ⬇️ back
            self.keyframe.params.outputter.function().getInputShape(
                self.keyframe.params.outputter.params, self.track, bottom, top, self.keyframe, painter)
        else:
            """painter.drawPolygon(
                [QPoint(-1, 7), QPoint(-1, -7), QPoint(0, -7), QPoint(7, 0), QPoint(0, 7)])"""
            self.keyframe.params.outputter.function().getOutputShape(
                self.keyframe.params.outputter.params, self.track, bottom, top, self.keyframe, painter)
            if hasattr(self.keyframe.params.outputter.function(), "getOutputIcon"):
                self.keyframe.params.outputter.function().getOutputIcon(
                    self.keyframe.params.outputter.params, self.track, self.keyframe, painter)

    def setBrush(self, brush):
        self.currentBrush = brush

    def shape(self) -> QPainterPath:
        if self.isInput:
            return self.keyframe.params.outputter.function().getInputPath(self.keyframe.params.outputter.params, self.track, self.keyframe)
        return self.keyframe.params.outputter.function().getOutputPath(self.keyframe.params.outputter.params, self.track, self.keyframe)
        

class CzeTimelineAnimationKeyframeItem(QGraphicsItemGroup):
    coolgradient = QRadialGradient(50, 50, 90)
    coolgradient.setColorAt(1, QColor(255, 255, 255))
    coolgradient.setColorAt(0, QColor(255, 0, 0))

    def __init__(self, keyframe: AnimationKeyframe):
        super().__init__()
        self.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        self.keyframe = keyframe
        self.currentBrush = self.coolgradient
        self.inputShapeItems: List[CzeTimelineAnimationKeyframeShape] = []
        self.outputShapeItems: List[CzeTimelineAnimationKeyframeShape] = []
        for track in range(len(self.keyframe.inputTracks)):
            self.addInputShapeItem(track)
        for track in range(len(self.keyframe.outputTracks)):
            self.addOutputShapeItem(track)

    def setBrush(self, brush):
        for shape in self.inputShapeItems:
            shape.setBrush(brush)

        for shape in self.outputShapeItems:
            shape.setBrush(brush)

    def addInputShapeItem(self, track):
        self.inputShapeItems.append(
            CzeTimelineAnimationKeyframeShape(self.keyframe, track, True))
        self.addToGroup(self.inputShapeItems[-1])
        self.inputShapeItems[-1].setPos(0, self.keyframe.inputTracks[track]*20)

    def addOutputShapeItem(self, track):
        self.outputShapeItems.append(
            CzeTimelineAnimationKeyframeShape(self.keyframe, track, False))
        self.addToGroup(self.outputShapeItems[-1])
        self.outputShapeItems[-1].setPos(0,
                                         self.keyframe.outputTracks[track]*20)

    def updateShapeTracks(self):
        for shape in self.inputShapeItems:
            shape.getNeighboringTracks()

        for shape in self.outputShapeItems:
            shape.getNeighboringTracks()

    def updateShapes(self):

        if len(self.inputShapeItems) < len(self.keyframe.inputTracks):
            if not self.inputShapeItems:
                self.addInputShapeItem(0)
            for track in range(self.inputShapeItems[-1].track+1, len(self.keyframe.inputTracks)):
                self.addInputShapeItem(track)
        elif len(self.inputShapeItems) > len(self.keyframe.inputTracks):
            for track in range(len(self.keyframe.inputTracks), len(self.inputShapeItems)):
                self.removeFromGroup(self.inputShapeItems[-1])
                self.inputShapeItems[-1].setParentItem(None)
                self.inputShapeItems.pop()

        if len(self.outputShapeItems) < len(self.keyframe.outputTracks):
            if not self.outputShapeItems:
                self.addOutputShapeItem(0)
            for track in range(self.outputShapeItems[-1].track+1, len(self.keyframe.outputTracks)):
                self.addOutputShapeItem(track)
        elif len(self.outputShapeItems) > len(self.keyframe.outputTracks):
            for track in range(len(self.keyframe.outputTracks), len(self.outputShapeItems)):
                self.removeFromGroup(self.outputShapeItems[-1])
                self.outputShapeItems[-1].setParentItem(None)
                self.outputShapeItems.pop()
        self.updateShapeTracks()


class CzeTimelineAnimationModeBackground(QGraphicsItem):
    def __init__(self, boundrect):
        super().__init__()
        self.boundrect = boundrect

    def boundingRect(self):
        return self.boundrect()

    def paint(self, painter: QPainter, option, widget) -> None:
        painter.setBrush(QColor(127, 127, 127, 127))
        painter.drawRect(self.boundrect())


class CzeTimelineAnimationTrackLine(QGraphicsItem):
    def __init__(self, boundrect, animationProperty):
        super().__init__()
        self.boundrect = boundrect
        self.animationProperty = animationProperty

    def boundingRect(self):
        return self.boundrect()

    def paint(self, painter: QPainter, option, widget) -> None:
        painter.setPen(QPen(QColor(255, 255, 255), 0))
        rect: QRectF = self.boundrect()
        # distance = max(1,int((rect.bottom()-rect.top())/100+1))*20
        # for track in range(int(rect.top()/distance-1),int(rect.bottom()/distance+1)):
        for track in self.animationProperty.timeline.tracks:
            painter.drawLine(rect.left(), track*20/painter.transform().m22(),
                             rect.right(), track*20/painter.transform().m22())


class CzeTimelineAnimationSidebar(QGraphicsItem):
    coolgradient = QRadialGradient(100, 150, 200)
    coolgradient.setColorAt(0, QColor(255, 0, 0))
    coolgradient.setColorAt(1, QColor(0, 0, 0))
    bottombuttongradient = QLinearGradient(0, -10, 0, 10)
    bottombuttongradient.setColorAt(0, QColor(80, 0, 0))
    bottombuttongradient.setColorAt(0.5, QColor(100, 0, 0))
    bottombuttongradient.setColorAt(0.51, QColor(70, 0, 0))
    bottombuttongradient.setColorAt(1, QColor(0, 0, 0))
    topbuttongradient = QLinearGradient(0, -10, 0, 10)
    topbuttongradient.setColorAt(0, QColor(80, 0, 0))
    topbuttongradient.setColorAt(0.5, QColor(100, 0, 0))
    topbuttongradient.setColorAt(0.51, QColor(70, 0, 0))
    topbuttongradient.setColorAt(1, QColor(0, 0, 0))

    def __init__(self, leftside, animationProperty, timelineWidget):
        super().__init__()
        self.leftside = leftside
        self.animationProperty = animationProperty
        self.timelineWidget = timelineWidget
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        self.topPlusButtonRect = QRectF(0, -19, 99, 19)
        self.bottomPlusButtonRect = QRectF(0, 19, 99, 19)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        self.setAcceptHoverEvents(True)
        self.tophovered = False
        self.tophover = False
        self.topunhover = False
        self.bottomhover = False
        self.bottomhovered = False
        self.bottomunhover = False
        timelineWidget.parentclass.connectToEvent(
            "FrameUpdate", self.frameUpdate)

    def boundingRect(self):
        self.setPos(self.leftside().x(), 0)
        return QRectF(0, self.topPlusButtonRect.top(), 100, 19+self.bottomPlusButtonRect.top()-self.topPlusButtonRect.top())

    def paint(self, painter: QPainter, option, widget) -> None:
        self.setPos(self.leftside().x(), 0)
        maxtrack = 0
        mintrack = 0
        painter.setFont(QFont("Tahoma", 8))
        for track in self.animationProperty.timeline.tracks:
            painter.setPen(QPen(QColor(0, 0, 0), 0))
            painter.setBrush(QColor(255, 127, 127))
            painter.drawRect(QRectF(1, track*20-9, 99, 19))
            painter.setPen(QPen(QColor(255, 127, 127), 0))
            self.coolgradient.setCenter(100, 150+track*20)
            painter.setBrush(self.coolgradient)
            painter.drawRect(QRectF(2, track*20-8, 97, 17))
            painter.setPen(QColor(255, 192, 192))
            painter.drawText(QRectF(1, track*20-9, 99, 19), str(self.animationProperty.timeline.tracks[track]["value"])[:5],
                             Qt.AlignmentFlag.AlignCenter)
            maxtrack = max(track, maxtrack)
            mintrack = min(track, mintrack)
        maxtrack += 1
        mintrack -= 1

        self.bottombuttongradient.setStart(0, maxtrack*20-10)
        self.bottombuttongradient.setFinalStop(0, maxtrack*20+10)

        painter.setPen(QColor(0, 0, 0))
        painter.setBrush(QColor(127, 0, 0))
        self.bottomPlusButtonRect = QRectF(1, maxtrack*20-9, 99, 19)
        painter.drawRoundedRect(self.bottomPlusButtonRect, 3, 3)
        if self.bottomhover:
            self.bottombuttongradient.setColorAt(0, QColor(240, 0, 0))
            self.bottombuttongradient.setColorAt(0.5, QColor(180, 0, 0))
            self.bottombuttongradient.setColorAt(0.51, QColor(135, 0, 0))
            self.bottombuttongradient.setColorAt(1, QColor(80, 0, 0))
            self.bottomhover = False
        if self.bottomunhover:
            self.bottombuttongradient.setColorAt(0, QColor(80, 0, 0))
            self.bottombuttongradient.setColorAt(0.5, QColor(100, 0, 0))
            self.bottombuttongradient.setColorAt(0.51, QColor(70, 0, 0))
            self.bottombuttongradient.setColorAt(1, QColor(0, 0, 0))
            self.bottomunhover = False
        painter.setBrush(self.bottombuttongradient)
        painter.setPen(QColor(127, 0, 0))
        painter.drawRoundedRect(QRectF(2, maxtrack*20-8, 97, 17), 3, 3)
        painter.setPen(QColor(255, 192, 192))
        painter.drawText(QRectF(1, maxtrack*20-9, 99, 19), "+",
                         Qt.AlignmentFlag.AlignCenter)
        self.topbuttongradient.setStart(0, mintrack*20-10)
        self.topbuttongradient.setFinalStop(0, mintrack*20+10)
        painter.setPen(QColor(0, 0, 0))
        painter.setBrush(QColor(127, 0, 0))
        if self.tophover:
            self.topbuttongradient.setColorAt(0, QColor(240, 0, 0))
            self.topbuttongradient.setColorAt(0.5, QColor(180, 0, 0))
            self.topbuttongradient.setColorAt(0.51, QColor(135, 0, 0))
            self.topbuttongradient.setColorAt(1, QColor(80, 0, 0))
            self.tophover = False
        if self.topunhover:
            self.topbuttongradient.setColorAt(0, QColor(80, 0, 0))
            self.topbuttongradient.setColorAt(0.5, QColor(100, 0, 0))
            self.topbuttongradient.setColorAt(0.51, QColor(70, 0, 0))
            self.topbuttongradient.setColorAt(1, QColor(0, 0, 0))
            self.topunhover = False
        self.topPlusButtonRect = QRectF(1, mintrack*20-9, 99, 19)
        painter.drawRoundedRect(self.topPlusButtonRect, 3, 3)
        painter.setBrush(self.topbuttongradient)
        painter.setPen(QColor(127, 0, 0))
        painter.drawRoundedRect(QRectF(2, mintrack*20-8, 97, 17), 3, 3)
        painter.setPen(QColor(255, 192, 192))
        painter.drawText(QRectF(1, mintrack*20-9, 99, 19), "+",
                         Qt.AlignmentFlag.AlignCenter)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if self.topPlusButtonRect.contains(event.pos()):
                self.animationProperty.timeline.originaltracks[min(self.animationProperty.timeline.originaltracks.keys(
                ))-1] = self.animationProperty.timeline.originaltracks[min(self.animationProperty.timeline.originaltracks.keys())].copy()
                self.timelineWidget.graphicsview.viewport().update()
            elif self.bottomPlusButtonRect.contains(event.pos()):
                self.animationProperty.timeline.originaltracks[max(self.animationProperty.timeline.originaltracks.keys(
                ))+1] = self.animationProperty.timeline.originaltracks[max(self.animationProperty.timeline.originaltracks.keys())].copy()
                self.timelineWidget.graphicsview.viewport().update()

        event.accept()

    def frameUpdate(self):
        self.update(self.boundingRect())

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if self.topPlusButtonRect.contains(event.pos()) and not self.tophovered:
            self.tophover = True
            self.tophovered = True
            self.update(self.boundingRect())
        elif not self.topPlusButtonRect.contains(event.pos()) and self.tophovered:
            self.topunhover = True
            self.tophovered = False
            self.update(self.boundingRect())

        if self.bottomPlusButtonRect.contains(event.pos()) and not self.bottomhovered:
            self.bottomhover = True
            self.bottomhovered = True
            self.update(self.boundingRect())
        elif not self.bottomPlusButtonRect.contains(event.pos()) and self.bottomhovered:
            self.bottomunhover = True
            self.bottomhovered = False
            self.update(self.boundingRect())

        event.accept()

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.bottomunhover = True
        self.bottomhovered = False
        self.topunhover = True
        self.tophovered = False
        return super().hoverLeaveEvent(event)


class CzeTimeline(QWidget):
    coolgradient = QRadialGradient(50, 50, 90)
    coolgradient.setColorAt(1, QColor(255, 255, 255))
    coolgradient.setColorAt(0, QColor(255, 0, 0))
    selectedcoolgradient = QRadialGradient(30, 30, 60)
    selectedcoolgradient.setColorAt(1, QColor(255, 127, 127))
    selectedcoolgradient.setColorAt(0, QColor(255, 0, 0))
    hovergradient = QRadialGradient(50, 50, 120)
    hovergradient.setColorAt(1, QColor(255, 255, 255))
    hovergradient.setColorAt(0, QColor(255, 0, 0))

    def __init__(self, parent, parentclass):
        self.keyframes = {}
        self.keyframeitems = {}
        super().__init__(parent)
        self.parentclass = parentclass

        # self.setSizePolicy(QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Ignored)

        self.scene = QGraphicsScene(self)
        self.graphicsview = QGraphicsViewEvent(self)
        # self.graphicsview.setSceneRect(QRectF(0,0,200,2000))
        self.graphicsview.setScene(self.scene)
        self.graphicsview.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphicsview.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphicsview.horizontalScrollBar().disconnect(self.graphicsview)
        self.graphicsview.verticalScrollBar().disconnect(self.graphicsview)
        self.graphicsview.ensureVisible = dummyfunction
        # kefrmae = self.scene.addRect(QRectF(0,0,18,18),QPen(QColor(0,0,0),0),coolgradient)
        # self.scene.addLine(QLine(0,0,0,self.scene.height()),QPen(QColor(0,0,0),0))
        self.graphicsview.setStyleSheet(
            "border-image:url(editor:Square Frame.png) 2; border-width:2;")
        # self.graphicsview.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        for keyframe in self.parentclass.keyframes:
            self.addKeyframe(keyframe)
        boundingrect = self.graphicsview.mapToScene(
            self.graphicsview.viewport().geometry()).boundingRect()
        self.playbackcursor = self.scene.addLine(QLine(playbackframe, boundingrect.top(
        ), playbackframe, boundingrect.bottom()), QPen(QColor(255, 0, 0), 0))
        self.draggedframe = None
        self.graphicsview.onpress = self.pressEvent
        self.graphicsview.onrelease = self.releaseEvent
        self.graphicsview.onmove = self.mmoveEvent
        self.graphicsview.onscroll = self.zoom
        self.graphicsview.ondoubleclick = self.doubleClickEvent
        # self.graphicsview.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        # self.graphicsview.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.graphicsview.verticalScrollBar().setMaximum(200000000)
        self.graphicsview.horizontalScrollBar().setMaximum(200000000)

        self.setAcceptDrops(True)
        self.graphicsview.setAcceptDrops(True)
        self.graphicsview.viewport().setAcceptDrops(True)
        self.graphicsview.dragenter = self.dragEnterEvent
        self.graphicsview.dragdrop = self.dropEvent
        self.graphicsview.dragmove = self.dragMoveEvent
        self.seekingBackground = None
        self.seekingText = None
        self.startTimer(0.25, Qt.TimerType.CoarseTimer)
        self.hoveredkeyframe = None
        self.animationProperty = None
        self.animationKeyframes = {}
        self.draggedAnimationFrameItem = None
        self.backButton = QRedButton(self, "Back", self.exitAnimationMode)
        self.backButton.hide()
        self.parentclass.connectToEvent(
            "UpdateAnimationKeyframe", self.updateAnimationKeyframe)

    def timerEvent(self, event) -> None:
        self.updateSeekingState()
        return super().timerEvent(event)

    def sizeHint(self):
        return QSize(self.size().width(), 150)

    def updateplaybackcursor(self, frame):
        boundingrect = self.graphicsview.mapToScene(
            self.graphicsview.viewport().geometry()).boundingRect()
        self.playbackcursor.setLine(
            QLine(frame, boundingrect.top(), frame, boundingrect.bottom()))

    def updateSeekingState(self):
        if self.parentclass.seeking and not self.seekingBackground:
            self.seekingBackground = self.scene.addPolygon(self.graphicsview.mapToScene(
                self.rect()), QColor(127, 127, 127, 127), QColor(127, 127, 127, 127))
            self.seekingText = self.scene.addText(
                "Seeking...", QFont("Arial", 12))
            self.seekingText.setPos(
                self.graphicsview.mapToScene(self.rect().center()))
        elif not self.parentclass.seeking and self.seekingBackground:
            self.scene.removeItem(self.seekingBackground)
            self.scene.removeItem(self.seekingText)
            self.seekingBackground = None
            self.seekingText = None

    def mmoveEvent(self, event: QMouseEvent, prevpos: QPoint) -> None:

        if event.buttons() & Qt.MouseButton.MiddleButton:

            delta = (event.pos()-prevpos) * \
                (self.graphicsview.sceneRect().width()/self.size().width())
            self.graphicsview.translate(delta.x(), delta.y())

            boundingrect = self.graphicsview.mapToScene(
                self.graphicsview.viewport().geometry()).boundingRect()
            self.playbackcursor.setLine(QLine(self.parentclass.playbackframe, boundingrect.top(
            ), self.parentclass.playbackframe, boundingrect.bottom()))
        if self.animationProperty is None:
            if not (event.buttons() & Qt.MouseButton.LeftButton):

                founditem: QGraphicsItem = self.graphicsview.itemAt(
                    event.pos())
                if isinstance(founditem, CzeTimelineKeyframeShape):
                    if founditem != self.hoveredkeyframe and self.hoveredkeyframe:
                        self.hoveredkeyframe.setBrush(self.coolgradient)
                        if founditem.currentBrush == self.coolgradient:
                            founditem.setBrush(self.hovergradient)
                            self.hoveredkeyframe = founditem
                        self.graphicsview.update()
                    else:
                        if founditem.currentBrush == self.coolgradient:
                            founditem.setBrush(self.hovergradient)
                            self.hoveredkeyframe = founditem
                            self.graphicsview.update()
                else:
                    if founditem != self.hoveredkeyframe and self.hoveredkeyframe:
                        if (self.hoveredkeyframe.currentBrush == self.hovergradient):
                            self.hoveredkeyframe.setBrush(self.coolgradient)
                        self.hoveredkeyframe = None
                        self.graphicsview.update()
            if self.draggedframe and self.graphicsview.geometry().contains(event.pos()):

                mapped = self.graphicsview.mapToScene(event.pos())

                self.parentclass.keyframes.setframe(
                    self.draggedframe, int(mapped.x()))
                self.parentclass.keyframes.setlayer(
                    self.draggedframe, -round(mapped.y()/25))

                self.keyframes[self.draggedframe].setPos(
                    self.draggedframe.frame, -self.draggedframe.layer*25)

                self.parentclass.updateviewport()

        else:
            if not (event.buttons() & Qt.MouseButton.LeftButton):
                founditem: QGraphicsItem = self.graphicsview.itemAt(
                    event.pos())
                if isinstance(founditem, CzeTimelineAnimationKeyframeShape):
                    if founditem != self.hoveredkeyframe and self.hoveredkeyframe:
                        self.hoveredkeyframe.setBrush(self.coolgradient)
                        if founditem.currentBrush == self.coolgradient:
                            founditem.setBrush(self.hovergradient)
                            self.hoveredkeyframe = founditem
                        self.graphicsview.update()
                    else:
                        if founditem.currentBrush == self.coolgradient:
                            founditem.setBrush(self.hovergradient)
                            self.hoveredkeyframe = founditem
                            self.graphicsview.update()
                else:
                    if founditem != self.hoveredkeyframe and self.hoveredkeyframe:
                        if (self.hoveredkeyframe.currentBrush == self.hovergradient):
                            self.hoveredkeyframe.setBrush(self.coolgradient)
                        self.hoveredkeyframe = None
                        self.graphicsview.update()
            if self.draggedAnimationFrameItem is not None and self.graphicsview.geometry().contains(event.pos()):
                mapped = self.graphicsview.mapToScene(event.pos())
                track = int((mapped.y()/20+0.5) *
                            self.graphicsview.transform().m22())
                if self.animationProperty.associatedKeyframe:
                    self.animationProperty.timeline.setframe(
                        self.draggedAnimationFrameItem.keyframe, int(mapped.x()-self.animationProperty.associatedKeyframe.frame))
                    if self.draggedAnimationFrameItem.isInput:
                        self.animationProperty.timeline.moveInputToTrack(
                            self.draggedAnimationFrameItem.keyframe, track, self.draggedAnimationFrameItem.track)
                        self.animationKeyframes[self.draggedAnimationFrameItem.keyframe].setPos(
                            self.draggedAnimationFrameItem.keyframe.frame+self.animationProperty.associatedKeyframe.frame, 0)
                        self.draggedAnimationFrameItem.setPos(
                            0, self.draggedAnimationFrameItem.keyframe.inputTracks[self.draggedAnimationFrameItem.track]*20)
                    else:
                        self.animationProperty.timeline.moveOutputToTrack(
                            self.draggedAnimationFrameItem.keyframe, track, self.draggedAnimationFrameItem.track)
                        self.animationKeyframes[self.draggedAnimationFrameItem.keyframe].setPos(
                            self.draggedAnimationFrameItem.keyframe.frame+self.animationProperty.associatedKeyframe.frame, 0)
                        self.draggedAnimationFrameItem.setPos(
                            0, self.draggedAnimationFrameItem.keyframe.outputTracks[self.draggedAnimationFrameItem.track]*20)
                else:
                    self.animationProperty.timeline.setframe(
                        self.draggedAnimationFrameItem.keyframe, int(mapped.x()))
                    if self.draggedAnimationFrameItem.isInput:
                        self.animationProperty.timeline.moveInputToTrack(
                            self.draggedAnimationFrameItem.keyframe, track, self.draggedAnimationFrameItem.track)
                        self.animationKeyframes[self.draggedAnimationFrameItem.keyframe].setPos(
                            self.draggedAnimationFrameItem.keyframe.frame, 0)
                        self.draggedAnimationFrameItem.setPos(
                            0, self.draggedAnimationFrameItem.keyframe.inputTracks[self.draggedAnimationFrameItem.track]*20)
                    else:
                        self.animationProperty.timeline.moveOutputToTrack(
                            self.draggedAnimationFrameItem.keyframe, track, self.draggedAnimationFrameItem.track)
                        self.animationKeyframes[self.draggedAnimationFrameItem.keyframe].setPos(
                            self.draggedAnimationFrameItem.keyframe.frame, 0)
                        self.draggedAnimationFrameItem.setPos(
                            0, self.draggedAnimationFrameItem.keyframe.outputTracks[self.draggedAnimationFrameItem.track]*20)

    def deselectFrame(self):
        if self.parentclass.selectedframe:
            self.keyframes[self.parentclass.selectedframe].setBrush(
                self.coolgradient)
            self.parentclass.selectedframe = None
            self.parentclass.updatekeyframeoptions()
            self.parentclass.viewport.updatehandles()
            self.graphicsview.update()

    def doubleClickEvent(self, event: QMouseEvent):
        if self.animationProperty is None:
            if event.button() == Qt.MouseButton.LeftButton:
                founditem: QGraphicsItem = self.graphicsview.itemAt(
                    event.pos().x(), event.pos().y())
                if isinstance(founditem, CzeTimelineKeyframeShape):
                    self.parentclass.draggedpreset = founditem.keyframe.copy()
                    drag = QDrag(self)
                    mime = QMimeData()
                    drag.setMimeData(mime)
                    drag.exec_(Qt.MoveAction)
                else:
                    self.deselectFrame()

    def pressEvent(self, event: QMouseEvent) -> None:
        if self.animationProperty is None:
            if event.button() == Qt.MouseButton.LeftButton:
                founditem: QGraphicsItem = self.graphicsview.itemAt(
                    event.pos().x(), event.pos().y())
                if isinstance(founditem, CzeTimelineKeyframeShape) or founditem is None:
                    if founditem != None:
                        self.draggedframe = founditem.keyframe
                        if self.parentclass.selectedframe:
                            self.keyframes[self.parentclass.selectedframe].setBrush(
                                self.coolgradient)
                        founditem.setBrush(self.selectedcoolgradient)
                        self.parentclass.selectedframe = founditem.keyframe
                        self.parentclass.regeneratekeyframeoptions()
                        self.parentclass.viewport.updatehandles()
                        self.graphicsview.update()

                    else:
                        self.parentclass.seek(
                            self.graphicsview.mapToScene(event.pos().x(), 0).x())
                        self.updateplaybackcursor(
                            self.graphicsview.mapToScene(event.pos().x(), 0).x())
                        self.parentclass.updateviewport()
                        self.graphicsview.update()
        else:
            if event.button() == Qt.MouseButton.LeftButton:
                founditem: QGraphicsItem = self.graphicsview.itemAt(
                    event.pos().x(), event.pos().y())
                if isinstance(founditem, CzeTimelineAnimationKeyframeShape) or isinstance(founditem, CzeTimelineAnimationModeBackground):
                    if not isinstance(founditem, CzeTimelineAnimationModeBackground):
                        self.draggedAnimationFrameItem = founditem
                        if self.parentclass.selectedAnimationFrame is not None:
                            self.animationKeyframes[self.parentclass.selectedAnimationFrame].setBrush(
                                self.coolgradient)
                        founditem.setBrush(self.selectedcoolgradient)
                        self.parentclass.selectedAnimationFrame = founditem.keyframe
                        self.parentclass.keyframeoptions.rebuild(
                            self.draggedAnimationFrameItem.keyframe.params)
                        self.parentclass.viewport.updatehandles()
                        self.graphicsview.update()
                    else:
                        self.parentclass.seek(
                            self.graphicsview.mapToScene(event.pos().x(), 0).x())
                        self.updateplaybackcursor(
                            self.graphicsview.mapToScene(event.pos().x(), 0).x())
                        self.parentclass.updateviewport()
                        self.graphicsview.update()

            # elif hasattr(founditem,"pressEvent"):
            #    founditem.pressEvent(event,self.graphicsview.mapToScene(event.pos().x(),0).toPoint()) # TODO : Give more parameters to the function

            self.lastm1pos = event.pos()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        event.accept()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        # print(self.parentclass.draggedpreset)
        if self.parentclass.draggedpreset and not self.draggedframe:
            mapped = self.graphicsview.mapToScene(event.pos())
            keyframe = Keyframe(int(mapped.x()), -round(mapped.y()/25),
                                self.parentclass.draggedpreset.params.copy())
            self.parentclass.keyframes.add(keyframe)
            self.addKeyframe(keyframe)
            if self.parentclass.selectedframe:
                self.keyframes[self.parentclass.selectedframe].setBrush(
                    self.coolgradient)
            self.parentclass.selectedframe = keyframe
            self.parentclass.draggedpreset = None
            self.parentclass.regeneratekeyframeoptions()
            self.parentclass.viewport.updatehandles()
            self.keyframes[keyframe].setBrush(self.selectedcoolgradient)
            self.graphicsview.update()
        event.accept()
        return super().dropEvent(event)

    def releaseEvent(self, event: QMouseEvent) -> None:
        if self.animationProperty is None:
            if event.button() == Qt.MouseButton.LeftButton:
                if self.draggedframe:
                    mapped = self.graphicsview.mapToScene(event.pos())

                    self.parentclass.keyframes.setframe(
                        self.draggedframe, int(mapped.x()))
                    self.parentclass.keyframes.setlayer(
                        self.draggedframe, -round(mapped.y()/25))

                    self.keyframes[self.draggedframe].setPos(
                        self.draggedframe.frame, -self.draggedframe.layer*25)
                    self.draggedframe = None
                    self.parentclass.updateviewport()
        else:
            if event.button() == Qt.MouseButton.LeftButton:
                if self.draggedAnimationFrameItem:
                    mapped = self.graphicsview.mapToScene(event.pos())
                    track = int((mapped.y()/20+0.5) *
                                self.graphicsview.transform().m22())
                    if self.animationProperty.associatedKeyframe:
                        self.animationProperty.timeline.setframe(
                            self.draggedAnimationFrameItem.keyframe, int(mapped.x()-self.animationProperty.associatedKeyframe.frame))
                        if self.draggedAnimationFrameItem.isInput:
                            self.animationProperty.timeline.moveInputToTrack(self.draggedAnimationFrameItem.keyframe, int(
                                (mapped.y()/20+0.5)*self.graphicsview.transform().m22()), self.draggedAnimationFrameItem.track)
                            self.animationKeyframes[self.draggedAnimationFrameItem.keyframe].setPos(
                                self.draggedAnimationFrameItem.keyframe.frame+self.animationProperty.associatedKeyframe.frame, 0)
                            self.draggedAnimationFrameItem.setPos(
                                0, self.draggedAnimationFrameItem.keyframe.inputTracks[self.draggedAnimationFrameItem.track]*20)
                        else:
                            self.animationProperty.timeline.moveOutputToTrack(self.draggedAnimationFrameItem.keyframe, int(
                                (mapped.y()/20+0.5)*self.graphicsview.transform().m22()), self.draggedAnimationFrameItem.track)
                            self.animationKeyframes[self.draggedAnimationFrameItem.keyframe].setPos(
                                self.draggedAnimationFrameItem.keyframe.frame+self.animationProperty.associatedKeyframe.frame, 0)
                            self.draggedAnimationFrameItem.setPos(
                                0, self.draggedAnimationFrameItem.keyframe.outputTracks[self.draggedAnimationFrameItem.track]*20)
                    else:
                        self.animationProperty.timeline.setframe(
                            self.draggedAnimationFrameItem.keyframe, int(mapped.x()))
                        if self.draggedAnimationFrameItem.isInput:
                            self.animationProperty.timeline.moveInputToTrack(
                                self.draggedAnimationFrameItem.keyframe, track, self.draggedAnimationFrameItem.track)
                            self.animationKeyframes[self.draggedAnimationFrameItem.keyframe].setPos(
                                self.draggedAnimationFrameItem.keyframe.frame, 0)
                            self.draggedAnimationFrameItem.setPos(
                                0, self.draggedAnimationFrameItem.keyframe.inputTracks[self.draggedAnimationFrameItem.track]*20)
                        else:
                            self.animationProperty.timeline.moveOutputToTrack(
                                self.draggedAnimationFrameItem.keyframe, track, self.draggedAnimationFrameItem.track)
                            self.animationKeyframes[self.draggedAnimationFrameItem.keyframe].setPos(
                                self.draggedAnimationFrameItem.keyframe.frame, 0)
                            self.draggedAnimationFrameItem.setPos(
                                0, self.draggedAnimationFrameItem.keyframe.outputTracks[self.draggedAnimationFrameItem.track]*20)
                    self.animationKeyframes[self.draggedAnimationFrameItem.keyframe].updateShapeTracks(
                    )
                    self.draggedAnimationFrameItem = None
                    self.parentclass.updateviewport()
            # elif hasattr(founditem,"pressEvent"):
            #    founditem.pressEvent(event,self.graphicsview.mapToScene(event.pos().x(),0).toPoint())
        return super().mouseReleaseEvent(event)

        # return super().mouseReleaseEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        # originaltransform = self.graphicsview.transform()
        self.scene.setSceneRect(self.rect())
        r = self.graphicsview.sceneRect()
        # hacky workaround, if this wasnt here it would snap to 0,0 every time you shrinked the view by more than 1 pixel per frame
        r.setSize(event.size()/self.graphicsview.transform().m11() +
                  QSize(10000, 10000))
        self.graphicsview.setSceneRect(r)
        self.graphicsview.setFixedSize(event.size())
        self.graphicsview.size().setHeight(event.size().height())
        self.graphicsview.size().setWidth(event.size().width())

        # self.graphicsview.adjustSize()
        r = self.graphicsview.sceneRect()
        r.setSize(event.size()/self.graphicsview.transform().m11())
        self.graphicsview.setSceneRect(r)
        # print(r)
        # print(self.graphicsview.)
        super().resizeEvent(event)

        # self.graphicsview.adjustSize()
        # self.graphicsview.setSceneRect(r)
        # self.graphicsview.setTransform(originaltransform)

        boundingrect = self.graphicsview.mapToScene(
            self.graphicsview.viewport().geometry()).boundingRect()
        self.playbackcursor.setLine(QLine(self.parentclass.playbackframe, boundingrect.top(
        ), self.parentclass.playbackframe, boundingrect.bottom()))

    def addKeyframe(self, keyframe: Keyframe):
        # self.keyframes[keyframe] = self.scene.addRect(QRectF(-9,-9,18,18),QPen(QColor(0,0,0),0),self.coolgradient)
        # self.keyframes[keyframe].setRotation(45)
        #
        # self.keyframes[keyframe].setData(0,keyframe)
        self.keyframes[keyframe] = CzeTimelineKeyframeItem(keyframe)
        self.scene.addItem(self.keyframes[keyframe])
        self.keyframes[keyframe].setPos(keyframe.frame, -keyframe.layer*25)
        self.createKeyframeItem(keyframe, keyframe.params.source)
        for action in keyframe.params.actions:
            self.createKeyframeItem(keyframe, action)
        for effect in keyframe.params.effects:
            self.createKeyframeItem(keyframe, effect)

    def addAnimationKeyframe(self, keyframe: AnimationKeyframe):
        self.animationKeyframes[keyframe] = CzeTimelineAnimationKeyframeItem(
            keyframe)
        self.scene.addItem(self.animationKeyframes[keyframe])
        if self.animationProperty.associatedKeyframe:
            self.animationKeyframes[keyframe].setPos(
                keyframe.frame+self.animationProperty.associatedKeyframe.frame, 0)
        else:
            self.animationKeyframes[keyframe].setPos(keyframe.frame, 0)

    def updateAnimationKeyframe(self):
        self.animationKeyframes[self.parentclass.selectedAnimationFrame].updateShapes(
        )

    def createKeyframeItem(self, keyframe: Keyframe, param: Params):
        if (keyframe is None):
            return
        if param.function and hasattr(param.function(), "timelineitem"):
            items = param.function().timelineitem(param, keyframe, self.parentclass)
            if (keyframe not in self.keyframeitems):
                self.keyframeitems[keyframe] = {}
                self.keyframeitems[keyframe][param] = []
            elif param not in self.keyframeitems[keyframe]:
                self.keyframeitems[keyframe][param] = []
            for item in items:
                self.keyframeitems[keyframe][param].append(item)
                self.scene.addItem(item)

    def deleteKeyframeItem(self, keyframe, param):
        if (keyframe is None):
            return
        if (keyframe in self.keyframeitems and param in self.keyframeitems[keyframe]):
            for item in self.keyframeitems[keyframe][param]:
                self.scene.removeItem(item)
            del self.keyframeitems[keyframe][param]

    def deleteKeyframeItems(self, keyframe):
        if (keyframe is None):
            return
        if (keyframe in self.keyframeitems):
            for param in self.keyframeitems[keyframe].keys():
                for item in self.keyframeitems[keyframe][param]:
                    self.scene.removeItem(item)
            del self.keyframeitems[keyframe]

    def zoom(self, event: QWheelEvent):
        oldpos = self.graphicsview.mapToScene(event.position().toPoint())
        factor = 1.05
        self.graphicsview.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.graphicsview.scale((factor if event.angleDelta().y(
        ) > 0 else 1/factor), (factor if event.angleDelta().y() > 0 else 1/factor))
        r = self.graphicsview.sceneRect()
        r.setSize(self.size()/self.graphicsview.transform().m11())
        self.graphicsview.setSceneRect(r)
        newpos = self.graphicsview.mapToScene(event.position().toPoint())
        delta = newpos-oldpos
        self.graphicsview.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorViewCenter)

        self.graphicsview.translate(delta.x(), delta.y())
        boundingrect = self.graphicsview.mapToScene(
            self.graphicsview.viewport().geometry()).boundingRect()
        self.playbackcursor.setLine(QLine(self.parentclass.playbackframe, boundingrect.top(
        ), self.parentclass.playbackframe, boundingrect.bottom()))

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if self.animationProperty is None:
            if event.text() == "k":

                self.addKeyframe(self.parentclass.keyframes.create(
                    self.parentclass.playbackframe))
            elif event.key() == Qt.Key.Key_Delete and not self.parentclass.rendering and not self.parentclass.seeking:
                if (self.parentclass.selectedframe == self.draggedframe):
                    self.draggedframe = None
                self.deleteKeyframeItems(self.parentclass.selectedframe)
                self.scene.removeItem(
                    self.keyframes[self.parentclass.selectedframe])
                self.parentclass.keyframes.remove(
                    self.parentclass.selectedframe)
                del self.keyframes[self.parentclass.selectedframe]
                self.parentclass.selectedframe = None
                self.parentclass.regeneratekeyframeoptions()
                self.parentclass.viewport.updatehandles()
                self.parentclass.updateviewport()
        else:
            if event.text() == "k":
                keyframe = self.animationProperty.defaultKeyframe(
                    self.parentclass.playbackframe-self.animationProperty.associatedKeyframe.frame, [0])  # TODO : Make track selection change what track the keyframe is created on.
                self.animationProperty.timeline.add(keyframe)
                self.addAnimationKeyframe(keyframe)

        return super().keyPressEvent(event)

    def enterAnimationMode(self, property):
        self.parentclass.selectedAnimationFrame = None
        self.animationProperty = property
        if self.animationProperty.timeline is None:
            self.animationProperty.timeline = AnimationKeyframeList(
                self.animationProperty.tracks, self.parentclass)
        for keyframe in self.animationKeyframes:
            self.scene.removeItem(self.animationKeyframes[keyframe])
        self.animationKeyframes = {}
        def boundrect(): return (
            self.graphicsview.mapToScene(self.graphicsview.viewport().geometry()).boundingRect())
        self.animationKeyframes["background"] = CzeTimelineAnimationModeBackground(
            boundrect)

        def leftside(): return (self.graphicsview.mapToScene(0, 0))
        self.animationKeyframes["tracks"] = CzeTimelineAnimationTrackLine(
            boundrect, self.animationProperty)
        self.animationKeyframes["sidebar"] = CzeTimelineAnimationSidebar(
            leftside, self.animationProperty, self)
        self.scene.addItem(self.animationKeyframes["tracks"])
        self.scene.addItem(self.animationKeyframes["background"])
        self.scene.addItem(self.animationKeyframes["sidebar"])
        for keyframe in self.animationProperty.timeline:
            self.addAnimationKeyframe(keyframe)
        self.backButton.show()

    def exitAnimationMode(self):
        for keyframe in self.animationKeyframes:
            self.scene.removeItem(self.animationKeyframes[keyframe])
        self.animationKeyframes = {}
        self.animationProperty = None
        self.parentclass.keyframeoptions.rebuild(
            self.parentclass.selectedframe.params)
        self.backButton.hide()
        self.parentclass.selectedAnimationFrame = None


class CzePresetKeyframeItem(QGraphicsItem):
    coolgradient = QRadialGradient(50, 50, 90)
    coolgradient.setColorAt(1, QColor(255, 255, 255))
    coolgradient.setColorAt(0, QColor(255, 0, 0))
    selectedcoolgradient = QRadialGradient(30, 30, 60)
    selectedcoolgradient.setColorAt(1, QColor(255, 127, 127))
    selectedcoolgradient.setColorAt(0, QColor(255, 0, 0))
    selectedcoolgradientbackground = QRadialGradient(40, 40, 90)
    selectedcoolgradientbackground.setColorAt(1, QColor(255, 127, 127, 63))
    selectedcoolgradientbackground.setColorAt(0, QColor(255, 0, 0, 63))
    hoveredcoolgradientbackground = QRadialGradient(40, 40, 80)
    hoveredcoolgradientbackground.setColorAt(1, QColor(255, 127, 127, 32))
    hoveredcoolgradientbackground.setColorAt(0, QColor(255, 0, 0, 32))

    def __init__(self, keyframe):
        super().__init__()
        self.keyframe = keyframe
        self.name = keyframe.params.properties.params.name
        self.selected = False
        self.hovered = False

    def boundingRect(self):
        return QRectF(-30, -20, 60, 45)

    def setSelect(self, value):
        self.selected = value

    def setHovered(self, value):
        self.hovered = value

    def paint(self, painter: QPainter, option, widget) -> None:

        if (self.selected):
            painter.setBrush(self.selectedcoolgradientbackground)
            painter.setPen(QPen(QColor(255, 192, 192, 64), 0))
            painter.drawRect(-30, -20, 60, 45)
            painter.setBrush(self.selectedcoolgradient)
            painter.setPen(QPen(QColor(0, 0, 0), 0))
            painter.drawPolygon([QPoint(10, 0), QPoint(
                0, 10), QPoint(-10, 0), QPoint(0, -10)])
        elif (self.hovered):
            painter.setBrush(self.hoveredcoolgradientbackground)
            painter.setPen(QPen(QColor(255, 192, 192, 32), 0))
            painter.drawRect(-30, -20, 60, 45)
            painter.setBrush(self.coolgradient)
            painter.setPen(QPen(QColor(0, 0, 0), 0))
            painter.drawPolygon([QPoint(10, 0), QPoint(
                0, 10), QPoint(-10, 0), QPoint(0, -10)])
        else:
            painter.setBrush(self.coolgradient)
            painter.setPen(QPen(QColor(0, 0, 0), 0))
            painter.drawPolygon([QPoint(10, 0), QPoint(
                0, 10), QPoint(-10, 0), QPoint(0, -10)])
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(255, 192, 192, 64), 0))
        painter.drawRect(-20, -20, 40, 40)
        painter.setPen(QPen(QColor(255, 192, 192), 0))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(QRectF(-30, 21, 60, 35), self.name(),
                         Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)


class CzePresets(QWidget):
    coolgradient = QRadialGradient(50, 50, 90)
    coolgradient.setColorAt(1, QColor(255, 255, 255))
    coolgradient.setColorAt(0, QColor(255, 0, 0))
    selectedcoolgradient = QRadialGradient(30, 30, 60)
    selectedcoolgradient.setColorAt(1, QColor(255, 127, 127))
    selectedcoolgradient.setColorAt(0, QColor(255, 0, 0))

    def __init__(self, parent, parentclass):
        super().__init__(parent)
        self.parentclass = parentclass
        self.scene = QGraphicsScene(self)
        self.graphicsview = QGraphicsViewEvent(self)
        self.graphicsview.setScene(self.scene)
        self.keyframes = [Keyframe(0, 0, Params({
            "properties": {
                "params": {
                    "name": LineStringProperty("Image"),
                }
            },
            "source":
            {
                "function": Selectable(0, self.parentclass.sourcefunctionsdropdown),
                "params": Selectable(0, self.parentclass.sourcefunctionsdropdown)().params.copy()
            },
            "actions": [
                {
                    "function": Selectable(0, self.parentclass.actionfunctionsdropdown),
                    "params": Selectable(0, self.parentclass.actionfunctionsdropdown)().params.copy()
                }
            ],
            "effects": [
                {
                    "function": Selectable(0, self.parentclass.effectfunctionsdropdown),
                    "params": Selectable(0, self.parentclass.effectfunctionsdropdown)().params.copy().set("x", IntProperty(640)).set("y", IntProperty(360))
                },
                {
                    "function": Selectable(2, self.parentclass.effectfunctionsdropdown),
                    "params": Selectable(2, self.parentclass.effectfunctionsdropdown)().params.copy()
                }
            ]
        })),
            Keyframe(0, 0, Params({
                "properties": {
                    "params": {
                        "name": LineStringProperty("Video"),
                    }
                },
                "source":
                {
                    "function": Selectable(4, self.parentclass.sourcefunctionsdropdown),
                    "params": Selectable(4, self.parentclass.sourcefunctionsdropdown)().params.copy()
                },
                "actions": [
                    {
                        "function": Selectable(0, self.parentclass.actionfunctionsdropdown),
                        "params": Selectable(0, self.parentclass.actionfunctionsdropdown)().params.copy()
                    }
                ],
                "effects": [
                    {
                        "function": Selectable(0, self.parentclass.effectfunctionsdropdown),
                        "params": Selectable(0, self.parentclass.effectfunctionsdropdown)().params.copy().set("x", IntProperty(640)).set("y", IntProperty(360))
                    },
                    {
                        "function": Selectable(2, self.parentclass.effectfunctionsdropdown),
                        "params": Selectable(2, self.parentclass.effectfunctionsdropdown)().params.copy()
                    }
                ]
            }))]
        self.drawnkeyframes = {}
        i = 0
        for keyframe in self.keyframes:  # TODO : Maybe load from a file?
            self.drawnkeyframes[keyframe] = CzePresetKeyframeItem(keyframe)
            self.scene.addItem(self.drawnkeyframes[keyframe])
            self.drawnkeyframes[keyframe].setPos(
                (i % 6)*64+30, floor(i/6)*44+20)
            # self.drawnkeyframes[keyframe] = self.scene.addRect(QRectF(-9,-9,18,18),QPen(QColor(0,0,0),0),self.coolgradient)
            # self.drawnkeyframes[keyframe].setRotation(45)
            # self.drawnkeyframes[keyframe].setPos((i%6)*25,floor(i/6)*25)
            # self.drawnkeyframes[keyframe].setData(0,keyframe)
            i += 1
        self.graphicsview.onpress = self.pressEvent
        self.setAcceptDrops(True)
        self.graphicsview.setAcceptDrops(True)
        self.graphicsview.viewport().setAcceptDrops(True)
        self.graphicsview.dragenter = self.dragEnterEvent
        self.graphicsview.dragmove = self.dragMoveEvent
        self.graphicsview.dragdrop = self.dropEvent
        self.graphicsview.onmove = self.mmoveEvent
        self.selectedpreset = None
        self.hoveredpreset = None

    def resizeEvent(self, event: QResizeEvent) -> None:
        # self.scene.setSceneRect(self.rect())
        r = self.graphicsview.sceneRect()
        # hacky workaround, if this wasnt here it would snap to 0,0 every time you shrinked the view by more than 1 pixel per frame
        r.setSize(event.size()/self.graphicsview.transform().m11() +
                  QSize(1000, 1000))
        self.graphicsview.setSceneRect(r)
        self.graphicsview.setFixedSize(event.size())
        r = self.graphicsview.sceneRect()
        r.setSize(event.size()/self.graphicsview.transform().m11())
        self.graphicsview.setSceneRect(r)
        # print(r)
        # print(self.graphicsview.)
        super().resizeEvent(event)
        # boundingrect = self.graphicsview.mapToScene(self.graphicsview.viewport().geometry()).boundingRect()
        # self.playbackcursor.setLine(QLine(playbackframe,boundingrect.top(),playbackframe,boundingrect.bottom()))

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        event.accept()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        if self.parentclass.draggedpreset:
            # print(self.parentclass.draggedpreset)
            if self.parentclass.draggedpreset in self.keyframes:
                self.parentclass.draggedpreset = None
                return super().mouseReleaseEvent(event)
            keyframe = self.parentclass.draggedpreset.copy()
            i = len(self.keyframes)
            self.keyframes.append(keyframe)
            self.drawnkeyframes[keyframe] = CzePresetKeyframeItem(keyframe)
            self.scene.addItem(self.drawnkeyframes[keyframe])
            self.drawnkeyframes[keyframe].setPos(
                (i % 6)*64+30, floor(i/6)*44+20)
            # self.drawnkeyframes[keyframe] = self.scene.addRect(QRectF(-9,-9,18,18),QPen(QColor(0,0,0),0),self.coolgradient)
            # self.drawnkeyframes[keyframe].setRotation(45)
            # self.drawnkeyframes[keyframe].setPos((i%6)*25,floor(i/6)*25)
            # self.drawnkeyframes[keyframe].setData(0,keyframe)
            self.parentclass.draggedpreset = None
        event.accept()

    def pressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            founditem: QGraphicsItem = self.graphicsview.itemAt(event.pos())
            if (self.selectedpreset):
                self.selectedpreset.setSelect(False)
            self.selectedpreset = founditem
            if (founditem):
                self.selectedpreset.setSelect(True)

                self.parentclass.timeline.deselectFrame()
                self.parentclass.keyframeoptions.regenerate(
                    self.selectedpreset.keyframe)

            else:
                self.parentclass.keyframeoptions.regenerate()
            self.graphicsview.update()
            self.parentclass.draggedpreset = None
        return super().mousePressEvent(event)

    def mmoveEvent(self, event: QMouseEvent, prevpos: QPoint) -> None:
        if not self.parentclass.draggedpreset and self.selectedpreset and event.buttons() & Qt.MouseButton.LeftButton:
            self.parentclass.draggedpreset = self.selectedpreset.keyframe.copy()
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.exec_(Qt.MoveAction)
        founditem: QGraphicsItem = self.graphicsview.itemAt(event.pos())
        if founditem != self.hoveredpreset:
            if self.hoveredpreset:
                self.hoveredpreset.setHovered(False)
            if isinstance(founditem, CzePresetKeyframeItem):
                self.hoveredpreset = founditem
                self.hoveredpreset.setHovered(True)
            elif founditem is None:
                self.hoveredpreset = founditem
            self.graphicsview.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if (event.key() == Qt.Key.Key_Delete and self.selectedpreset):
            self.keyframes.pop(self.keyframes.index(
                self.selectedpreset.keyframe))
            self.drawnkeyframes[self.selectedpreset.keyframe] = None
            self.scene.removeItem(self.selectedpreset)
            self.selectedpreset = None
