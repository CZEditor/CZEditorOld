from PIL import Image
from util import *
from generate import CreateXPWindow
from graphics import *


class NormalImage():
    name = "Image"
    params = Params(
        {
            "imagepath":""
        }
    )
    def image(param:Params):
        return openimage(param.imagepath)
    def __str__(self):
        return self.name
class FilledRectangle():
    name = "Filled Rectangle"
    params = Params(
        {
            "width":100,
            "height":100,
            "color":[192,255,192]
        }
    )
    def image(param:Params):
        return CreateFilledRectangle((param.width,param.height),tuple(param.color))
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
    def image(param:Params):
        #fillindefaults(param,{"text":"","title":"","buttons":[],"buttonstyles":emptylist(0),"erroricon":Selectable(1,[["Critical Error","xp/Critical Error.png"],["Exclamation","xp/Exclamation.png"],["Information","xp/Information.png"],["Question","xp/Question.png"],["None",""]])})
        return CreateXPWindow(param)
    def __str__(self):
        return self.name
imagefunctionsdropdown = [["Image",NormalImage],["Windows XP Error",XPError],["Filled Rectangle",FilledRectangle]]