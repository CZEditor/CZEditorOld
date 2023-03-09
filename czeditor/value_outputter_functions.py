from czeditor.util import Params
from czeditor.properties import *
from PySide6.QtGui import QPainter, QPainterPath
from PySide6.QtCore import QPoint, QRectF

valueOutputterFunctions = []


class Outputter:
    def __init_subclass__(cls):
        valueOutputterFunctions.append([cls.name, cls])

    def getOutputShape(params, track, bottom, top, keyframe, painter: QPainter):
        painter.drawPolygon(
            [QPoint(-7, 0), QPoint(0, -7), QPoint(7, 0), QPoint(0, 7)])

    def getInputShape(params, track, bottom, top, keyframe, painter: QPainter):
        painter.drawPolygon(
            [QPoint(-7, 0), QPoint(0, -7), QPoint(7, 0), QPoint(0, 7)])

    def getInputRect(params, track, keyframe):
        return QRectF(-7, -7, 15, 15)

    def getOutputRect(params, track, keyframe):
        return QRectF(-7, -7, 15, 15)


class Constant(Outputter):
    name = "Constant"
    params = Params({})
    outputs = ["Float"]
    inputs = []

    def getValue(params, trackValues, keyframe, frame, nextKeyframes):
        values = keyframe.getValue(trackValues, frame)
        return values
        
    def getOutputIcon(params, track, keyframe, painter:QPainter):
        painter.drawLines([QPoint(-2,2),QPoint(0,2),QPoint(0,2),QPoint(0,-2),QPoint(0,-2),QPoint(2,-2)])

class FloatLerp(Outputter):
    name = "Linear"
    params = Params({})
    outputs = ["Float"]
    inputs = []

    def getValue(params, trackValues, keyframe, frame, nextKeyframes):
        value = keyframe.getValue(trackValues, frame)
        if nextKeyframes:
            t = frame/max(frame, nextKeyframes[0].frame-keyframe.frame)
            return [{"type": "Float", "value": value[0]["value"] * (1-t)+nextKeyframes[0].getValue(trackValues, frame)[0]["value"]*t}]
        return value
    
    def getOutputIcon(params, track, keyframe, painter:QPainter):
        painter.drawLine(-2,2,2,-2)


class FloatSmoothInterpolation(Outputter):
    name = "Smooth 1"
    params = Params({})
    outputs = ["Float"]
    inputs = []

    def getValue(params, trackValues, keyframe, frame, nextKeyframes):
        value = keyframe.getValue(trackValues, frame)
        if nextKeyframes:
            t = frame/max(frame, nextKeyframes[0].frame-keyframe.frame)
            t = t*t*3-t*t*t*2
            return [{"type": "Float", "value": value[0]["value"] * (1-t)+nextKeyframes[0].getValue(trackValues, frame)[0]["value"]*t}]
        return value

    def getOutputIcon(params, track, keyframe, painter: QPainter):
        path = QPainterPath(QPoint(-4, 0))
        path.cubicTo(-2, 6, 2, -6, 4, 0)
        painter.drawPath(path)


class FloatAddition(Outputter):
    name = "Add"
    params = Params({})
    outputs = ["Float"]
    inputs = ["Float", "Float"]

    def getValue(params, trackValues, keyframe, frame, nextKeyframes):
        return [{"type": "Float", "value": trackValues[0]["value"] + trackValues[1]["value"]}]

    def getInputShape(params, track, bottom, top, keyframe, painter: QPainter):
        painter.drawPolygon(
            [QPoint(-3, 0), QPoint(-7, -4), QPoint(-7, -7+top), QPoint(-3, -7+top), QPoint(-3, -7), QPoint(0, -7), QPoint(0, 7), QPoint(-3, 7), QPoint(-3, 7+bottom), QPoint(-7, 7+bottom), QPoint(-7, 4)])
        #   CENTER           GO ↙️       ⬇️ to connect         ➡️ by 4           ⬆️ back         ➡️            ⬆️           ⬅️            ⬆️ to connect         ⬅️ by 4            ⬇️ back

    def getOutputShape(params, track, bottom, top, keyframe, painter: QPainter):
        painter.drawPolygon(
            [QPoint(-1, 7), QPoint(-1, -7), QPoint(0, -7), QPoint(7, 0), QPoint(0, 7)])

    def getInputRect(params, track, keyframe):
        return QRectF(-7, -7, 7, 15)

    def getOutputRect(params, track, keyframe):
        return QRectF(-1, -7, 8, 15)
