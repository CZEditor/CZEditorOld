from PySide6.QtWidgets import QGraphicsItem,QGraphicsSceneMouseEvent
from PySide6.QtGui import QPainter,QPen,QColor,QMouseEvent
from PySide6.QtCore import QRectF,QPointF,Qt
from keyframes import Keyframe

class TimelineDurationLineItem(QGraphicsItem):
    def __init__(self,params,windowClass,keyframe):
        super().__init__(None)
        self.params = params
        self.windowClass = windowClass
        self.keyframe = keyframe
        self.setCursor(Qt.CursorShape.IBeamCursor)
    def boundingRect(self) -> QRectF:
        return QRectF(0,-1,self.params.params.duration(),1)
    def paint(self, painter, option, widget):
        self.setPos(self.keyframe.frame,0)
        painter.setPen(QPen(QColor(255,255,255),1))
        painter.drawLine(QPointF(0,0),QPointF(self.params.params.duration(),0))
        #print(self.params.params.duration())
    def pressEvent(self, scenepos) -> None:
        
        #print(scenepos.x())
        durationAfterKeyframe = scenepos.x()-self.keyframe.frame
        originalStartFrame = self.params.params.startframe()
        self.params.params.duration.set(self.params.params.duration()-durationAfterKeyframe)
        self.params.params.startframe.set(self.params.params.startframe()+durationAfterKeyframe)
        #print(self.params.params.duration(),self.params.params.startframe())
        self.windowClass.createKeyframe(Keyframe(scenepos.x(),self.keyframe.params.copy()))
        self.params.params.duration.set(durationAfterKeyframe)
        self.params.params.startframe.set(originalStartFrame)
        #print(self.params.params.duration(),self.params.params.startframe())