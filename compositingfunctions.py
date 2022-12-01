from PIL import Image
from util import ParamLink
from handles import CzeViewportDraggableHandle
imagecache = {}
def cachecomposite(func):
    global imagecache
    strparam = str(func)
    if strparam not in imagecache:
        imagecache[strparam] = func.function().image(func.params)
    return imagecache[strparam]

class ImageComposite():
    name = "Normal Media"
    params = {
        "x":0,
        "y":0
    }
    def composite(canvas,imagefunction,params):
        
        canvas.alpha_composite(cachecomposite(imagefunction),(params.params.x,params.params.y))
        return canvas
    def handle(keyframe,parentclass,params):
        return CzeViewportDraggableHandle(None,parentclass,ParamLink(params.params,"x"),ParamLink(params.params,"y"))
    def __str__(self):
        return self.name
compositingfunctionsdropdown = [["Normal Media",ImageComposite]]