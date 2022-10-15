from PIL import Image
from util import *
from generate import CreateXPWindow
imagecache = {}

def cache(name,param,func):
    global imagecache
    tempparam = param.copy()
    del tempparam["x"]
    del tempparam["y"]
    strparam = name+":"+str(tempparam)
    if strparam not in imagecache:
        imagecache[strparam] = func()
    return imagecache[strparam]


def NormalImage(param):
    return openimage(param["imagepath"])

def XPText(param):
    return cache("XPText",param,lambda:CreateXPWindow(0,0,"",True,"","",param["text"]))