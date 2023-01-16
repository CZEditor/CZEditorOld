from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter,QPen,QColor
from PySide6.QtCore import QRectF,QPointF

class TimelineDurationLineItem(QGraphicsItem):
    def __init__(self,params,windowClass,keyframe):
        super().__init__(None)
        print("inited")
        self.params = params
        self.windowClass = windowClass
        self.keyframe = keyframe
    def boundingRect(self) -> QRectF:
        if(self.params.params.secrets().pimsobject):
            return QRectF(0,0,len(self.params.params.secrets().pimsobject)/self.params.params.secrets().pimsobject.frame_rate*60,1)
        return QRectF(0,0,1,1)
    def paint(self, painter, option, widget):
        self.setPos(self.keyframe.frame,0)
        if(self.params.params.secrets().pimsobject):
            painter.setPen(QPen(QColor(255,255,255),1))
            painter.drawLine(QPointF(0,0.5),QPointF(len(self.params.params.secrets().pimsobject)/self.params.params.secrets().pimsobject.frame_rate*60,0.5))
        #print(len(self.params.params.secrets().pimsobject))