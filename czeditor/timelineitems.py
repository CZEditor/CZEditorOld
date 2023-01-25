from PySide6.QtWidgets import QGraphicsItem,QGraphicsSceneMouseEvent
from PySide6.QtGui import QPainter,QPen,QColor,QMouseEvent
from PySide6.QtCore import QRectF,QPointF,Qt
from czeditor.keyframes import Keyframe

class TimelineDurationLineItem(QGraphicsItem):
    def __init__(self,params,windowClass,keyframe):
        super().__init__(None)
        self.params = params
        self.windowClass = windowClass
        self.keyframe = keyframe
        self.setPos(self.keyframe.frame,0)
        self.setCursor(Qt.CursorShape.IBeamCursor)

    def boundingRect(self) -> QRectF:
        return QRectF(0,-2,self.params.params.duration(),2)

    def paint(self, painter, option, widget):
        self.setPos(self.keyframe.frame,self.params.params.transient().handleHeight)
        painter.setPen(QPen(QColor(255,255,255),0))
        painter.drawLine(QPointF(0,0),QPointF(self.params.params.duration(),0))
        #print(self.params.params.duration())

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        scenepos = event.scenePos().toPoint()
        durationAfterKeyframe = scenepos.x()-self.keyframe.frame
        originalStartFrame = self.params.params.startframe()
        self.params.params.duration.set(self.params.params.duration()-durationAfterKeyframe)
        self.params.params.startframe.set(self.params.params.startframe()+durationAfterKeyframe)
        #print(self.params.params.duration(),self.params.params.startframe())
        self.windowClass.createKeyframe(Keyframe(scenepos.x(),self.keyframe.params.copy()))
        self.params.params.duration.set(durationAfterKeyframe)
        self.params.params.startframe.set(originalStartFrame)
        event.accept()

class TimelineVerticalLineItem(QGraphicsItem):
    def __init__(self,params,windowClass,keyframe):
        super().__init__(None)
        self.params = params
        self.windowClass = windowClass
        self.keyframe = keyframe
        self.setPos(self.keyframe.frame,0)
        self.setCursor(Qt.CursorShape.IBeamCursor)

    def boundingRect(self) -> QRectF:
        return QRectF(0,min(0,self.params.params.transient().handleHeight),1,abs(self.params.params.transient().handleHeight))

    def paint(self, painter, option, widget):
        self.setPos(self.keyframe.frame,0)
        painter.setPen(QPen(QColor(255,255,255),0))
        painter.drawLine(QPointF(0,0),QPointF(0,self.params.params.transient().handleHeight))
        #print(self.params.params.duration()


class TimelineDurationHandleItem(QGraphicsItem):
    def __init__(self,params,windowClass,keyframe):
        super().__init__(None)
        self.params = params
        self.windowClass = windowClass
        self.keyframe = keyframe
        self.setPos(self.keyframe.frame+self.params.params.duration(),self.params.params.transient().handleHeight)
        self.setCursor(Qt.CursorShape.SizeHorCursor)

    def boundingRect(self) -> QRectF:
        return QRectF(-5,-5,9,9)

    def paint(self, painter, option, widget):
        self.setPos(self.keyframe.frame+self.params.params.duration(),self.params.params.transient().handleHeight)
        painter.setPen(QPen(QColor(255,255,255),1))
        painter.drawEllipse(QRectF(-5,-5,9,9))

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        event.accept()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        scenepos = event.scenePos().toPoint()
        self.params.params.duration.set(max(1,min(self.params.params.transient().maxduration,scenepos.x()-self.keyframe.frame)))
        self.params.params.transient().handleHeight = scenepos.y()
        self.setPos(self.keyframe.frame+self.params.params.duration(),self.params.params.transient().handleHeight)
        event.accept()

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        scenepos = event.scenePos().toPoint()
        self.params.params.duration.set(max(1,min(self.params.params.transient().maxduration,scenepos.x()-self.keyframe.frame)))
        self.params.params.transient().handleHeight = scenepos.y()
        self.setPos(self.keyframe.frame+self.params.params.duration(),self.params.params.transient().handleHeight)
        event.accept()


class TimelineStartFrameHandleItem(QGraphicsItem):
    def __init__(self,params,windowClass,keyframe):
        super().__init__(None)
        self.params = params
        self.windowClass = windowClass
        self.keyframe = keyframe
        self.setPos(self.keyframe.frame,0)
        self.setCursor(Qt.CursorShape.SizeHorCursor)

    def boundingRect(self) -> QRectF:
        return QRectF(-5,-5,9,9)

    def paint(self, painter, option, widget):
        self.setPos(self.keyframe.frame,self.params.params.transient().handleHeight)
        painter.setPen(QPen(QColor(127,127,127),1))
        painter.drawEllipse(QRectF(-5,-5,9,9))

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        event.accept()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        scenepos = event.scenePos().toPoint()
        self.params.params.duration.set(min(self.params.params.transient().maxduration,self.params.params.duration()-scenepos.x()+self.keyframe.frame))
        self.params.params.startframe.set(min(self.params.params.transient().maxduration,self.params.params.duration()+self.keyframe.frame,self.params.params.startframe()+scenepos.x()-self.keyframe.frame))
        self.params.params.duration.set(max(0,self.params.params.duration()))
        self.params.params.startframe.set(max(0,self.params.params.startframe()))
        clampedpos = max(self.keyframe.frame-self.params.params.startframe(),scenepos.x())
        #print(self.keyframe.frame,self.params.params.startframe(),scenepos.x(),clampedpos)
        self.keyframe.frame = clampedpos
        self.windowClass.timeline.keyframes[self.keyframe].setPos(clampedpos,0)
        self.params.params.transient().handleHeight = scenepos.y()
        self.setPos(clampedpos,self.params.params.transient().handleHeight)
        event.accept()

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        scenepos = event.scenePos().toPoint()
        self.params.params.duration.set(min(self.params.params.transient().maxduration,self.params.params.duration()-scenepos.x()+self.keyframe.frame))
        self.params.params.startframe.set(min(self.params.params.transient().maxduration,self.params.params.duration()+self.keyframe.frame,self.params.params.startframe()+scenepos.x()-self.keyframe.frame))
        self.params.params.duration.set(max(0,self.params.params.duration()))
        self.params.params.startframe.set(max(0,self.params.params.startframe()))
        clampedpos = min(self.keyframe.frame+self.params.params.duration(),max(self.keyframe.frame-self.params.params.startframe(),scenepos.x()))
        #print(self.keyframe.frame,self.params.params.startframe(),scenepos.x(),clampedpos)
        self.keyframe.frame = clampedpos
        self.windowClass.timeline.keyframes[self.keyframe].setPos(clampedpos,0)
        self.params.params.transient().handleHeight = scenepos.y()
        self.setPos(clampedpos,self.params.params.transient().handleHeight)
        
        event.accept()