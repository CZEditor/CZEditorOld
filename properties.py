from property_widgets import *


class IntProperty:
    def __init__(self,value):
        self._val = value
        
    def copy(self):
        return IntProperty(self._val)

    def __call__(self):
        return self._val

    def widget(self):
        return IntPropertyWidget(self)

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, value):
        self._val = value

    def set(self,value):
        self._val = value


class StringProperty:
    def __init__(self,value):
        self._val = value

    def copy(self):
        return StringProperty(self._val)

    def __call__(self):
        return self._val

    def widget(self):
        return StringPropertyWidget(self)

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, value):
        self._val = value

    def set(self,value):
        self._val = value

    def __str__(self):
        return self._val

class LineStringProperty:
    def __init__(self,value):
        self._val = value

    def copy(self):
        return LineStringProperty(self._val)

    def __call__(self):
        return self._val

    def widget(self):
        return LineStringPropertyWidget(self)

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, value):
        self._val = value

    def set(self,value):
        self._val = value

    def __str__(self):
        return self._val


class FileProperty:
    def __init__(self,value,filetypes=""):
        self._val = value
        self._filetypes = filetypes
        
    def copy(self):
        return FileProperty(self._val,self._filetypes)

    def __call__(self):
        return self._val

    def widget(self):
        return FilePropertyWidget(self,self._filetypes)

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, value):
        self._val = value

    def set(self,value):
        self._val = value


class TransientProperty:
    def __init__(self,param):
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

    def set(self,value):
        self._val = value


class SizeProperty():
    def __init__(self,basewidth,baseheight,width,height):
        self._basewidth = basewidth
        self._baseheight = baseheight
        self._width = width
        self._height = height
        self._relativewidth = width/basewidth
        self._relativeheight = height/baseheight
        
    def copy(self):
        return SizeProperty(self._basewidth,self._baseheight,self._width,self._height)

    def __call__(self):
        return self._width,self._height

    def set(self,size):
        self._width = size[0]
        self._height = size[1]
        self._relativewidth = size[0]/self._basewidth
        self._relativeheight = size[1]/self._baseheight

    def setrelative(self,size):
        self._relativewidth = size[0]
        self._relativeheight = size[1]
        self._width = self._basewidth*size[0]
        self._height = self._baseheight*size[1]

    def setbase(self,size):
        self._basewidth = size[0]
        self._baseheight = size[1]
        self._width = self._basewidth*self._relativewidth
        self._height = self._baseheight*self._relativeheight

    def width(self):
        return self._width

    def height(self):
        return self._height

    def widget(self):
        return SizePropertyWidget(self)


class FloatProperty:
    def __init__(self,value):
        self._val = value
        
    def copy(self):
        return FloatProperty(self._val)

    def __call__(self):
        return self._val

    def widget(self):
        return FloatPropertyWidget(self)

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, value):
        self._val = value

    def set(self,value):
        self._val = value
