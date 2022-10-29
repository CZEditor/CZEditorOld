from PIL import Image
from util import *
from generate import CreateXPWindow



class NormalImage():
    name = "Image"
    def image(param:Params):
        return openimage(param.imagepath)
class XPError():
    name = "Windows XP Error"
    def image(param:Params):
        fillindefaults(param,{"text":"","title":"","buttons":[],"buttonstyles":[],"erroricon":""})
        return CreateXPWindow(param)