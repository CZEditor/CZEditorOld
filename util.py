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
            if isinstance(params[k],dict):
                setattr(self,k,Params(params[k]))
            elif isinstance(params[k],list):
                setattr(self,k,self.iterateoverlist(params[k]))
            else:
                setattr(self,k,params[k])
        #print(vars(self))
        for k in kwargs:
            if isinstance(kwargs[k],dict):
                setattr(self,k,Params(kwargs[k]))
            else:
                setattr(self,k,kwargs[k])
    def iterateoverlist(self,l:list):
        returnal = []
        for i in l:
            if isinstance(i,dict):
                returnal.append(Params(i))
            elif isinstance(i,list):
                returnal.append(self.iterateoverlist(i))
            else:
                returnal.append(i)
        return returnal
    def __getattr__(self,param:str):
        return None
    def iterate(self,toiterate:dict):
        out = {}
        for k,v in toiterate.items():
            if isinstance(v,Params):
                #print(v)
                out[k] = v.copy()
            else:
                out[k] = v
        return out
    def copy(self):
        var = self.iterate(vars(self))
        return Params(var)
    def __str__(self):
        returnal = {}
        for k,v in vars(self).items():
            returnal[k] = str(v)
        return str(returnal)
    def __getitem__(self,param):
        return self.__getattribute__(param)
    def __setitem__(self,index,param):
        return self.__setattr__(index,param)

class Selectable():
    def __init__(self,options=[None],index=0):
        self.options = options
        self.index = index
    def __call__(self):
        return self.options[self.index]
        
    

def fillindefaults(param,defaults):
    for key in defaults.keys():
        if getattr(param,key) == None:
            setattr(param,key,defaults[key])
    return param
class emptylist():
    def __init__(self,default):
        self.default = default
    def __getitem__(self,param):
        return self.default
    def __setitem__(self,index,param):
        return
def dummyfunction(*args,**kwargs):
    pass
