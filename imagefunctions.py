from PIL import Image
from util import *
from generate import CreateXPWindow
from graphics import *
#import ffmpeg
from PySide6.QtCore import QByteArray,QBuffer,QIODevice

class NormalImage():
    name = "Image"
    params = Params(
        {
            "imagepath":""
        }
    )
    def image(param:Params,parentclass):
        return openimage(param.imagepath)
    def __str__(self):
        return self.name
    def gethashstring(self,param:Params,parentclass):
        return self.name+str(param)
class FilledRectangle():
    name = "Filled Rectangle"
    params = Params(
        {
            "width":100,
            "height":100,
            "color":[192,255,192]
        }
    )
    def image(param:Params,parentclass):
        return CreateFilledRectangle((param.width,param.height),tuple(param.color))
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
        return CreateXPWindow(param)
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
    def image(param:Params):
        return emptyimage
    def __str__(self):
        return self.name
    def gethashstring(self,param:Params,parentclass):
        return self.name+str(param)
class ImageSequence():
    name = "Image Sequence"
    params = Params({
        "imagespath":""
    })
    def image(param:Params,parentclass):
        return Image.open(param.imagespath.replace("*",str(int(parentclass.playbackframe))))

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