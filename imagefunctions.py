from PIL import Image
from util import *
from generate import CreateXPWindow



def NormalImage(param:Params):
    return openimage(param.imagepath)

def XPError(param:Params):
    fillindefaults(param,{"text":"","title":"","buttons":[],"buttonstyles":[],"erroricon":""})
    return CreateXPWindow(param)