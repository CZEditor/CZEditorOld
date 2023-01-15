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

class FileProperty:
    def __init__(self,value):
        self._val = value
    def copy(self):
        return FileProperty(self._val)
    def __call__(self):
        return self._val
    def widget(self):
        return FilePropertyWidget(self)
    @property
    def val(self):
        return self._val
    @val.setter
    def val(self, value):
        self._val = value
    def set(self,value):
        self._val = value

class SecretProperty:
    def __init__(self,param):
        self._val = param.copy()
        self._originalparam = param.copy()
    def copy(self):
        return SecretProperty(self._originalparam.copy())
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