from multiprocessing import dummy
import numpy as np
import moviepy.editor as mpy
import moviepy.config as mpyconfig
from imagefunctions import NormalImage,XPError
from statefunctions import NormalKeyframe
from compositingfunctions import ImageComposite
from util import *
from PySide6.QtWidgets import QAbstractButton,QMainWindow,QApplication,QFrame,QScrollArea,QSplitter,QWidget,QGraphicsScene,QGraphicsView,QGraphicsItem,QGraphicsSceneMouseEvent,QComboBox,QPlainTextEdit,QLabel,QVBoxLayout,QHBoxLayout,QSizePolicy,QFormLayout,QLineEdit,QGridLayout
from PySide6.QtGui import QPixmap,QPainter,QPen,QBrush,QColor,QRadialGradient,QResizeEvent,QMouseEvent,QWheelEvent,QTextOption
from PySide6.QtCore import QSize,Qt,QRectF,QPoint,QLine,SIGNAL
from PIL import Image,ImageQt
from ui import *
from typing import *
import sys
from keyframes import *




def stateprocessor(keyframes):
    state = []
    for keyframe in keyframes:
        state = keyframe.state(state)
    return state

def composite(state):
    canvas = newimage(1280, 720)
    for keyframe in state:
        canvas = keyframe.composite(canvas, keyframe.imageparams)
    return canvas

def frameprocessor(frame, keyframes):
    returnkeyframes = []
    for keyframe in keyframes:
        if keyframe.frame < frame:
            returnkeyframes.append(keyframe)
        else:
            break
    return returnkeyframes



def getframeimage(i):
    global keyframes
    i = i * 60
    processedkeyframes = frameprocessor(i, keyframes)
    state = stateprocessor(processedkeyframes)
    image:Image = composite(state)
    return np.asarray(image.convert("RGB"))

def getviewportimage(i):
    global keyframes
    processedkeyframes = frameprocessor(i, keyframes)
    state = stateprocessor(processedkeyframes)
    image:Image = composite(state)
    return image
mpyconfig.FFMPEG_BINARY = "ffmpeg"
def render(filename, length, keyframes):

    clip = mpy.VideoClip(getframeimage, duration=length / 60)
    #clip.write_videofile(filename=filename, fps=60, codec="libx264rgb", ffmpeg_params=["-strict","-2"]) perfection, doesnt embed | don't delete this
    clip.write_videofile(filename=filename, fps=60, codec="libvpx-vp9",ffmpeg_params=["-pix_fmt","yuv444p"],write_logfile=True) #perfection, embeds only on pc

#render("video.mp4", 150, keyframes)
def dummyfunction(*args,**kwargs):
    pass
class QRedButton(QAbstractButton):

    def __init__(self,parent,text,x,y,onpress = dummyfunction, imagefunction = CreateRedButton,argself = False,*args,**kwargs):
        super().__init__(parent)
        self.imagefunction = imagefunction
        self.state = 0
        self.text = text
        self.pressedfunction = onpress
        self.enterEvent = self.hoveredevent
        self.leaveEvent = self.releasedevent
        self.pressed.connect(self.pressedevent)
        self.released.connect(self.hoveredevent)
        self.setPicture()
        self.setFixedSize(self.picture.size())
        self.move(x,y)
        self.args = args
        self.kwargs = kwargs
        if argself:
            self.kwargs["callerButton"] = self
    def setPicture(self):
        qim = ImageQt.ImageQt(self.imagefunction(self.text,self.state))
        self.picture = QPixmap.fromImage(qim) 
        self.update()
    def hoveredevent(self,notimportant=None):
        self.state = 1
        self.setPicture()
    def pressedevent(self):
        self.state = 2
        self.pressedfunction(*self.args,**self.kwargs)
        self.setPicture()
    def releasedevent(self,notimportant=None): 
        self.state = 0
        self.setPicture()
    def sizeHint(self):
        return self.picture.size()
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.picture)
class QRedExpandableButton(QAbstractButton):
    def __init__(self,parent,text,onpress = dummyfunction, imagefunction = CreateRedStretchableButton,*args,**kwargs):
        super().__init__(parent)
        self.imagefunction = imagefunction
        self.state = 0
        self.text = text
        self.pressedfunction = onpress
        self.enterEvent = self.hoveredevent
        self.leaveEvent = self.releasedevent
        self.pressed.connect(self.pressedevent)
        self.released.connect(self.hoveredevent)
        self.setSizePolicy(QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Preferred)
        self.setPicture()
        self.setFixedHeight(self.picture.height())
        self.args = args
        self.kwargs = kwargs
        
    def setPicture(self):
        qim = ImageQt.ImageQt(self.imagefunction(self.text,self.state,self.width()))
        self.picture = QPixmap.fromImage(qim) 
        self.update()
    def hoveredevent(self,notimportant=None):
        self.state = 1
        self.setPicture()
    def pressedevent(self):
        self.state = 2
        self.pressedfunction(*self.args,**self.kwargs)
        self.setPicture()
    def releasedevent(self,notimportant=None): 
        self.state = 0
        self.setPicture()
    #def sizeHint(self):
    #    return self.sizeHint()
    def resizeEvent(self, event) -> None:
        self.setPicture()
        self.update()
        return super().resizeEvent(event)
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.picture)
class QRedFrame(QFrame):
    def __init__(self,parent):
        super().__init__(parent)
        self.setStyleSheet("border-image:url(editor/Square Frame.png) 2; border-width:2;")

class QRedScrollArea(QScrollArea):
    def __init__(self,parent):
        super().__init__(parent)
        self.setStyleSheet("border-image:url(editor/Square Frame.png) 2; border-width:2;")

class QRedTextBox(QPlainTextEdit):
    def __init__(self,parent,onchange=dummyfunction):
        super().__init__(parent)
        self.onchange = onchange
        self.setStyleSheet("border-image:url(editor/Text Box.png) 2; border-width:2;")
        self.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        #self.setMaximumHeight(150)
        self.textChanged.connect(self.change)
    def change(self) -> None:
        self.onchange(self.toPlainText())

class QRedTextEntry(QLineEdit):
    def __init__(self,parent,onchange=dummyfunction):
        super().__init__(parent)
        self.onchange = onchange
        self.setStyleSheet("border-image:url(editor/Text Box.png) 2; border-width:2;")
        #self.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        #self.setMaximumHeight(150)
        self.textChanged.connect(self.change)
    def change(self) -> None:
        self.onchange(self.text())   
class QRedTextProperty(QRedFrame):
    def __init__(self,parent,param:Params,index):
        super().__init__(parent)
        self.param = param
        self.widgets = QHBoxLayout()
        self.index = index
        self.textbox = QRedTextBox(self,self.updateproperty)
        self.textbox.setPlainText(param[index])
        self.widgets.addWidget(self.textbox)
        self.setLayout(self.widgets)
        self.setStyleSheet("border-width:0px;")
    def updateproperty(self,value:str):
        #print("setting:",value)
        self.param[self.index] = value
    def updatetextbox(self):
        self.textbox.onchange = dummyfunction
        self.textbox.setPlainText(self.param[self.index])
        self.textbox.onchange = self.updateproperty
class QRedTextEntryListProperty(QRedFrame):
    def __init__(self,parent,param:Params,index):
        super().__init__(parent)
        self.param = param
        self.widgets = QHBoxLayout()
        self.index = index
        self.textbox = QRedTextEntry(self,self.updateproperty)
        self.textbox.setText(param[index])
        self.widgets.addWidget(self.textbox)
        self.setLayout(self.widgets)
        self.setStyleSheet("border-width:0px;")
    def updateproperty(self,value:str):
        #print("setting:",value)
        self.param[self.index] = value
    def updatetextbox(self):
        self.textbox.onchange = dummyfunction
        self.textbox.setText(self.param[self.index])
        self.textbox.onchange = self.updateproperty
class QRedTextListProperty(QRedFrame):
    def __init__(self,parent):
        super().__init__(parent)
        
        self.whole = QVBoxLayout(self)
        self.collapseButton = QRedExpandableButton(None,"expand",self.collapse)
        self.mainView = QRedFrame(self)
        self.withbuttons = QGridLayout()
        self.widgets = QFormLayout()
        self.thelist = keyframes[0].imageparams.params.buttons
        self.entries = []
        self.widgetbuttons = QGridLayout()
        for i in range(len(self.thelist)):
            self.entries.append(QRedTextEntryListProperty(None,self.thelist,i))
            arow = QHBoxLayout()
            arow.addWidget(self.entries[i])
            arow.addWidget(QRedButton(None,"/\\",0,0,self.moveup,CreateRedSmallButton,False,arow))
            arow.addWidget(QRedButton(None,"\\/",0,0,self.movedown,CreateRedSmallButton,False,arow))
            arow.addWidget(QRedButton(None,"-",0,0,self.remove,CreateRedSmallButton,False,arow))
            self.widgets.addRow("button",arow)
        self.withbuttons.addLayout(self.widgets,0,0)
        self.withbuttons.addLayout(self.widgetbuttons,0,1)
        self.withbuttons.addWidget(QRedExpandableButton(None,"+",self.add),1,0)
        self.mainView.setLayout(self.withbuttons)
        self.mainView.sizePolicy().setVerticalPolicy(QSizePolicy.Policy.Minimum)
        self.mainView.sizePolicy().setHorizontalPolicy(QSizePolicy.Policy.MinimumExpanding)
        self.whole.addWidget(self.collapseButton)
        self.whole.addWidget(self.mainView)
        #self.whole.addWidget(QRedExpandableButton(None,"+",self.add))
        self.setLayout(self.whole)
        self.collapsed = False
        self.whole.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.whole.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        #print(self.mainView.maximumHeight())
        #self.setMaximumHeight(200)
        self.mainView.setStyleSheet("border-width:0px; background:none;")
    def collapse(self):
        if self.collapsed:
            self.mainView.setMaximumHeight(9999)
            self.collapsed = False
        else:
            self.mainView.setMaximumHeight(0)
            self.collapsed = True
    def moveup(self,arow):
        index = self.widgets.getLayoutPosition(arow)[0]
        if index == 0:
            return
        self.thelist[index],self.thelist[index-1] = self.thelist[index-1],self.thelist[index]
        self.entries[index].updatetextbox()
        self.entries[index-1].updatetextbox()
    def movedown(self,arow):
        index = self.widgets.getLayoutPosition(arow)[0]
        if index == len(self.thelist)-1:
            return
        self.thelist[index],self.thelist[index+1] = self.thelist[index+1],self.thelist[index]
        self.entries[index].updatetextbox()
        self.entries[index+1].updatetextbox()
    def remove(self,arow):
        index = self.widgets.getLayoutPosition(arow)[0] #no idea either why it has to be [0]. it returns a tuple that looks like this (4, <ItemRole.FieldRole: 1>)
        self.thelist.pop(index)
        self.widgets.removeRow(index)
        self.entries.pop(index)
    def add(self):
        
        self.thelist.append("")
        i = len(self.thelist)-1
        self.entries.append(QRedTextEntryListProperty(None,self.thelist,i))
        arow = QHBoxLayout()
        arow.addWidget(self.entries[i])
        arow.addWidget(QRedButton(None,"/\\",0,0,self.moveup,CreateRedSmallButton,False,arow))
        arow.addWidget(QRedButton(None,"\\/",0,0,self.movedown,CreateRedSmallButton,False,arow))
        arow.addWidget(QRedButton(None,"-",0,0,self.remove,CreateRedSmallButton,False,arow))
        self.widgets.addRow("button",arow)
        print(self.thelist)
class QRedDropDownFrame(QRedFrame):
    def __init__(self,parent,name):
        super().__init__(parent)
        
        self.whole = QVBoxLayout(self)
        self.collapseButton = QRedExpandableButton(None,name,self.collapse)
        self.mainView = QRedFrame(self)
        self.widgets = QFormLayout(self.mainView)
        self.widgets.addRow("text",QRedTextProperty(None,keyframes[0].imageparams.params,"text"))
        self.widgets.addRow("buttons",QRedTextListProperty(None))
        self.mainView.setLayout(self.widgets)
        self.mainView.sizePolicy().setVerticalPolicy(QSizePolicy.Policy.Minimum)
        self.mainView.sizePolicy().setHorizontalPolicy(QSizePolicy.Policy.MinimumExpanding)
        self.whole.addWidget(self.collapseButton)
        self.whole.addWidget(self.mainView)
        self.setLayout(self.whole)
        self.collapsed = False
        self.whole.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.whole.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        #print(self.mainView.maximumHeight())
        #self.setMaximumHeight(200)
        self.mainView.setStyleSheet("border-width:0px; background:none;")
    def collapse(self):
        if self.collapsed:
            self.mainView.setMaximumHeight(9999)
            self.collapsed = False
        else:
            self.mainView.setMaximumHeight(0)
            self.collapsed = True



class QRedOptionCategory(QRedFrame):
    def __init__(self,parent,param:Params):
        super().__init__(parent)
        self.param = param
        

class CzeKeyframeOptions(QRedScrollArea):
    def __init__(self,parent):
        super().__init__(parent)
        self.viewframe = QRedFrame(None)
        #self.alayout = QVBoxLayout()
        self.widgets = QVBoxLayout()
        dropdo = QRedDropDownFrame(None,"yo")
        self.widgets.addWidget(dropdo)
        #dropdo2 = QRedDropDownListFrame(None)
        #self.widgets.addWidget(dropdo2)
        self.viewframe.setLayout(self.widgets)
        self.widgets.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setWidget(self.viewframe)
        self.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Preferred)
        #self.widgets.setAlignment(Qt.AlignmentFlag.AlignTop)
        #self.alayout.addWidget(self.viewframe)
        self.setWidgetResizable(True)
    
class CzeViewport(QWidget):
    def __init__(self,parent):
        super().__init__(parent)
        self.timestamp = 100
        self.updateviewportimage(self.timestamp)
        #self.thelayout = QHBoxLayout()
       # self.setLayout(self.thelayout)
        #self.setMaximumSize(1280,720)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Ignored)
    def updateviewportimage(self,i):
        image:Image.Image = getviewportimage(i)
        #image = image.resize(self.size().toTuple(),Image.Resampling.NEAREST)
        self.picture = QPixmap.fromImage(ImageQt.ImageQt(image))
        self.timestamp = i
    def paintEvent(self, e):
        painter = QPainter(self)
       # print(self.size(),QSize(self.size().width(),self.size().height()))
        pic = self.picture.scaled(QSize(min(self.size().width(),1280),min(self.size().height(),720)),Qt.AspectRatioMode.KeepAspectRatio)
        painter.drawPixmap((self.width()-pic.width())/2,(self.height()-pic.height())/2,pic)
    def resizeEvent(self, event:QResizeEvent) -> None:
        self.updateviewportimage(self.timestamp)
        #size = event.size()
        #croppedevent = QResizeEvent(QSize(min(size.width(),size.height()/self.picture.size().width()*self.picture.size().height()),min(size.height(),size.width()/self.picture.size().height()*self.picture.size().width())),event.oldSize())
        return super().resizeEvent(event)






    
    #def paintEvent(self, event) -> None:
    #    painter = QPainter(self)
    #    painter.setViewport()
        #self.scene.render(painter,aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
        #return super().paintEvent(event)
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("fgdf")
        self.setGeometry(100,100,1280,720)
        #button = QRedButton(self,"yeah",4,4,lambda: print("pressed"))
        self.setStyleSheet("background-color: qradialgradient(spread:pad, cx:4.5, cy:4.5, radius:7, fx:4.5, fy:4.5, stop:0 rgba(255, 0, 0, 255), stop:1 rgba(0, 0, 0, 255));  color: rgb(255,192,192);")
        hozsplitter = QSplitter(Qt.Orientation.Vertical,self)
        topsplitter = QSplitter(hozsplitter)
        self.keyframeoptions = CzeKeyframeOptions(topsplitter)
        self.viewport = CzeViewport(topsplitter)
        self.timeline = CzeTimeline(hozsplitter,self)
        self.setCentralWidget(hozsplitter)
        self.show()
    def updateviewport(self,theframe):
        self.viewport.updateviewportimage(theframe)
        self.viewport.update()
app = QApplication([])
window = Window()
sys.exit(app.exec())