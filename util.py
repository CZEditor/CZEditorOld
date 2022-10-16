from PIL import Image

openedimages = {}
newimages = {}
def openimage(s):
    if s not in openedimages:
        openedimages[s] = Image.open(s).convert("RGBA")
    return openedimages[s].copy()
def newimage(w,h,r=0,g=0,b=0,a=255):
    cachestr = f"{w},{h},{r},{g},{b},{a}"
    if cachestr not in newimages:
        newimages[cachestr] = Image.new("RGBA",(w,h),(r,g,b,a))
    return newimages[cachestr].copy()

class Params(object):
    def __init__(self,params:dict,**kwargs):
        for k in params.keys():
            setattr(self,k,params[k])
        for k in kwargs:
            setattr(self,k,kwargs[k])
    def __getattr__(self,param:str):
        return None
    def copy(self):
        return Params(vars(self))
    def __str__(self):
        return str(vars(self))

def fillindefaults(param,defaults):
    for key in defaults.keys():
        if getattr(param,key) == None:
            setattr(param,key,defaults[key])
    return param