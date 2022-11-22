from PIL import Image

imagecache = {}
def cachecomposite(func):
    global imagecache
    strparam = str(func)
    if strparam not in imagecache:
        imagecache[strparam] = func.function.image(func.params)
    return imagecache[strparam]

class ImageComposite():
    name = "Normal Media"
    def composite(canvas,imagefunction,params):
        
        canvas.alpha_composite(cachecomposite(imagefunction),(params.params.x,params.params.y))
        return canvas
    def __str__(self):
        return self.name
