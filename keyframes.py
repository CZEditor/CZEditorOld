from typing import overload
from util import *
import numpy as np

class Keyframe():
    def __init__(self, frame, param:Params):
        self.frame = frame
        self.params = param
        self.imageparams = param.image
        self.stateparams = param.states
        self.compositingparams = param.compositing
        self.shared = Params({})

    def image(self,parentclass):
        return self.imageparams.function().image(self.imageparams.params,parentclass,parentclass.playbackframe-self.frame)
    
    def state(self, statetomodify,windowClass): #action
        for stateparam in self.stateparams:
            statetomodify = stateparam.function().state(statetomodify,self,stateparam,windowClass.playbackframe-self.frame)
        return statetomodify
    
    def composite(self, image,parentclass=None):
        for compositingparam in self.compositingparams:
            if hasattr(compositingparam.function(),"composite"):
                compositingparam.function().composite(image,compositingparam,parentclass,self,parentclass.playbackframe-self.frame)
    
    def sound(self,sample):
        if hasattr(self.imageparams.function(),"sound"):
            source = self.imageparams.function().sound(self.imageparams.params,sample-int(self.frame/60*48000))
            for soundeffectparam in self.compositingparams:
                if hasattr(soundeffectparam.function(),"soundeffect"):
                    source = soundeffectparam.function().soundeffect(source,soundeffectparam,sample-int(self.frame/60*48000))
            return source
        return np.array(((0),(0))),48000

    def timelineitems(self):
        items = []
        for action in self.params.states:
            if hasattr(action.function(),"timelineitem"):
                items.append(action.function().timelineitem(action.params,self))
        for effect in self.params.compositing:
            if hasattr(effect.function(),"timelineitem"):
                items.append(effect.function().timelineitem(effect.params,self))
        return items
        
class Keyframelist():
    def __init__(self,windowClass):
        self.windowClass = windowClass
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
        return self.keyframes[i]
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
    def create(self,frame:int):
        addedkeyframe = Keyframe(frame,Params(
            {
                "image":
                {
                    "function":Selectable(0,self.windowClass.imagefunctionsdropdown),
                    "params":Selectable(0,self.windowClass.imagefunctionsdropdown)().params.copy()
                },
                "states":[],
                "compositing":[]
            }
        ))
        self.append(addedkeyframe)
        return addedkeyframe

"""keyframes.append(Keyframe(20,Params(
    {
        "image":
        {
            "function":Selectable(0,imagefunctionsdropdown),
            "params":{"imagepath":FileProperty("editor/icondark.png")}
        },
        "states":
        [
            {
                "function":Selectable(0,statefunctionsdropdown),
                "params":{}
            }
        ],
        "compositing":
        [
            {
                "function":Selectable(1,compositingfunctionsdropdown),
                "params":
                {
                    "x":IntProperty(0),
                    "y":IntProperty(0),
                    "z":IntProperty(0),
                    "width":IntProperty(1280),
                    "height":IntProperty(720),
                    "Xrotation":IntProperty(0),
                    "Yrotation":IntProperty(0),
                    "Zrotation":IntProperty(0),
                    "relativewidth":IntProperty(100),
                    "relativeheight":IntProperty(100),
                    "textureid":0,
                    "vbo":0,
                    "vao":0,
                    "pbo":0,
                    "lastsize":(32,32)

                }
            }
        ]
    })))"""
"""keyframes.append(Keyframe(40,Params(
    {
        "image":
        {
            "function":Selectable(0,imagefunctionsdropdown),
            "params":{"imagepath":"xp/Close button Active.png"}
        },
        "states":
        [
            {
                "function":Selectable(0,statefunctionsdropdown),
                "params":{}
            }
        ],
        "compositing":
        [
            {
                "function":Selectable(0,compositingfunctionsdropdown),
                "params":
                {
                    "x":500,
                    "y":400,
                }
            }
        ]
    })))
keyframes.append(Keyframe(60,Params(
    {
        "image":
        {
            "function":Selectable(0,imagefunctionsdropdown),
            "params":{"imagepath":"xp/Information.png"}
        },
        "states":
        [
            {
                "function":Selectable(0,statefunctionsdropdown),
                "params":{}
            }
        ],
        "compositing":
        [
            {
                "function":Selectable(0,compositingfunctionsdropdown),
                "params":
                {
                    "x":500,
                    "y":400,
                }
            }
        ]
    })))
keyframes.append(Keyframe(80,Params(
    {
        "image":
        {
            "function":Selectable(0,imagefunctionsdropdown),
            "params":{"imagepath":"xp/Exclamation.png"}
        },
        "states":
        [
            {
                "function":Selectable(0,statefunctionsdropdown),
                "params":{}
            }
        ],
        "compositing":
        [
            {
                "function":Selectable(0,compositingfunctionsdropdown),
                "params":
                {
                    "x":500,
                    "y":400,
                }
            }
        ]
    })))"""
#keyframes.append(Keyframe(10, Params({"image":{"function":Selectable(1,imagefunctionsdropdown),"params":{"text":"smoke","buttons":["yeah","lets go","Cancel"]}},"states":[{"function":Selectable(0,statefunctionsdropdown),"params":{}}],"compositing":[{"function":Selectable(0,compositingfunctionsdropdown),"params":{"x":100,"y":200}}]})))
#keyframes.append(Keyframe(70, Params({"image":{"function":Selectable(1,imagefunctionsdropdown),"params":{"text":"gdfgjdlgrgrelhjrtklhjgreg","buttons":["OK"]}},"states":[{"function":Selectable(0,statefunctionsdropdown),"params":{}}],"compositing":[{"function":Selectable(0,compositingfunctionsdropdown),"params":{"x":120,"y":220}}]})))
#keyframes.append(Keyframe(130, Params({"image":{"function":Selectable(1,imagefunctionsdropdown),"params":{"title":"Error","erroricon":Selectable(1,[["Critical Error","xp/Critical Error.png"],["Exclamation","xp/Exclamation.png"],["Information","xp/Information.png"],["Question","xp/Question.png"],["None",""]]),"buttons":["Yes","No"]}},"states":[{"function":Selectable(0,statefunctionsdropdown),"params":{}}],"compositing":[{"function":Selectable(0,compositingfunctionsdropdown),"params":{"x":140,"y":240}}]})))
