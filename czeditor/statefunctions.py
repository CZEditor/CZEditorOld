from czeditor.handles import (CzeViewportDraggableOffset,
                              CzeViewportDraggableOffsetLine)
from czeditor.properties import *
from czeditor.util import Params


class NormalKeyframe():
    name = "Media"
    params = Params({})

    def state(statetomodify, keyframe, stateparam, frame):
        if (keyframe.params.image.params.duration and keyframe.params.image.params.duration() != 0):
            if (keyframe.params.image.params.duration() < frame):
                return statetomodify
        statetomodify.append(keyframe)
        return statetomodify

    def __str__(self):
        return self.name


class ErrorKeyframe():
    name = "Windows Error"
    params = Params({})

    def state(statetomodify, keyframe, stateparam, frame):
        if statetomodify:
            statetomodify[-1].imageparams.params.active = False
        keyframe.imageparams.params.active = True
        # statetomodify.append(keyframe)
        return statetomodify

    def __str__(self):
        return self.name


class CascadeKeyframe():
    name = "Cascade"
    params = Params(
        {
            "x": IntProperty(16),
            "y": IntProperty(16)
        })

    def state(statetomodify, keyframe, stateparam, frame):
        if statetomodify:
            # get previous keyframe normal media params
            for lastkeyframe in statetomodify[-1].compositingparams:
                if lastkeyframe.function().params.x != None:
                    # get current keyframe normal media params
                    for currentkeyframe in keyframe.compositingparams:
                        if currentkeyframe.function().params.x != None:
                            # set current keyframe normal media params to previous keyframe normal media params and add x and y
                            currentkeyframe.params.x.set(
                                lastkeyframe.params.x()+stateparam.params.x())
                            currentkeyframe.params.y.set(
                                lastkeyframe.params.y()+stateparam.params.y())
                            break
                    break
        return statetomodify

    def handle(keyframe, parentclass, params):
        for currentkeyframe in keyframe.compositingparams:
            if currentkeyframe.function().params.x != None:
                return [CzeViewportDraggableOffset(None, parentclass, currentkeyframe.params.x, currentkeyframe.params.y, params.params.x, params.params.y), CzeViewportDraggableOffsetLine(None, parentclass, currentkeyframe.params.x, currentkeyframe.params.y, params.params.x, params.params.y)]
        return []

    def __str__(self):
        return self.name


statefunctionsdropdown = [["Media", NormalKeyframe], [
    "Windows Error", ErrorKeyframe], ["Cascade", CascadeKeyframe]]
