from PIL import Image
from util import *
from generate import CreateXPWindow
from graphics import *
#import ffmpeg
from PySide6.QtCore import QByteArray,QBuffer,QIODevice
import pyspng
import pims
import numpy as np
from properties import *
import os
import av

loadedimages = {}
class NormalImage():
    name = "Image"
    params = Params(
        {
            "imagepath":FileProperty("")
        }
    )
    def image(param:Params,parentclass,frame):
        path = param.imagepath()
        if(path in loadedimages):
            img = loadedimages[path]
            return img,(img.shape[1],img.shape[0])
        try:
            with open(path,"rb") as file:
                img = pyspng.load(file.read())
            loadedimages[path] = img
            if(len(loadedimages.keys()) > 300):
                del loadedimages[loadedimages.keys()[0]]

            return img,(img.shape[1],img.shape[0])
        except:
            return np.array([[[0,0,0,0]]]),(1,1)
    def __str__(self):
        return self.name
    def gethashstring(self,param:Params,parentclass):
        return self.name+str(param)
class FilledRectangle():
    name = "Filled Rectangle"
    params = Params(
        {
            "width":IntProperty(32),
            "height":IntProperty(32),
            "color":[192,255,192,255]
        }
    )
    def image(param:Params,parentclass,frame):
        #return CreateFilledRectangle((param.width,param.height),tuple(param.color))
        made = np.full((param.width(),param.height(),4),np.array(param.color,dtype=np.uint8))
        return made,(param.width(),param.height())
    def __str__(self):
        return self.name
class XPError():
    name = "Windows XP Error"
    params = Params(
        {
            "text":"",
            "title":"",
            "buttons":StringList([]),
            "buttonstyles":emptylist(0),
            "erroricon":Selectable(1,[
                ["Critical Error","xp/Critical Error.png"],
                ["Exclamation","xp/Exclamation.png"],
                ["Information","xp/Information.png"],
                ["Question","xp/Question.png"],
                ["None",""]])
        }
    )
    def image(param:Params,parentclass,frame):
        #fillindefaults(param,{"text":"","title":"","buttons":[],"buttonstyles":emptylist(0),"erroricon":Selectable(1,[["Critical Error","xp/Critical Error.png"],["Exclamation","xp/Exclamation.png"],["Information","xp/Information.png"],["Question","xp/Question.png"],["None",""]])})
        generated = CreateXPWindow(param)
        return np.array(generated),generated.size
    def __str__(self):
        return self.name
class SoundFile():
    name = "Sound"
    params = Params(
        {
            "path":""
        }
    )
    def image(param:Params,parentclass,frame):
        return np.array(emptyimage),(1,1)
    def __str__(self):
        return self.name
class ImageSequence():
    name = "Image Sequence"
    params = Params({
        "imagespath":FileProperty("")
    })
    def image(param:Params,parentclass,frame):
        #return Image.open(param.imagespath.replace("*",str(int(parentclass.playbackframe))))
        with open(param.imagespath().replace("*",str(int(frame))),"rb") as file:
            img = pyspng.load(file.read())
        return img,(img.shape[1],img.shape[0])
    def __str__(self):
        return self.name
class Video():
    name = "Video"
    params = Params({
        "videopath":FileProperty(""),
        "startframe":IntProperty(0),
        "secrets":SecretProperty(Params({
            "pimsobject":None,
            "avobject":None,
            "decodedaudio":None,
            "lastpath":""}))
    })
    def image(param:Params,parentclass,frame):
        #return Image.open(param.imagespath.replace("*",str(int(parentclass.playbackframe))))
        secrets = param.secrets()
        if(not os.path.exists(param.videopath())):
            return np.array(emptyimage),(1,1)
        if(param.videopath() != secrets.lastpath or secrets.pimsobject == None):
            secrets.pimsobject = pims.PyAVVideoReader(param.videopath())
            secrets.avobject = av.open(param.videopath())
            secrets.lastpath = param.videopath()
        frame += param.startframe()
        frame = int(frame/60*secrets.pimsobject.frame_rate)
        if(frame >= len(secrets.pimsobject) or frame < 0):
            return np.array(emptyimage),(1,1)
        img = secrets.pimsobject[int(frame)]
        img = np.pad(img,((0,0),(0,0),(0,1)),mode="constant",constant_values=255) # TODO : Maybe support alpha videos?
        return img,(img.shape[1],img.shape[0])
    def sound(param:Params,frame):
        secrets = param.secrets()
        if(not os.path.exists(param.videopath())):
            return np.array((0)),1
        if(param.videopath() != secrets.lastpath or secrets.avobject == None):
            secrets.pimsobject = pims.PyAVVideoReader(param.videopath())
            secrets.avobject = av.open(param.videopath())
            secrets.lastpath = param.videopath()
        frame += param.startframe()
        #print(secrets.avobject.streams.audio[0].duration)
        #print(frame/60/secrets.avobject.streams.audio[0].time_base)
        #secrets.avobject.seek(int(frame/60/secrets.avobject.streams.audio[0].time_base),any_frame=True)
        for frame in secrets.avobject.decode(secrets.avobject.streams.audio[0]):
            #print(frame.to_ndarray())
            return np.array(frame.to_ndarray()),secrets.avobject.streams.audio[0]
    def __str__(self):
        return self.name
imagefunctionsdropdown = [["Image",NormalImage],["Windows XP Error",XPError],["Filled Rectangle",FilledRectangle],["Sound",SoundFile],["Image Sequence",ImageSequence],["Video",Video]]