from PIL import Image, ImageDraw

rectangles = {}


def CreateFilledRectangle(size, color):
    hash = str(size)+str(color)
    if hash in rectangles:
        return rectangles[hash]
    rectangles[hash] = Image.new("RGBA", size, color)
    return rectangles[hash]
