from PIL import Image

def ImageComposite(canvas,image,params):
    canvas.alpha_composite(image,(params["x"],params["y"]))
    return canvas