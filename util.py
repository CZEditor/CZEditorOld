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