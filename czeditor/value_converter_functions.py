from czeditor.util import Params
from czeditor.properties import *
from math import floor, ceil

valueConverterFunctions = []


class Converter:
    def __init_subclass__(cls):
        valueConverterFunctions.append([cls.name, cls])


class RoundFloatToInt(Converter):
    name = "Round Number"
    params = Params({
        "rounding": SelectableProperty([["Round down (floor)", floor], ["Round", round], ["Round up (ceil)", ceil]])
    })
    accepts = ["Float"]
    returns = ["Int"]

    def convert(params, number):
        return params.rounding()(number)
