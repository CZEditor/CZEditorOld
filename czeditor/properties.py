from typing import Any, Union
from PySide6.QtWidgets import QMainWindow

from czeditor.property_widgets import *
from czeditor.animation_keyframes import *
from czeditor.util import Selectable, Params


class Property:
    def __init__(self, value):
        self._val = value
        self.associatedKeyframe = None

    def copy(self):
        return Property(self._val)

    def __call__(self):
        return self._val

    def set(self, value):
        self._val = value

    def associateKeyframe(self, keyframe):
        self.associatedKeyframe = keyframe


class IntProperty(Property):
    def __init__(self, value):
        self._val = value

    def copy(self):
        return IntProperty(self._val)

    def __call__(self):
        return self._val

    def widget(self, windowObject):
        return IntPropertyWidget(self, windowObject)

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, value):
        self._val = value

    def set(self, value):
        self._val = value


class StringProperty(Property):
    def __init__(self, value):
        self._val = value

    def copy(self):
        return StringProperty(self._val)

    def __call__(self):
        return self._val

    def widget(self, windowObject):
        return StringPropertyWidget(self, windowObject)

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, value):
        self._val = value

    def set(self, value):
        self._val = value

    def __str__(self):
        return self._val


class OpenWindowButtonProperty(Property):
    def __init__(self, button_name: str, window: QMainWindow, value: Any):
        """A property that's capable of opening a secondary window with a button."""
        self._val = value
        self.__button_name = button_name
        self.__window = window

    @property
    def btn_name(self) -> str:
        return self.__button_name

    @property
    def window(self) -> QMainWindow:
        return self.__window

    def copy(self):
        return OpenWindowButtonProperty(self.__button_name, self.__window, self._val)

    def widget(self, windowObject) -> OpenWindowButtonPropertyWidget:
        return OpenWindowButtonPropertyWidget(self, windowObject)

    def __call__(self):
        return self._val

    def __str__(self):
        return self._val


class LineStringProperty(Property):
    def __init__(self, value):
        self._val = value

    def copy(self):
        return LineStringProperty(self._val)

    def __call__(self):
        return self._val

    def widget(self, windowObject):
        return LineStringPropertyWidget(self, windowObject)

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, value):
        self._val = value

    def set(self, value):
        self._val = value

    def __str__(self):
        return self._val


class FileProperty(Property):
    def __init__(self, value, filetypes=""):
        self._val = value
        self._filetypes = filetypes

    def copy(self):
        return FileProperty(self._val, self._filetypes)

    def __call__(self):
        return self._val

    def widget(self, windowObject):
        return FilePropertyWidget(self, self._filetypes, windowObject)

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, value):
        self._val = value

    def set(self, value):
        self._val = value


class TransientProperty(Property):
    def __init__(self, param):
        self._val = param.copy()
        self._originalparam = param

    def copy(self):
        return TransientProperty(self._originalparam.copy())

    def __call__(self):
        return self._val

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, value):
        self._val = value

    def set(self, value):
        self._val = value


class SizeProperty(Property):
    def __init__(self, basewidth, baseheight, width, height):
        self._basewidth = basewidth
        self._baseheight = baseheight
        self._width = width
        self._height = height
        self._relativewidth = width/basewidth
        self._relativeheight = height/baseheight

    def copy(self):
        return SizeProperty(self._basewidth, self._baseheight, self._width, self._height)

    def __call__(self):
        return self._width, self._height

    def set(self, size):
        self._width = size[0]
        self._height = size[1]
        self._relativewidth = size[0]/self._basewidth
        self._relativeheight = size[1]/self._baseheight

    def setrelative(self, size):
        self._relativewidth = size[0]
        self._relativeheight = size[1]
        self._width = self._basewidth*size[0]
        self._height = self._baseheight*size[1]

    def setbase(self, size):
        self._basewidth = size[0]
        self._baseheight = size[1]
        self._width = self._basewidth*self._relativewidth
        self._height = self._baseheight*self._relativeheight

    def width(self):
        return self._width

    def height(self):
        return self._height

    def widget(self, windowObject):
        return SizePropertyWidget(self, windowObject)


class FloatProperty(Property):
    def __init__(self, value, timeline: Union[AnimationKeyframeList, None] = None):
        self._val = value
        self.timeline = timeline
        self.tracks = {0: {"type": "Float", "value": 0}}
        self.mixerFunctions = []
        self.providerFunctions = []
        self.compatibleTypes = ["Float", "Int"]

    def copy(self):
        return FloatProperty(self._val, self.timeline)

    def __call__(self, frame):
        if self.timeline is None:
            return self._val
        else:
            gotten = self.timeline.getValueAt(frame)
            if gotten is not None:
                return gotten[0]["value"]
            return self._val

    def widget(self, windowObject):
        return FloatPropertyWidget(self, windowObject)

    def defaultKeyframe(self, frame, tracks):
        from czeditor.value_outputter_functions import valueOutputterFunctions
        from czeditor.value_provider_functions import valueProviderFunctions

        return AnimationKeyframe(frame, [], tracks, Params(
            {
                "provider":
                {
                    "function": Selectable(0, valueProviderFunctions),
                    "params": Selectable(0, valueProviderFunctions)().params.copy()
                },
                "outputter":
                {
                    "function": Selectable(0, valueOutputterFunctions),
                    "params": Selectable(0, valueOutputterFunctions)().params.copy()
                }
            }
        ))

    def set(self, value):
        self._val = value

    def associateKeyframe(self, keyframe):
        if self.timeline:
            self.timeline.associatedKeyframe = keyframe
        return super().associateKeyframe(keyframe)


class SelectableProperty(Property):

    def __init__(self, options=[["None", None]], index=0):
        self._selectable = Selectable(index, options)

    def __call__(self):
        return self._selectable()

    def widget(self, windowObject):
        return SelectablePropertyWidget(self, windowObject)

    def set(self, value):
        self._selectable.index = value

    def copy(self):
        return SelectableProperty(self._selectable.copy().options, self._selectable.index)
