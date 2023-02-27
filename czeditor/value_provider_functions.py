from czeditor.util import Params
from properties import *

class StaticDecimalNumber:
    name = "Static Decimal Number"
    params = Params(
            {
                "value":FloatProperty(0)
            }
        )
    def __call__(params, frame):
        return params.value
