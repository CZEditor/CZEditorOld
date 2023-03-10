from czeditor.util import Params, SelectableItem
from czeditor.properties import *

valueProviderFunctions = []


class Provider:
    def __init_subclass__(cls):
        valueProviderFunctions.append(SelectableItem(cls.name, cls))


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
