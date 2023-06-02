from typing import Any, Union
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QFont

from czeditor.property_widgets import *
from czeditor.animation_keyframes import *
from czeditor.util import Selectable, Params, SelectableItem
import czeditor.shared

class Property:
    def __init__(self, value):
        self._val = value
        self.associatedKeyframe = None

    def __init_subclass__(cls):
        czeditor.shared.deserializable[cls.__name__] = cls

    def copy(self):
        return Property(self._val)

    def __call__(self):
        return self._val

    def set(self, value):
        self._val = value

    def associateKeyframe(self, keyframe):
        self.associatedKeyframe = keyframe

    def serialize(self):
        return {"value": self._val}

    def deserialize(data):
        return __class__(data["value"])


class IntProperty(Property):
    def __init__(self, value, timeline: Union[AnimationKeyframeList, None] = None):
        self._val = value
        self.timeline = timeline
        self.tracks = {0: {"type": "Int", "value": 0}}
        self.mixerFunctions = []
        self.providerFunctions = []
        self.compatibleTypes = ["Float", "Int"]
        self.currentvalue = 0
        self.lastframe = 0
        self.associatedKeyframe = None

    def copy(self):
        return IntProperty(self._val, self.timeline)

    def __call__(self):
        frame = czeditor.shared.windowObject.playbackframe
        if self.timeline is None:
            self.currentvalue = self._val
            return self._val
        else:
            if self.lastframe == frame:
                return self.currentvalue
            self.lastframe = frame
            gotten = self.timeline.getValueAt(frame)
            if gotten is not None:
                self.currentvalue = gotten[0]["value"]
                return self.currentvalue

            self.currentvalue = self._val
            return self.currentvalue

    def widget(self, windowObject, updateParamsFunction):
        return IntPropertyWidget(self, windowObject, updateParamsFunction)

    def defaultKeyframe(self, frame, tracks):
        
        sortedValueProviderFunctions = [i for i in czeditor.shared.valueProviderFunctions.values()]
        sortedValueOutputterFunctions = [i for i in czeditor.shared.valueOutputterFunctions.values()]
        return AnimationKeyframe(frame, [], tracks, Params(
            {
                "provider":
                {
                    "function": Selectable(0, [SelectableItem(i.name,i) for i in sortedValueProviderFunctions]),
                    "params": sortedValueProviderFunctions[0].params.copy()
                },
                "outputter":
                {
                    "function": Selectable(0, [SelectableItem(i.name,i) for i in sortedValueOutputterFunctions]),
                    "params": sortedValueOutputterFunctions[0].params.copy()
                }
            }
        ))

    def set(self, value):
        self._val = value

    def associateKeyframe(self, keyframe):
        if self.timeline:
            self.timeline.associatedKeyframe = keyframe
        return super().associateKeyframe(keyframe)

    def serialize(self):
        if self.timeline:
            return {"value": self._val, "timeline": self.timeline.serialize()}
        return {"value": self._val}
    
    def deserialize(data):
        if "timeline" in data:
            return __class__(data["value"],AnimationKeyframeList.deserialize(data["timeline"]))
        return __class__(data["value"])


class StringProperty(Property):
    def __init__(self, value):
        self._val = value

    def copy(self):
        return StringProperty(self._val)

    def __call__(self):
        return self._val

    def widget(self, windowObject, updateParamsFunction):
        return StringPropertyWidget(self, windowObject, updateParamsFunction)

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

    def deserialize(data):
        return __class__(data["value"])


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

    def widget(self, windowObject, updateParamsFunction) -> OpenWindowButtonPropertyWidget:
        return OpenWindowButtonPropertyWidget(self, windowObject, updateParamsFunction)

    def __call__(self):
        return self._val

    def __str__(self):
        return self._val

    def deserialize(data):
        from czeditor.code_edit_window import CodeEditWindow
        return __class__("Edit Script...", CodeEditWindow, data["value"]) # Why would you do it like that? This only complicates saving! TODO :Support other types of windows.


class LineStringProperty(Property):
    def __init__(self, value):
        self._val = value

    def copy(self):
        return LineStringProperty(self._val)

    def __call__(self):
        return self._val

    def widget(self, windowObject,updateParamsFunction):
        return LineStringPropertyWidget(self, windowObject,updateParamsFunction)

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

    def deserialize(data):
        return __class__(data["value"])

class FileProperty(Property):
    def __init__(self, value, filetypes=""):
        self._val = value
        self._filetypes = filetypes

    def copy(self):
        return FileProperty(self._val, self._filetypes)

    def __call__(self):
        return self._val

    def widget(self, windowObject,updateParamsFunction):
        return FilePropertyWidget(self, self._filetypes, windowObject,updateParamsFunction)

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, value):
        self._val = value

    def set(self, value):
        self._val = value
    
    def serialize(self):
        return {"value":self._val,"filetypes":self._filetypes}

    def deserialize(data):
        return __class__(data["value"],data["filetypes"])
        


class TransientProperty(Property):
    def __init__(self, param):
        self._val = param.copy()
        self._originalparam = param
        self._dontserialize = True

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

    def widget(self, windowObject,updateParamsFunction):
        return SizePropertyWidget(self, windowObject,updateParamsFunction)

    def serialize(self):
        return {"basewidth": self._basewidth, "baseheight": self._baseheight, "width": self._width, "height": self._height}

    def deserialize(data):
        return __class__(data["basewidth"],data["baseheight"],data["width"],data["height"])

class FloatProperty(Property):
    def __init__(self, value, timeline: Union[AnimationKeyframeList, None] = None):
        self._val = value
        self.timeline = timeline
        self.tracks = {0: {"type": "Float", "value": 0}}
        self.mixerFunctions = []
        self.providerFunctions = []
        self.compatibleTypes = ["Float", "Int"]
        self.currentvalue = 0
        self.lastframe = 0
        self.associatedKeyframe = None

    def copy(self):
        return FloatProperty(self._val, self.timeline)

    def __call__(self):
        frame = czeditor.shared.windowObject.playbackframe
        if self.timeline is None:
            self.currentvalue = self._val
            return self._val
        else:
            if self.lastframe == frame:
                return self.currentvalue
            self.lastframe = frame
            gotten = self.timeline.getValueAt(frame)
            if gotten is not None:
                self.currentvalue = gotten[0]["value"]
                return self.currentvalue

            self.currentvalue = self._val
            return self.currentvalue

    def widget(self, windowObject,updateParamsFunction):
        return FloatPropertyWidget(self, windowObject,updateParamsFunction)

    def defaultKeyframe(self, frame, tracks):
        
        sortedValueProviderFunctions = [i for i in czeditor.shared.valueProviderFunctions.values()]
        sortedValueOutputterFunctions = [i for i in czeditor.shared.valueOutputterFunctions.values()]
        return AnimationKeyframe(frame, [], tracks, Params(
            {
                "provider":
                {
                    "function": Selectable(0, [SelectableItem(i.name,i) for i in sortedValueProviderFunctions]),
                    "params": sortedValueProviderFunctions[0].params.copy()
                },
                "outputter":
                {
                    "function": Selectable(0, [SelectableItem(i.name,i) for i in sortedValueOutputterFunctions]),
                    "params": sortedValueOutputterFunctions[0].params.copy()
                }
            }
        ))

    def set(self, value):
        self._val = value

    def associateKeyframe(self, keyframe):
        if self.timeline:
            self.timeline.associatedKeyframe = keyframe
        return super().associateKeyframe(keyframe)

    def serialize(self):
        if self.timeline:
            return {"value": self._val, "timeline": self.timeline.serialize()}
        return {"value": self._val}
    
    def deserialize(data):
        if "timeline" in data:
            return __class__(data["value"],AnimationKeyframeList.deserialize(data["timeline"]))
        return __class__(data["value"])


class SelectableProperty(Property):

    def __init__(self, options=[SelectableItem()], index=0):
        self._selectable = Selectable(index, options)

    def __call__(self):
        return self._selectable()

    def widget(self, windowObject,updateParamsFunction):
        return SelectablePropertyWidget(self, windowObject,updateParamsFunction)

    def set(self, value):
        self._selectable.index = value

    def copy(self):
        return SelectableProperty(self._selectable.copy().options, self._selectable.index)

    def serialize(self):
        return {"values":[v.serialize() for v in self._selectable.options],"index":self._selectable.index}

    def deserialize(data):
        return __class__([SelectableItem.deserialize(i) for i in data["values"]],data["index"])


class RGBProperty(Property):
    def __init__(self, R, G, B, A=255):
        self._r = R
        self._g = G
        self._b = B
        self._a = A

    def __call__(self):
        return self._r, self._g, self._b, self._a

    def set(self, R, G, B, A=255):
        self._r = R
        self._g = G
        self._b = B
        self._a = A

    def copy(self):
        return RGBProperty(self._r, self._g, self._b, self._a)

    def widget(self, windowObject,updateParamsFunction):
        return RGBPropertyWidget(self, windowObject,updateParamsFunction)

    def serialize(self):
        return {"R": self._r, "G": self._g, "B": self._b, "A": self._a}
    
    def deserialize(data):
        return __class__(data["R"],data["G"],data["B"],data["A"])


class FontProperty(Property):
    def __init__(self, font):
        self.font = font
        self._font = QFont(font)

    def __call__(self):
        return self._font

    def set(self, font):
        self.font = font
        self._font = QFont(font)

    def copy(self):
        return FontProperty(self.font)

    def widget(self, windowObject, updateParamsFunction):
        return FontPropertyWidget(self, windowObject, updateParamsFunction)

    def serialize(self):
        return {"font": self.font}

    def deserialize(data):
        return __class__(data["font"])
