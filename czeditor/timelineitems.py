from PySide6.QtCore import QPointF, QRectF, Qt, QPoint
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent, QGraphicsItemGroup

from czeditor.keyframes import Keyframe
import czeditor.shared


class TimelineDurationLineItem(QGraphicsItem):
    def __init__(self, params, keyframe):
        super().__init__(None)
        self.params = params
        self.windowClass = czeditor.shared.windowObject
        self.keyframe = keyframe
        self.setPos(self.keyframe.frame, -self.keyframe.layer*25)
        self.setCursor(Qt.CursorShape.IBeamCursor)
        self.setAcceptedMouseButtons(Qt.MouseButton.RightButton)

    def boundingRect(self) -> QRectF:
        return QRectF(0, -4, self.params.params.duration(), 8)

    def paint(self, painter, option, widget):
        if not self.keyframe:
            return
        self.setPos(self.keyframe.frame, -self.keyframe.layer *
                    25+self.params.params.transient().handleHeight)
        painter.setPen(QPen(QColor(255, 255, 255, 127), 0))
        painter.drawLine(QPointF(0, 0), QPointF(
            self.params.params.duration(), 0))
        # print(self.params.params.duration())

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        scenepos = event.scenePos().toPoint()
        durationAfterKeyframe = scenepos.x()-self.keyframe.frame
        originalStartFrame = self.params.params.startframe()
        self.params.params.duration.set(
            self.params.params.duration()-durationAfterKeyframe)
        self.params.params.startframe.set(
            self.params.params.startframe()+durationAfterKeyframe)
        # print(self.params.params.duration(),self.params.params.startframe())
        self.windowClass.createKeyframe(
            Keyframe(scenepos.x(), self.keyframe.layer, self.keyframe.params.copy()))
        self.params.params.duration.set(durationAfterKeyframe)
        self.params.params.startframe.set(originalStartFrame)
        event.accept()
    


class TimelineVerticalLineItem(QGraphicsItem):
    def __init__(self, params, keyframe):
        super().__init__(None)
        self.params = params
        self.windowClass = czeditor.shared.windowObject
        self.keyframe = keyframe
        self.setPos(self.keyframe.frame, -self.keyframe.layer*25)
        self.setCursor(Qt.CursorShape.IBeamCursor)

    def boundingRect(self) -> QRectF:
        return QRectF(0, min(0, self.params.params.transient().handleHeight), 1, abs(self.params.params.transient().handleHeight))

    def paint(self, painter, option, widget):
        self.setPos(self.keyframe.frame, -self.keyframe.layer*25)
        painter.setPen(QPen(QColor(255, 255, 255), 0))
        painter.drawLine(QPointF(0, 0), QPointF(
            0, self.params.params.transient().handleHeight))
        # print(self.params.params.duration()


class TimelineDurationHandleItem(QGraphicsItem):
    def __init__(self, params, keyframe):
        super().__init__(None)
        self.params = params
        self.windowClass = czeditor.shared.windowObject
        self.keyframe = keyframe
        self.setPos(self.keyframe.frame+self.params.params.duration(), -
                    self.keyframe.layer*25+self.params.params.transient().handleHeight)
        self.setCursor(Qt.CursorShape.SizeHorCursor)
        self.setFlags(self.GraphicsItemFlag.ItemIgnoresTransformations)

    def boundingRect(self) -> QRectF:
        return QRectF(-3, -5, 3, 11)

    def paint(self, painter, option, widget):
        self.setPos(self.keyframe.frame+self.params.params.duration(), -
                    self.keyframe.layer*25+self.params.params.transient().handleHeight)
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawLines([QPoint(0,-5),QPoint(0,5),QPoint(0,5),QPoint(-5,0),QPoint(-5,0),QPoint(0,-5)])

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.origduration = self.params.params.duration()
        self.origheight = self.params.params.transient().handleHeight
        self.startpress = event.scenePos().toPoint()
        event.accept()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        scenepos = event.scenePos().toPoint()
        if abs(self.startpress.x()-scenepos.x()) > abs(self.startpress.y()-scenepos.y()):
            self.params.params.duration.set(max(1, min(self.params.params.transient(
            ).maxduration-self.params.params.startframe(), scenepos.x()-self.keyframe.frame)))
            self.params.params.transient().handleHeight = self.origheight
        else:
            self.params.params.transient().handleHeight = scenepos.y()+self.keyframe.layer*25
            self.params.params.duration.set(self.origduration)
        self.setPos(self.keyframe.frame+self.params.params.duration(), -
                    self.keyframe.layer*25+self.params.params.transient().handleHeight)
        event.accept()

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        scenepos = event.scenePos().toPoint()
        if abs(self.startpress.x()-scenepos.x()) > abs(self.startpress.y()-scenepos.y()):
            self.params.params.duration.set(max(1, min(self.params.params.transient(
            ).maxduration-self.params.params.startframe(), scenepos.x()-self.keyframe.frame)))
            self.params.params.transient().handleHeight = self.origheight
        else:
            self.params.params.transient().handleHeight = scenepos.y()+self.keyframe.layer*25
            self.params.params.duration.set(self.origduration)
        self.setPos(self.keyframe.frame+self.params.params.duration(), -
                    self.keyframe.layer*25+self.params.params.transient().handleHeight)
        event.accept()


class TimelineStartFrameHandleItem(QGraphicsItem):
    def __init__(self, params, keyframe):
        super().__init__(None)
        self.params = params
        self.windowClass = czeditor.shared.windowObject
        self.keyframe = keyframe
        self.setPos(self.keyframe.frame, -self.keyframe.layer*25)
        self.setCursor(Qt.CursorShape.SizeHorCursor)
        self.setFlags(self.GraphicsItemFlag.ItemIgnoresTransformations)

    def boundingRect(self) -> QRectF:
        return QRectF(0, -5, 3, 11)

    def paint(self, painter, option, widget):
        self.setPos(self.keyframe.frame, -self.keyframe.layer *
                    25+self.params.params.transient().handleHeight)
        painter.setPen(QPen(QColor(127, 127, 127), 1))
        painter.drawLines([QPoint(0,-5),QPoint(0,5),QPoint(0,5),QPoint(5,0),QPoint(5,0),QPoint(0,-5)])

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.origduration = self.params.params.duration()
        self.origheight = self.params.params.transient().handleHeight
        self.origstartframe = self.params.params.startframe()
        self.origframe = self.keyframe.frame
        self.startpress = event.scenePos().toPoint()
        event.accept()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        scenepos = event.scenePos().toPoint()
        if abs(self.startpress.x()-scenepos.x()) > abs(self.startpress.y()-scenepos.y()):
            self.params.params.startframe.set(min(self.params.params.transient().maxduration,
                                                self.origduration+self.origframe,
                                                self.origstartframe+scenepos.x()-self.origframe))
            self.params.params.startframe.set(
                max(0, self.params.params.startframe()))
            self.params.params.duration.set(min(self.params.params.transient(
            ).maxduration, self.origduration-scenepos.x()+self.origframe,self.origduration+self.origstartframe))
            self.params.params.duration.set(
                max(0, self.params.params.duration()))
            
            clampedpos = max(self.origframe -
                            self.origstartframe, scenepos.x())
            # print(self.keyframe.frame,self.params.params.startframe(),scenepos.x(),clampedpos)
            self.keyframe.frame = clampedpos
            self.windowClass.timeline.keyframes[self.keyframe].setPos(
                clampedpos, -self.keyframe.layer*25)
            self.params.params.transient().handleHeight = self.origheight
            self.setPos(clampedpos, -self.keyframe.layer*25 +
                        self.params.params.transient().handleHeight)
        else:
            self.params.params.duration.set(self.origduration)
            self.params.params.startframe.set(self.origstartframe)
            self.keyframe.frame = self.origframe
            self.windowClass.timeline.keyframes[self.keyframe].setPos(
                self.origframe, -self.keyframe.layer*25)
            self.params.params.transient().handleHeight = scenepos.y()+self.keyframe.layer*25
            self.setPos(self.keyframe.frame, -self.keyframe.layer*25 + self.params.params.transient().handleHeight)
        event.accept()

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        scenepos = event.scenePos().toPoint()
        if abs(self.startpress.x()-scenepos.x()) > abs(self.startpress.y()-scenepos.y()):
            self.params.params.startframe.set(min(self.params.params.transient().maxduration,
                                                self.origduration+self.origframe,
                                                self.origstartframe+scenepos.x()-self.origframe))
            self.params.params.startframe.set(
                max(0, self.params.params.startframe()))
            self.params.params.duration.set(min(self.params.params.transient(
            ).maxduration, self.origduration-scenepos.x()+self.origframe,self.origduration+self.origstartframe))
            self.params.params.duration.set(
                max(0, self.params.params.duration()))
            
            clampedpos = max(self.origframe -
                            self.origstartframe, scenepos.x())
            # print(self.keyframe.frame,self.params.params.startframe(),scenepos.x(),clampedpos)
            self.keyframe.frame = clampedpos
            self.windowClass.timeline.keyframes[self.keyframe].setPos(
                clampedpos, -self.keyframe.layer*25)
            self.params.params.transient().handleHeight = self.origheight
            self.setPos(clampedpos, -self.keyframe.layer*25 +
                        self.params.params.transient().handleHeight)
        else:
            self.params.params.duration.set(self.origduration)
            self.params.params.startframe.set(self.origstartframe)
            self.keyframe.frame = self.origframe
            self.windowClass.timeline.keyframes[self.keyframe].setPos(
                self.origframe, -self.keyframe.layer*25)
            self.params.params.transient().handleHeight = scenepos.y()+self.keyframe.layer*25
            self.setPos(self.keyframe.frame, -self.keyframe.layer*25 + self.params.params.transient().handleHeight)
        event.accept()


class TimelineDurationItem(QGraphicsItemGroup):
    def __init__(self, params, keyframe):
        super().__init__(None)
        self.keyframe = keyframe
        self.params = params
        self.addToGroup(TimelineDurationLineItem(self.params, self.keyframe))
        self.addToGroup(TimelineDurationHandleItem(self.params,self.keyframe))
        self.addToGroup(TimelineStartFrameHandleItem(self.params,self.keyframe))
        self.addToGroup(TimelineVerticalLineItem(self.params,self.keyframe))
        self.setHandlesChildEvents(False)