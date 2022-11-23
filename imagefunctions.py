from PIL import Image
from util import *
from generate import CreateXPWindow



class NormalImage():
    name = "Image"
    def image(param:Params):
        return openimage(param.imagepath)
    def __str__(self):
        return self.name
class XPError():
    name = "Windows XP Error"
    def image(param:Params):
        fillindefaults(param,{"text":"","title":"","buttons":[],"buttonstyles":emptylist(0),"erroricon":Selectable(1,[["Critical Error","xp/Critical Error.png"],["Exclamation","xp/Exclamation.png"],["Information","xp/Information.png"],["Question","xp/Question.png"],["None",""]])})
        return CreateXPWindow(param)
    def __str__(self):
        return self.name
imagefunctionsdropdown = [["Image",NormalImage],["Windows XP Error",XPError]]