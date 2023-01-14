from PySide6.QtWidgets import QWidget,QGraphicsItem,QGraphicsSceneMouseEvent,QGraphicsItemGroup
from PySide6.QtGui import QPainter,QPen,QColor,QTransform
from PySide6.QtCore import Qt,QRectF
from typing import *

class CzeViewportDraggableHandle(QGraphicsItem):
    def __init__(self,parent,parentclass,x,y):
        super().__init__(parent)
        self.xlink = x
        self.ylink = y
        self.parentclass = parentclass
        #self.setPos(self.x,self.y)
        
        self.setCursor(Qt.CursorShape.OpenHandCursor)
    def boundingRect(self) -> QRectF:
        return QRectF(-4,-4,7,7)
    def paint(self, painter: QPainter, option, widget: Optional[QWidget] = ...) -> None:
        #print(self.params)
        self.setPos(self.xlink()/1280*self.parentclass.picture.width(),self.ylink()/720*self.parentclass.picture.height())
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
            self.xlink.set(int(event.scenePos().x()/self.parentclass.picture.width()*1280))
            self.ylink.set(int(event.scenePos().y()/self.parentclass.picture.height()*720))
            self.setPos(self.xlink()/1280*self.parentclass.picture.width(),self.ylink()/720*self.parentclass.picture.height())
        event.accept()
        self.parentclass.updateviewportimage(self.parentclass.timestamp)
        self.parentclass.parentclass.updatekeyframeoptions()
        #return super().mouseMoveEvent(event)
    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.parentclass.updateviewportimage(self.parentclass.timestamp)
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
        self.setPos((self.xlink())/1280*self.parentclass.picture.width(),(self.ylink())/720*self.parentclass.picture.height())
        painter.setPen(QPen(QColor(255,255,255),1))
        #draw ellipse at the end
        painter.drawEllipse(QRectF(-5,-5,9,9))
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        #print(event.buttons())
        event.accept()
        #return super().mousePressEvent(event)
    def mouseMoveEvent(self, event:QGraphicsSceneMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.lengthx.set(self.lengthx()+int((event.scenePos().x()-event.lastScenePos().x())/self.parentclass.picture.width()*1280))
            self.lengthy.set(self.lengthy()+int((event.scenePos().y()-event.lastScenePos().y())/self.parentclass.picture.height()*720))
            self.setPos((self.xlink())/1280*self.parentclass.picture.width(),(self.ylink())/720*self.parentclass.picture.height())
        self.parentclass.scene.update()
        event.accept()
        #return super().mouseMoveEvent(event)
    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.parentclass.updateviewportimage(self.parentclass.timestamp)
        self.parentclass.update()
        self.parentclass.scene.update()
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
        self.setPos((self.xlink()-self.lengthx())/1280*self.parentclass.picture.width(),(self.ylink()-self.lengthy())/720*self.parentclass.picture.height())
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



