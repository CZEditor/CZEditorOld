from util import Params,ParamLink
from handles import CzeViewportDraggableOffsetLine,CzeViewportDraggableOffset
class NormalKeyframe():
    name = "Media"
    params = Params({})
    def state(statetomodify,keyframe,stateparam,frame):
        if(keyframe.params.image.params.duration and keyframe.params.image.params.duration() != 0):
            if(keyframe.params.image.params.duration() < frame):
                return statetomodify
        statetomodify.append(keyframe)
        return statetomodify
    def __str__(self):
        return self.name
class ErrorKeyframe():
    name = "Windows Error"
    params = Params({})
    def state(statetomodify,keyframe,stateparam,frame):
        if statetomodify:
            statetomodify[-1].imageparams.params.active = False
        keyframe.imageparams.params.active = True
        #statetomodify.append(keyframe)
        return statetomodify
    def __str__(self):
        return self.name
class CascadeKeyframe():
    name = "Cascade"
    params = Params(
        {
            "x":16,
            "y":16
        })
    def state(statetomodify,keyframe,stateparam,frame):
        if statetomodify:
            #get previous keyframe normal media params
            for lastkeyframe in statetomodify[-1].compositingparams:
                if lastkeyframe.function().name == "Normal Media":
                    #get current keyframe normal media params
                    for currentkeyframe in keyframe.compositingparams:
                        if currentkeyframe.function().name == "Normal Media":
                            #set current keyframe normal media params to previous keyframe normal media params and add x and y 
                            currentkeyframe.params.x = lastkeyframe.params.x+stateparam.params.x
                            currentkeyframe.params.y = lastkeyframe.params.y+stateparam.params.y
                            break
                    break
        return statetomodify
    def handle(keyframe,parentclass,params):
        for currentkeyframe in keyframe.compositingparams:
            if currentkeyframe.function().name == "Normal Media":
                return [CzeViewportDraggableOffset(None,parentclass,ParamLink(currentkeyframe.params,"x"),ParamLink(currentkeyframe.params,"y"),ParamLink(params.params,"x"),ParamLink(params.params,"y")),CzeViewportDraggableOffsetLine(None,parentclass,ParamLink(currentkeyframe.params,"x"),ParamLink(currentkeyframe.params,"y"),ParamLink(params.params,"x"),ParamLink(params.params,"y"))]
        
    def __str__(self):
        return self.name

statefunctionsdropdown = [["Media",NormalKeyframe],["Windows Error",ErrorKeyframe],["Cascade",CascadeKeyframe]]