from PIL import Image
from generate import *
from util import *

Width = 1280
Height = 720

class Window():
    def __init__(self,os="xp",text="",subtext="",icon=0,title="",buttons=["","",""],buttonstyles=[0,0,0],buttondefaults=[False,False,False],bar=True,closebutton=True,active=True,collapsed=False,img="",startpos=(0,0,0),animate=True,startrotation=(0,0,0),animationlength=0.016666666,origin=(0,0,0),animationcloselength=0.0166666666,timingfunction=win7bezierapprox,endpos=(0,0,0),endrotation=(0,0,0),endorigin=(0,0,0),closetimingfunction=win7bezierapproxclose):
        self.os = os
        self.active = active
        self.text = text
        self.subtext = subtext
        self.title = title
        self.icon = icon
        self.buttons = buttons
        self.buttonstyles = buttonstyles
        self.buttondefaults = buttondefaults
        self.bar = bar
        self.closebutton = closebutton
        self.collapsed = collapsed
        
        self.icons = {
            "xp":[
                "xp/Critical Error.png",
                "xp/Exclamation.png",
                "xp/Information.png",
                "xp/Question.png"],
            "macwindoid":["",
                "mac/Speech Bubble"],
            "ubuntu":["ubuntu/Error.png",
                      "ubuntu/Exclamation.png",
                      "ubuntu/Attention.png",
                      "ubuntu/Information.png",
                      "ubuntu/Question Mark.png"],
            "95":["95/Critical Error.png",
                  "95/Exclamation.png.png",
                  "95/Information.png",
                  "95/Question.png"],
            "macwindow":["mac/hand.png",
                         "mac/Exclamation.png",
                         "mac/Speech Bubble.png"],
            "7":["7/Critical Error.png",
                 "7/Exclamation.png",
                 "7/Information.png",
                 "7/Question Mark.png"]}
        self.cancomposite = self.os in ["7","custom"]
        self.imgstr = img
        if self.imgstr:
            self.img = openimage(self.imgstr)
        else:
            self.img = newimage(Width,Height)
        self.startpos = startpos
        self.animate = animate
        self.startrotation = startrotation
        self.animationlength = animationlength
        self.animationcloselength = animationcloselength
        self.origin = origin
        self.hashstring = self.os+","+str(self.active)+","+self.text+","+self.subtext+","+str(self.icon)+","+self.title+","+str(self.buttons)+","+str(self.buttonstyles)+","+str(self.buttondefaults)+","+str(self.bar)+","+str(self.closebutton)+","+str(self.collapsed)+":"+self.imgstr
        self.timingfunction = timingfunction
        self.endpos=endpos
        self.endrotation=endrotation
        self.endorigin=endorigin
        self.closetimingfunction=closetimingfunction
        self.isbackground = False