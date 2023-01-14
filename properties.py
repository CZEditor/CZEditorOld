from property_widgets import *


class IntProperty:
    def __init__(self,value):
        self._val = value
        self.propertywidget = None
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
    