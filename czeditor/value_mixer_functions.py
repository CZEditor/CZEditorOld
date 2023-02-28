from czeditor.util import Params
from czeditor.properties import *

class Constant:
    name = "Constant"
    params = Params({})

    def getValue(self, frame, length, a, b):
        return a

class FloatLerp:
    name = "Linear"
    params = Params({})

    def getValue(self, frame, length, a, b):
        return frame/length*b+(1-frame/length)*a

valueMixerFunctions = [["Constant",Constant],["Linear",FloatLerp]]