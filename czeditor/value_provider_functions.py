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

    def getValue(params, frame):
        return params.value(frame)



