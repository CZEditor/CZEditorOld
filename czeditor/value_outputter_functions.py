from czeditor.util import Params
from czeditor.properties import *

valueOutputterFunctions = []


class Outputter:
    def __init_subclass__(cls):
        valueOutputterFunctions.append([cls.name, cls])


class Constant(Outputter):
    name = "Constant"
    params = Params({})
    outputs = ["Float"]
    inputs = []

    def getValue(params, trackValues, keyframe, frame, nextKeyframes):
        values = keyframe.getValue(trackValues, frame)
        return values


class FloatLerp(Outputter):
    name = "Linear"
    params = Params({})
    outputs = ["Float"]
    inputs = []

    def getValue(params, trackValues, keyframe, frame, nextKeyframes):
        value = keyframe.getValue(trackValues, frame)
        if nextKeyframes:
            t = frame/(nextKeyframes[0].frame-keyframe.frame)
            return [{"type": "Float", "value": value[0]["value"] * (1-t)+nextKeyframes[0].getValue(trackValues, frame)[0]["value"]*t}]
        return value


class FloatSmoothInterpolation(Outputter):
    name = "Smooth 1"
    params = Params({})
    outputs = ["Float"]
    inputs = []

    def getValue(params, trackValues, keyframe, frame, nextKeyframes):
        value = keyframe.getValue(trackValues, frame)
        if nextKeyframes:
            t = frame/(nextKeyframes[0].frame-keyframe.frame)
            t = t*t*3-t*t*t*2
            return [{"type": "Float", "value": value[0]["value"] * (1-t)+nextKeyframes[0].getValue(trackValues, frame)[0]["value"]*t}]
        return value

class FloatAddition(Outputter):
    name = "Add"
    params = Params({})
    outputs = ["Float"]
    inputs = ["Float", "Float"]

    def getValue(params, trackValues, keyframe, frame, nextKeyframes):
        return [{"type": "Float", "value": trackValues[0]["value"] + trackValues[1]["value"]}]
