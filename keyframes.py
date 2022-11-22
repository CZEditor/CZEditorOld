from typing import overload
from util import *
from imagefunctions import *
from statefunctions import *
from compositingfunctions import *

class Keyframe():
    def __init__(self, frame, param:Params):
        self.frame = frame
        self.params = param
        self.imageparams = param.image
        self.stateparams = param.states
        self.compositingparams = param.compositing
    def image(self):
        return self.imageparams.function.image(self.imageparams.params)
    def state(self, statetomodify):
        for stateparam in self.stateparams:
            statetomodify = stateparam.function.state(statetomodify,self)
        return statetomodify
    def composite(self, canvas, image):
        for compositingparam in self.compositingparams:
            canvas = compositingparam.function.composite(canvas,image,compositingparam)
        return canvas

class Keyframelist():
    def __init__(self):
        self.keyframes = []
        self.needssorting = False
    def add(self,keyframe:Keyframe) -> None:
        self.keyframes.append(keyframe)
        self.needssorting = True
    def append(self,keyframe:Keyframe) -> None:
        self.keyframes.append(keyframe)
        self.needssorting = True
    @overload
    def change(self,keyframe:Keyframe,change:Keyframe) -> None:
        ...
    @overload
    def change(self,i:int,change:Keyframe) -> None:
        ...
    def change(self,o,change:Keyframe) -> None:
        if isinstance(o,Keyframe):
            i = self.keyframes.index(o)
        else:
            i = o
        prevframe = self.keyframes[i].frame
        self.keyframes[i] = change
        self.needssorting = True
    @overload
    def remove(self,keyframe:Keyframe) -> None:
        ...
    @overload
    def remove(self,i:int) -> None:
        ...
    def remove(self,o) -> None:
        if isinstance(o,Keyframe):
            i = self.keyframes.index(o)
        else:
            i = o
        self.keyframes.pop(i)
    def pop(self,i:int) -> None:
        self.keyframes.pop(i)
    def len(self) -> int:
        return len(self.keyframes)
    def get(self,i) -> Keyframe:
        if self.needssorting:
            self.keyframes = sorted(self.keyframes,key=lambda k: k.frame)
            self.needssorting = False
        return keyframes[i]
    def __str__(self) -> str:
        if self.needssorting:
            self.keyframes = sorted(self.keyframes,key=lambda k: k.frame)
            self.needssorting = False
        return str(self.keyframes)
    def __getitem__(self,i:int) -> Keyframe:
        if self.needssorting:
            self.keyframes = sorted(self.keyframes,key=lambda k: k.frame)
            self.needssorting = False
        return self.keyframes[i]
    def __setitem__(self,i:int,change:Keyframe) -> None:
        prevframe = self.keyframes[i].frame
        self.keyframes[i] = change
        self.needssorting = True
    @overload
    def setframe(self,keyframe:Keyframe,frame:int):
        ...
    @overload
    def setframe(self,i:int,frame:int):
        ...
    def setframe(self,o,frame:int):
        if isinstance(o,Keyframe):
            i = self.keyframes.index(o)
        else:
            i = o
        prevframe = self.keyframes[i].frame
        self.keyframes[i].frame = frame
        self.needssorting = True
    def isinrange(self,i) -> bool:
        return len(self.keyframes) > i and i > 0
    def getsafe(self,i):
        if len(self.keyframes) > i and i > 0:
            return self.keyframes[i]
        else:
            return None
    def isin(self,keyframe:Keyframe) -> bool:
        return keyframe in self.keyframes


keyframes = Keyframelist()
keyframes.append(Keyframe(10, Params({"image":{"function":XPError,"params":{"text":"smoke","buttons":["yeah","lets go","Cancel"]}},"states":[{"function":NormalKeyframe,"params":{}}],"compositing":[{"function":ImageComposite,"params":{"x":100,"y":200}}]})))
keyframes.append(Keyframe(70, Params({"image":{"function":XPError,"params":{"text":"gdfgjdlgrgrelhjrtklhjgreg","buttons":["OK"]}},"states":[{"function":NormalKeyframe,"params":{}}],"compositing":[{"function":ImageComposite,"params":{"x":120,"y":220}}]})))
keyframes.append(Keyframe(130, Params({"image":{"function":XPError,"params":{"title":"Error","erroricon":"xp/Exclamation.png","buttons":["Yes","No"]}},"states":[{"function":NormalKeyframe,"params":{}}],"compositing":[{"function":ImageComposite,"params":{"x":140,"y":240}}]})))
