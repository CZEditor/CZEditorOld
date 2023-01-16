from PySide6.QtWidgets import QWidget,QGraphicsItem,QGraphicsSceneMouseEvent,QGraphicsItemGroup
from PySide6.QtGui import QPainter,QPen,QColor,QTransform
from PySide6.QtCore import Qt,QRectF
from typing import *

class CzeViewportDraggableHandle(QGraphicsItem):
    def __init__(self,parent,parentclass,x,y):
        super().__init__(parent)
        self.xproperty = x
        self.yproperty = y
        self.parentclass = parentclass
        #self.setPos(self.x,self.y)
        
        self.setCursor(Qt.CursorShape.OpenHandCursor)
    def boundingRect(self) -> QRectF:
        return QRectF(-4,-4,7,7)
    def paint(self, painter: QPainter, option, widget: Optional[QWidget] = ...) -> None:
        #print(self.params)
        self.setPos(self.xproperty(),self.yproperty())
        painter.setPen(QPen(QColor(255,255,255),1))
        painter.drawEllipse(QRectF(-4,-4,7,7))
        #return super().paint(painter, option, widget)
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        #print(event.buttons())
        event.accept()
        #return super().mousePressEvent(event)
    def mouseMoveEvent(self, event:QGraphicsSceneMouseEvent) -> None:
        #print(event.buttons())
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.xproperty.set(int(event.scenePos().x()))
            self.yproperty.set(int(event.scenePos().y()))
            self.setPos(self.xproperty(),self.yproperty())
        event.accept()
        self.parentclass.updateviewport()
        self.parentclass.updatekeyframeoptions()
        #return super().mouseMoveEvent(event)
    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.parentclass.updateviewport()
        self.parentclass.updatekeyframeoptions()
        return super().mouseReleaseEvent(event)


class CzeViewportDraggableOffset(QGraphicsItem):
    def __init__(self,parent,parentclass,x,y,lengthx,lengthy):
        super().__init__(parent)
        self.parentclass = parentclass
        self.xlink = x
        self.ylink = y
        self.lengthx = lengthx
        self.lengthy = lengthy
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    #set the bounding rect
    def boundingRect(self) -> QRectF:
        return QRectF(-5,-5,9,9)
    def paint(self, painter, option, widget):
        self.setPos(self.xlink(),self.ylink())
        painter.setPen(QPen(QColor(255,255,255),1))
        #draw ellipse at the end
        painter.drawEllipse(QRectF(-5,-5,9,9))
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        #print(event.buttons())
        event.accept()
        #return super().mousePressEvent(event)
    def mouseMoveEvent(self, event:QGraphicsSceneMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.lengthx.set(self.lengthx()+int((event.scenePos().x()-event.lastScenePos().x())))
            self.lengthy.set(self.lengthy()+int((event.scenePos().y()-event.lastScenePos().y())))
            self.setPos(self.xlink(),self.ylink())
        #self.parentclass.scene.update()
        self.parentclass.updateviewport()
        self.parentclass.updatekeyframeoptions()
        event.accept()
        #return super().mouseMoveEvent(event)
    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.parentclass.updateviewport()
        self.parentclass.updatekeyframeoptions()
        #self.parentclass.update()
        #self.parentclass.scene.update()
        return super().mouseReleaseEvent(event)
    
class CzeViewportDraggableOffsetLine(QGraphicsItem):
    def __init__(self,parent,parentclass,x,y,lengthx,lengthy):
        super().__init__(parent)
        self.parentclass = parentclass
        self.xlink = x
        self.ylink = y
        self.lengthx = lengthx
        self.lengthy = lengthy
    def boundingRect(self) -> QRectF:
        return QRectF(0,0,self.lengthx(),self.lengthy())
    def paint(self, painter, option, widget):
        self.setPos(self.xlink()-self.lengthx(),self.ylink()-self.lengthy())
        painter.setPen(QPen(QColor(255,255,255),1))
        painter.drawLine(self.boundingRect().topLeft(),self.boundingRect().bottomRight())
        
"""class CzeViewportDraggableLine(QGraphicsItemGroup):
    def __init__(self,parent,parentclass,x,y,lengthx,lengthy):
        super().__init__(parent)
        self.addToGroup(CzeViewportDraggableOffsetLine(None,parentclass,x,y,lengthx,lengthy))
        self.addToGroup(CzeViewportDraggableOffset(None,parentclass,x,y,lengthx,lengthy))
    def paint(self,painter, option, widget):
        for child in self.childItems():
            child.paint(painter, option, widget)
    def mousePressEvent(self, event) -> None:
        #find child at position and redirect the event to it
        self.scene().itemAt(event.scenePos(),QTransform()).mousePressEvent(event)
    def mouseMoveEvent(self, event) -> None:
        self.scene().itemAt(event.scenePos(),QTransform()).mouseMoveEvent(event)
    def mouseReleaseEvent(self, event) -> None:
        self.scene().itemAt(event.scenePos(),QTransform()).mouseReleaseEvent(event)"""



