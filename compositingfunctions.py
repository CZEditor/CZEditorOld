from PIL import Image

imagecache = {}
def cache(param,func):
    global imagecache
    strparam = str(func)
    #tempparam = param.copy()
    #strparam = func.__name__+":"+str(tempparam)
    if strparam not in imagecache:
        imagecache[strparam] = func.function.image(func.params)
        #print("NOT IN",strparam)
    return imagecache[strparam]

class ImageComposite():
    name = "Normal Media"
    def composite(canvas,imagefunction,params):
        canvas.alpha_composite(cache(params,imagefunction),(params.params.x,params.params.y))
        return canvas 
