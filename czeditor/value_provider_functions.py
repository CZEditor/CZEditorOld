from czeditor.util import Params, SelectableItem
from czeditor.properties import *
from czeditor.code_edit_window import CodeEditWindow
from math import *
import czeditor.shared


class Provider:
    def __init_subclass__(cls):
        czeditor.shared.valueProviderFunctions[cls.__name__] = cls


class StaticDecimalNumber(Provider):
    name = "Static Decimal Number"
    params = Params(
        {
            "value": FloatProperty(0)
        }
    )
    output = ["Float"]

    def getValue(params, trackValues, keyframe, frame):
        return [{"type": "Float", "value": params.value(frame)}]


class MathProvider(Provider):
    name = "Math function"
    params = Params(
        {
            "function": OpenWindowButtonProperty("Edit Script...", CodeEditWindow, "sin(frame)")
        }
    )
    output = ["Float"]

    def getValue(params, trackValues, keyframe, frame):
        return [{"type": "Float", "value": eval(params.function(), globals(), {"frame": frame})}]


class StaticText(Provider):
    name = "Text"
    params = Params(
        {
            "value": StringProperty("")
        }
    )
    output = ["String"]

    def getValue(params, trackValues, keyframe, frame):
        return [{"type": "String", "value": params.value()}]
