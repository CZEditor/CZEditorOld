from PIL import Image

openedimages = {}
newimages = {}
emptyimage = Image.new("RGBA",(1,1),(0,0,0,0))

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
    
    def __getattr__(self,param:str): #This is a failsafe
        return None
        
    def iterate(self,toiterate:dict):
        out = {}
        for k,v in toiterate.items():
            if isinstance(v,list):
                out[k] = self.iteratelist(v)
            elif hasattr(v,"copy"):
                out[k] = v.copy()
            else:
                out[k] = v
        return out

    def iteratelist(self,toiterate:list):
        out = []
        for v in toiterate:
            if isinstance(v,list):
                out.append(self.iteratelist(v))
            elif hasattr(v,"copy"):
                out.append(v.copy())
            else:
                out.append(v)
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

    def set(self,index,value):
        self.__setattr__(index,value)
        return self
class Selectable():
    def __init__(self,index=0,options=[["None",None]]):
        self.options = options
        self.index = index
        self.names = [i[0] for i in self.options]
    def __call__(self):
        return self.options[self.index][1]
    def __str__(self):
        return str(self.options[self.index][1])
    def copy(self):
        return Selectable(self.index,self.options)
    def name(self):
        return self.names[self.index]

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


class StringList():
    def __init__(self,initial):
        self.list = initial
    def __getitem__(self,param):
        return self.list[param]
    def __setitem__(self,param,value):
        self.list[param] = value
    def pop(self,index):
        self.list.pop(index)
    def append(self,param):
        self.list.append(param)
    def __len__(self):
        return len(self.list)
    def __str__(self):
        return str(self.list)

class ParamLink():
    def __init__(self,params,key):
        self.params = params
        self.key = key
    def __call__(self):
        return self.params[self.key]
    def set(self,value):
        self.params[self.key] = value