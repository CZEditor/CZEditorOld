import cv2
import numpy as np
import moviepy.editor as mpy
from imagefunctions import NormalImage,XPText
from statefunctions import NormalKeyframe
from compositingfunctions import ImageComposite
from util import *
keyframes = []

class Keyframe():
    def image(self):
        return self.imagefunction(self.param)
    def state(self, statetomodify):
        return self.statefunction(statetomodify, self)
    def composite(self, canvas, image):
        return self.compositingfunction(canvas, image, self.param)
    def __init__(self, frame, param, imagefunction, statefunction, compositingfunction):
        self.frame = frame
        self.param = param
        self.imagefunction = imagefunction
        self.statefunction = statefunction
        self.compositingfunction = compositingfunction


def stateprocessor(keyframes):
    state = []
    for keyframe in keyframes:
        state = keyframe.state(state)
    return state

def composite(state):
    canvas = newimage(1280, 720)
    for keyframe in state:
        canvas = keyframe.composite(canvas, keyframe.image())
    return canvas

def frameprocessor(frame, keyframes):
    returnkeyframes = []
    for keyframe in keyframes:
        if keyframe.frame < frame:
            returnkeyframes.append(keyframe)
        else:
            break
    return returnkeyframes

keyframes.append(Keyframe(10, {"text":"dgkldfjldgk","x":100,"y":200}, XPText, NormalKeyframe, ImageComposite))
keyframes.append(Keyframe(70, {"text":"dgkldfjldgk","x":120,"y":220}, XPText, NormalKeyframe, ImageComposite))
keyframes.append(Keyframe(130, {"text":"dgkldfjldgk","x":140,"y":240}, XPText, NormalKeyframe, ImageComposite))


def getframeimage(i):
    global keyframes
    i = i * 60
    processedkeyframes = frameprocessor(i, keyframes)
    state = stateprocessor(processedkeyframes)
    image:Image = composite(state)
    return np.asarray(image.convert("RGB"))

def render(filename, length, keyframes):
    clip = mpy.VideoClip(getframeimage, duration=length / 60)
    #clip.write_videofile(filename=filename, fps=60, codec="libx264rgb", ffmpeg_params=["-strict","-2"]) perfection, doesnt embed | don't delete this
    clip.write_videofile(filename=filename, fps=60, codec="libvpx-vp9",ffmpeg_params=["-pix_fmt","yuv444p"],write_logfile=True) #perfection, embeds

render("video.mp4", 150, keyframes)