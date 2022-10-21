from generate import *
from PIL import Image
from functools import cache
@cache
def CreateRedButton(text,style):
    styles = ["editor/Button.png","editor/Button Highlighted.png","editor/Button Pressed.png"]
    Button = Image.open(styles[style]).convert("RGBA")
    col = (0,0,0,255)
    textsize = measuretext7(text,"7\\fonts\\text\\",kerningadjust=-1)
    Button = resize(Button,max(textsize[0]+16,86),max(24,textsize[1]+9),3,3,3,3,Image.NEAREST)
    Button = createtext7(Button,w(Button)//2-textsize[0]//2,4,text,"7\\fonts\\text\\",color=(255,128,128),kerningadjust=-1)
    return Button
def CreateRedTab(text,active=True):
    if active:
        TabImg = Image.open("editor/Selected Tab.png").convert("RGBA").transpose(Image.ROTATE_90)
    else:
        TabImg = Image.open("editor/Unselected Tab.png").convert("RGBA").transpose(Image.ROTATE_90)
    textsize = measuretext7(text,"7\\fonts\\text\\",kerningadjust=-1)
    Tab = resize(TabImg,textsize[0]+10,textsize[1]+9,3,3,3,3,Image.NEAREST)
    Tab = createtext7(Tab,5,4,text,"7\\fonts\\text\\",color=(255,128,128),kerningadjust=-1)
    return Tab.transpose(Image.ROTATE_270)