from PIL import Image

imagecache = {}
def cache(param,func):
    global imagecache
    tempparam = param.copy()
    del tempparam.x
    del tempparam.y
    strparam = func.__name__+":"+str(tempparam)
    if strparam not in imagecache:
        imagecache[strparam] = func(param)
    return imagecache[strparam]

def ImageComposite(canvas,imagefunction,params):
    canvas.alpha_composite(cache(params,imagefunction),(params.x,params.y))
    return canvas