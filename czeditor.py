from PIL import Image
from generate import *
from util import *


class Keyframe():
    def image(self):
        self.imagefunction(self.param)
    def state(self,statetomodify):
        self.statefunction(statetomodify,self.param)
    def __init__(self,param,imagefunction,statefunction):
        self.param = param
        self.imagefunction = imagefunction
        self.statefunction = statefunction