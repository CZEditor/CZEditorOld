from PySide6.QtWidgets import QWidget,QGraphicsItem,QGraphicsSceneMouseEvent
from PySide6.QtGui import QPainter,QPen,QColor
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
        #return super().mouseMoveEvent(event)
    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.parentclass.updateviewportimage(self.parentclass.timestamp)
        return super().mouseReleaseEvent(event)