from czeditor.util import Params
from czeditor.properties import *

valueMixerFunctions = []


class Mixer:
    def __init_subclass__(cls):
        valueMixerFunctions.append([cls.name, cls])


class Constant(Mixer):
    name = "Constant"
    params = Params({})

    def getValue(self, frame, length, a, b):
        return a


class FloatLerp(Mixer):
    name = "Linear"
    params = Params({})

    def getValue(self, frame, length, a, b):
        return frame/length*b+(1-frame/length)*a
