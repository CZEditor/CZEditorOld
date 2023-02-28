from czeditor.util import Params
from czeditor.properties import *


class StaticDecimalNumber:
    name = "Static Decimal Number"
    params = Params(
        {
            "value": FloatProperty(0)
        }
    )

    def getValue(params, frame):
        return params.value(frame)


valueProviderFunctions = [["Static Decimal Number", StaticDecimalNumber]]
