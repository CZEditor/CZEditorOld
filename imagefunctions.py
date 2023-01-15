from PIL import Image
from util import *
from generate import CreateXPWindow
from graphics import *
#import ffmpeg
from PySide6.QtCore import QByteArray,QBuffer,QIODevice
import pyspng
import numpy as np
from properties import *
loadedimages = {}
class NormalImage():
    name = "Image"
    params = Params(
        {
            "imagepath":FileProperty("")
        }
    )
    def image(param:Params,parentclass):
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
    def image(param:Params,parentclass):
        #return CreateFilledRectangle((param.width,param.height),tuple(param.color))
        made = np.full((param.width(),param.height(),4),np.array(param.color,dtype=np.uint8))
        return made,(param.width(),param.height())
    def __str__(self):
        return self.name
    def gethashstring(self,param:Params,parentclass):
        return self.name+str(param)
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
    def image(param:Params,parentclass):
        #fillindefaults(param,{"text":"","title":"","buttons":[],"buttonstyles":emptylist(0),"erroricon":Selectable(1,[["Critical Error","xp/Critical Error.png"],["Exclamation","xp/Exclamation.png"],["Information","xp/Information.png"],["Question","xp/Question.png"],["None",""]])})
        generated = CreateXPWindow(param)
        return np.array(generated),generated.size
    def __str__(self):
        return self.name
    def gethashstring(self,param:Params,parentclass):
        return self.name+str(param)
class SoundFile():
    name = "Sound"
    params = Params(
        {
            "path":""
        }
    )
    def image(param:Params,parentclass):
        return np.array(emptyimage),(1,1)
    def __str__(self):
        return self.name
    def gethashstring(self,param:Params,parentclass):
        return self.name+str(param)
class ImageSequence():
    name = "Image Sequence"
    params = Params({
        "imagespath":FileProperty("")
    })
    def image(param:Params,parentclass):
        #return Image.open(param.imagespath.replace("*",str(int(parentclass.playbackframe))))
        with open(param.imagespath().replace("*",str(int(parentclass.playbackframe))),"rb") as file:
            img = pyspng.load(file.read())
        return img,(img.shape[1],img.shape[0])
    def __str__(self):
        return self.name
    def gethashstring(self,param:Params,parentclass):
        return str(int(parentclass.playbackframe))+self.name+str(param)
class FFMPEGInput():
    name = "FFMPEG Input"
    params = Params({
        "path":""
    })
    def image(param:Params,parentclass):
        return openimage(param.imagespath.replace("*",str(int(parentclass.playbackframe))))
    def __str__(self):
        return self.name
    def gethashstring(self,param:Params,parentclass):
        return str(int(parentclass.playbackframe))+self.name+str(param)
imagefunctionsdropdown = [["Image",NormalImage],["Windows XP Error",XPError],["Filled Rectangle",FilledRectangle],["Sound",SoundFile],["Image Sequence",ImageSequence]]