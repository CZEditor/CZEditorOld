from czeditor.handles import (CzeViewportDraggableOffset,
                              CzeViewportDraggableOffsetLine)
from czeditor.properties import *
from czeditor.util import Params


class NormalKeyframe():
    name = "Media"
    params = Params({})

    def action(statetomodify, keyframe, stateparam, frame, windowObject):
        if (keyframe.params.source.params.duration and keyframe.params.source.params.duration() != 0):
            if (keyframe.params.source.params.duration() < frame):
                return statetomodify
        statetomodify.append(keyframe)
        return statetomodify

    def __str__(self):
        return self.name


class ErrorKeyframe():
    name = "Windows Error"
    params = Params({})

    def action(statetomodify, keyframe, stateparam, frame, windowObject):
        if statetomodify:
            statetomodify[-1].imageparams.params.active = False
        keyframe.source.params.active = True
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

    def action(statetomodify, keyframe, stateparam, frame, windowObject):
        if statetomodify:
            # get previous keyframe normal media params
            for lastkeyframe in statetomodify[-1].params.effects:
                if lastkeyframe.function().params.x != None:
                    # get current keyframe normal media params
                    for currentkeyframe in keyframe.params.effects:
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
        for currentkeyframe in keyframe.params.effects:
            if currentkeyframe.function().params.x != None:
                return [CzeViewportDraggableOffset(None, parentclass, currentkeyframe.params.x, currentkeyframe.params.y, params.params.x, params.params.y), CzeViewportDraggableOffsetLine(None, parentclass, currentkeyframe.params.x, currentkeyframe.params.y, params.params.x, params.params.y)]
        return []

    def __str__(self):
        return self.name


class CameraMotionKeyframe():
    name = "Camera Motion"
    params = Params({
        "x": IntProperty(-640),
        "y": IntProperty(-360),
        "z": IntProperty(-360),
        "pitch": IntProperty(0),
        "yaw": IntProperty(0),
        "roll": IntProperty(0),
        "fov": IntProperty(90)
    })

    def action(statetomodify, keyframe, params, frame, windowObject):
        windowObject.cameraParams.x = params.params.x()
        windowObject.cameraParams.y = params.params.y()
        windowObject.cameraParams.z = params.params.z()
        windowObject.cameraParams.pitch = params.params.pitch()
        windowObject.cameraParams.yaw = params.params.yaw()
        windowObject.cameraParams.roll = params.params.roll()
        windowObject.cameraParams.fov = params.params.fov()
        return statetomodify


actionfunctionsdropdown = [["Media", NormalKeyframe], [
    "Windows Error", ErrorKeyframe], ["Cascade", CascadeKeyframe], ["Camera Motion", CameraMotionKeyframe]]
