from czeditor.util import Params
from czeditor.properties import *

valueProviderFunctions = []


class Provider:
    def __init_subclass__(cls):
        valueProviderFunctions.append([cls.name, cls])


class StaticDecimalNumber(Provider):
    name = "Static Decimal Number"
    params = Params(
        {
            "value": FloatProperty(0)
        }
    )
    output = ["Float"]

    def getValue(params, trackValues, keyframe, frame):
        return [{"type": "Float", "value": params.value(frame)}]*len(trackValues)



