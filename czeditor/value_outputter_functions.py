from czeditor.util import Params
from czeditor.properties import *

valueOutputterFunctions = []


class Outputter:
    def __init_subclass__(cls):
        valueOutputterFunctions.append([cls.name, cls])


class Constant(Outputter):
    name = "Constant"
    params = Params({})
    output = ["Float"]

    def getValue(params, trackValues, keyframe, frame, nextKeyframes):
        values = keyframe.getValue(trackValues, frame)
        i = 0
        for value in values:
            trackValues[i]["value"] = value["value"]
            i += 1
        return trackValues


class FloatLerp(Outputter):
    name = "Linear"
    params = Params({})
    output = ["Float"]

    def getValue(params, trackValues, keyframe, frame, nextKeyframes):
        value = keyframe.getValue(trackValues, frame)
        i = 0
        for nextKeyframe in nextKeyframes:
            t = frame/(nextKeyframe.frame-keyframe.frame)
            trackValues[i]["value"] = value[i]["value"] * \
                (1-t)+nextKeyframe.getValue(trackValues, frame)[i]["value"]*t
            i += 1
        return trackValues
