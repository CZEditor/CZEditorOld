from PIL import Image
from util import ParamLink,Params
from handles import CzeViewportDraggableHandle
from PySide6.QtCore import QUrl
from PySide6.QtGui import QOpenGLContext
from OpenGL.GL import *
from time import time
import numpy as np
imagecache = {}
"""def cachecomposite(func,parentclass,width,height):
    global imagecache
    strparam = func.function().gethashstring(func.function(),func.params,parentclass)
    if strparam not in imagecache:
        imagecache[strparam] = func.function().image(func.params,parentclass).resize((width,height))
    return imagecache[strparam]"""

class ImageComposite():
    name = "Normal Media"
    params = {
        "x":0,
        "y":0,
        "width":1280,
        "height":720,
        "relativewidth":100,
        "relativeheight":100
    }
    def composite(canvas,imageparam,params,parentclass,keyframe):
        img = imageparam.function().image(imageparam.params,parentclass)
        params.params.width = int(img.size[0]*params.params.relativewidth/100) #put this in the onupdate function! make sure that it gets called only after the image has been updated
        params.params.height = int(img.size[1]*params.params.relativeheight/100)
        canvas.alpha_composite(img.resize((params.params.width,params.params.height),Image.Resampling.NEAREST),(params.params.x,params.params.y))
        return canvas
    def onupdate(self,imageparam,params,parentclass,keyframe):
        img = imageparam.function().image(imageparam.params,parentclass)
        params.params.width = int(img.size[0]*params.params.relativewidth/100)
        params.params.height = int(img.size[1]*params.params.relativeheight/100)
    def handle(keyframe,parentclass,params):
        return [CzeViewportDraggableHandle(None,parentclass,ParamLink(params.params,"x"),ParamLink(params.params,"y"))]
    def __str__(self):
        return self.name
class SoundFile():
    name = "Sound"
    params = Params({
        "volume":50,
        "lastplaying":False
    })
    def composite(canvas,imagefunction,params,parentclass,keyframe):
        if(not parentclass.isplaying):
            if(params.params.lastplaying):
                parentclass.player.pause()
            parentclass.player.setPosition(int(parentclass.playbackframe/60*1000))
            parentclass.player.setSource(QUrl.fromLocalFile(keyframe.imageparams.params.path))
            parentclass.audio_output.setVolume(float(params.params.volume))
            params.params.lastplaying = False
        elif(not params.params.lastplaying):
            parentclass.player.play()
            params.params.lastplaying = True
        return canvas
    def __str__(self):
        return self.name
class Unholy():
    name = "Unholy"
    params = {
        "x":0,
        "y":0,
        "width":1280,
        "height":720,
        "relativewidth":100,
        "relativeheight":100
    }
    def composite(canvas,imageparam,params,parentclass,keyframe):
        img = imageparam.function().image(imageparam.params,parentclass)
        #params.params.width = int(img.size[0]*params.params.relativewidth/100) #put this in the onupdate function! make sure that it gets called only after the image has been updated
        #params.params.height = int(img.size[1]*params.params.relativeheight/100)
        imgdata = np.array(img)[:,:,:3].flatten().tobytes()
        QOpenGLContext.create(QOpenGLContext)
        glClearColor(0.0,0.0,0.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        print("1")
        textid = glGenTextures(1)
        print("2")
        glBindTexture(GL_TEXTURE_2D,textid)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGB,img.size[0],img.size[1],0,GL_RGB,GL_UNSIGNED_BYTE,imgdata)
        print("5")
        glBindTexture(GL_TEXTURE_2D,0)
        print("4")
        glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,textid,0)
        pixels = bytearray(img.size[0]*img.size[1]*4)
        glBindFramebuffer(GL_FRAMEBUFFER,0)
        glReadPixels(0,0,img.size[0],img.size[1],GL_RGBA,GL_UNSIGNED_BYTE,pixels)
        glBindFramebuffer(GL_FRAMEBUFFER,0)
        print("3")
        #img.resize((params.params.width,params.params.height),Image.Resampling.NEAREST)
        canvas.alpha_composite(Image.frombytes("RGBA",(img.size[0],img.size[1]),pixels),(params.params.x,params.params.y))
        return canvas
    def onupdate(self,imageparam,params,parentclass,keyframe):
        img = imageparam.function().image(imageparam.params,parentclass)
        params.params.width = int(img.size[0]*params.params.relativewidth/100)
        params.params.height = int(img.size[1]*params.params.relativeheight/100)
    def handle(keyframe,parentclass,params):
        return [CzeViewportDraggableHandle(None,parentclass,ParamLink(params.params,"x"),ParamLink(params.params,"y"))]
    def __str__(self):
        return self.name
compositingfunctionsdropdown = [["Normal Media",ImageComposite],["Sound",SoundFile],["Unholy",Unholy]]