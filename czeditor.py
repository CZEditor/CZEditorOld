from multiprocessing import dummy
from turtle import update
import numpy as np
import moviepy.editor as mpy
import moviepy.config as mpyconfig
from imagefunctions import NormalImage,XPError
from statefunctions import NormalKeyframe
from compositingfunctions import ImageComposite
from util import *
from PySide6.QtWidgets import QAbstractButton,QMainWindow,QApplication,QFrame,QScrollArea,QSplitter,QWidget,QGraphicsScene,QGraphicsView,QGraphicsItem,QGraphicsSceneMouseEvent
from PySide6.QtGui import QPixmap,QPainter,QPen,QBrush,QColor,QRadialGradient,QResizeEvent,QMouseEvent
from PySide6.QtCore import QSize,Qt,QRectF,QPoint,QLine
from PIL import Image,ImageQt
from ui import *
from typing import *
import sys
keyframes = []
class Keyframe():
    def image(self):
        return self.imagefunction(self.param)
    def state(self, statetomodify):
        return self.statefunction(statetomodify, self)
    def composite(self, canvas, image):
        return self.compositingfunction(canvas, image, self.param)
    def __init__(self, frame, param, imagefunction, statefunction, compositingfunction):
        self.frame = frame
        self.param = param
        self.imagefunction = imagefunction
        self.statefunction = statefunction
        self.compositingfunction = compositingfunction

class Keyframelist():
    def __init__(self):
        self.keyframes = []
        self.needssorting = False
    def add(self,keyframe:Keyframe) -> None:
        self.keyframes.append(keyframe)
        self.needssorting = True
    def append(self,keyframe:Keyframe) -> None:
        self.keyframes.append(keyframe)
        self.needssorting = True
    @overload
    def change(self,keyframe:Keyframe,change:Keyframe) -> None:
        ...
    @overload
    def change(self,i:int,change:Keyframe) -> None:
        ...
    def change(self,o,change:Keyframe) -> None:
        if isinstance(o,Keyframe):
            i = self.keyframes.index(o)
        else:
            i = o
        prevframe = self.keyframes[i].frame
        self.keyframes[i] = change
        self.needssorting = True
    @overload
    def remove(self,keyframe:Keyframe) -> None:
        ...
    @overload
    def remove(self,i:int) -> None:
        ...
    def remove(self,o) -> None:
        if isinstance(o,Keyframe):
            i = self.keyframes.index(o)
        else:
            i = o
        self.keyframes.pop(i)
    def pop(self,i:int) -> None:
        self.keyframes.pop(i)
    def len(self) -> int:
        return len(self.keyframes)
    def get(self,i) -> Keyframe:
        if self.needssorting:
            self.keyframes = sorted(self.keyframes,key=lambda k: k.frame)
            self.needssorting = False
        return keyframes[i]
    def __str__(self) -> str:
        if self.needssorting:
            self.keyframes = sorted(self.keyframes,key=lambda k: k.frame)
            self.needssorting = False
        return str(self.keyframes)
    def __getitem__(self,i:int) -> Keyframe:
        if self.needssorting:
            self.keyframes = sorted(self.keyframes,key=lambda k: k.frame)
            self.needssorting = False
        return self.keyframes[i]
    def __setitem__(self,i:int,change:Keyframe) -> None:
        prevframe = self.keyframes[i].frame
        self.keyframes[i] = change
        self.needssorting = True
    @overload
    def setframe(self,keyframe:Keyframe,frame:int):
        ...
    @overload
    def setframe(self,i:int,frame:int):
        ...
    def setframe(self,o,frame:int):
        if isinstance(o,Keyframe):
            i = self.keyframes.index(o)
        else:
            i = o
        prevframe = self.keyframes[i].frame
        self.keyframes[i].frame = frame
        self.needssorting = True
    def isinrange(self,i) -> bool:
        return len(self.keyframes) > i and i > 0
    def getsafe(self,i):
        if len(self.keyframes) > i and i > 0:
            return self.keyframes[i]
        else:
            return None
    def isin(self,keyframe:Keyframe) -> bool:
        return keyframe in self.keyframes


def stateprocessor(keyframes):
    state = []
    for keyframe in keyframes:
        state = keyframe.state(state)
    return state

def composite(state):
    canvas = newimage(1280, 720)
    for keyframe in state:
        canvas = keyframe.composite(canvas, keyframe.imagefunction)
    return canvas

def frameprocessor(frame, keyframes):
    returnkeyframes = []
    for keyframe in keyframes:
        if keyframe.frame < frame:
            returnkeyframes.append(keyframe)
        else:
            break
    return returnkeyframes

keyframes = Keyframelist()
keyframes.append(Keyframe(10, Params({"text":"smoke","buttons":["yeah","lets go","Cancel"],"x":100,"y":200}), XPError, NormalKeyframe, ImageComposite))
keyframes.append(Keyframe(70, Params({"text":"gdfgjdlgrgrelhjrtklhjgreg","buttons":["OK"],"x":120,"y":220}), XPError, NormalKeyframe, ImageComposite))
keyframes.append(Keyframe(130, Params({"title":"Error","erroricon":"xp/Exclamation.png","buttons":["Yes","No"],"x":140,"y":240}), XPError, NormalKeyframe, ImageComposite))


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

    def __init__(self,parent,text,x,y,onpress = dummyfunction, imagefunction = CreateRedButton):
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

    def setPicture(self):
        qim = ImageQt.ImageQt(self.imagefunction(self.text,self.state))
        self.picture = QPixmap.fromImage(qim) 
        self.update()
    def hoveredevent(self,notimportant=None):
        self.state = 1
        self.setPicture()
    def pressedevent(self):
        self.state = 2
        self.pressedfunction()
        self.setPicture()
    def releasedevent(self,notimportant=None): 
        self.state = 0
        self.setPicture()
    def sizeHint(self):
        return self.picture.size()
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.picture)

class QRedFrame(QFrame):
    def __init__(self,parent):
        super().__init__(parent)
        #self.setFixedSize(w,h)
        #self.move(x,y)
        self.setStyleSheet("border-image:url(editor/Square Frame.png) 2; border-width:2;")
class QRedScrollArea(QScrollArea):
    def __init__(self,parent):
        super().__init__(parent)
        #self.setFixedSize(w,h)
        #self.move(x,y)
        self.setStyleSheet("border-image:url(editor/Square Frame.png) 2; border-width:2;")
class CzeKeyframeOptions(QRedScrollArea):
    def __init__(self,parent):
        super().__init__(parent)
class CzeViewport(QWidget):
    def __init__(self,parent):
        super().__init__(parent)
        self.timestamp = 100
        self.updateviewportimage(self.timestamp)
    def updateviewportimage(self,i):
        image:Image.Image = getviewportimage(i)
        #image = image.resize(self.size().toTuple(),Image.Resampling.NEAREST)
        self.picture = QPixmap.fromImage(ImageQt.ImageQt(image))
        self.timestamp = i
    def paintEvent(self, e):
        painter = QPainter(self)
        pic = self.picture.scaled(self.size(),Qt.AspectRatioMode.KeepAspectRatio)
        painter.drawPixmap((self.width()-pic.width())/2,(self.height()-pic.height())/2,pic)
    def resizeEvent(self, event:QResizeEvent) -> None:
        self.updateviewportimage(self.timestamp)
        #size = event.size()
        #croppedevent = QResizeEvent(QSize(min(size.width(),size.height()/self.picture.size().width()*self.picture.size().height()),min(size.height(),size.width()/self.picture.size().height()*self.picture.size().width())),event.oldSize())
        
        return super().resizeEvent(event)



playbackframe = 100


def updateplaybackframe(frame):
    global playbackframe
    playbackframe = frame

class QGraphicsViewEvent(QGraphicsView):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.onpress = dummyfunction
        self.onmove = dummyfunction
        self.onrelease = dummyfunction
    def mousePressEvent(self, event) -> None:
        self.onpress(event)
        return super().mousePressEvent(event)
    def mouseReleaseEvent(self, event) -> None:
        self.onrelease(event)
        return super().mouseReleaseEvent(event)
    def mouseMoveEvent(self, event) -> None:
        self.onmove(event)
        return super().mouseMoveEvent(event)

class CzeTimeline(QWidget):
    coolgradient = QRadialGradient(50,50,90)
    coolgradient.setColorAt(1,QColor(255,255,255))
    coolgradient.setColorAt(0,QColor(255,0,0))
    
    def __init__(self,parent,parentclass):
        global keyframes
        self.keyframes = {}
        super().__init__(parent)
        self.parentclass:Window = parentclass
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(self.rect())
        self.graphicsview = QGraphicsViewEvent(self)
        self.graphicsview.setScene(self.scene)
        self.graphicsview.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        #kefrmae = self.scene.addRect(QRectF(0,0,18,18),QPen(QColor(0,0,0),0),coolgradient)
        #self.scene.addLine(QLine(0,0,0,self.scene.height()),QPen(QColor(0,0,0),0))
        self.graphicsview.setStyleSheet("border-image:url(editor/Square Frame.png) 2; border-width:2;")
        #self.graphicsview.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        for keyframe in keyframes:
            self.addKeyframe(keyframe)
        self.playbackcursor = self.scene.addLine(QLine(playbackframe,self.graphicsview.sceneRect().top(),playbackframe,self.graphicsview.sceneRect().bottom()),QPen(QColor(255,0,0),0))
        self.draggedframe = None
        self.graphicsview.onpress = self.pressEvent
        self.graphicsview.onrelease = self.releaseEvent
        self.graphicsview.onmove = self.mmoveEvent
    def updateplaybackcursor(self,frame):
        self.playbackcursor.setLine(QLine(frame,self.graphicsview.sceneRect().top(),frame,self.graphicsview.sceneRect().bottom()))
    def mmoveEvent(self, event:QMouseEvent) -> None:
        if self.draggedframe:
            keyframes.setframe(self.draggedframe,event.pos().x())
            self.keyframes[self.draggedframe].setPos(self.draggedframe.frame,0)
            self.parentclass.updateviewport()
        return super().mouseMoveEvent(event)
    def pressEvent(self, event:QMouseEvent) -> None:
        founditem:QGraphicsItem = self.scene.itemAt(event.pos().x()+self.graphicsview.sceneRect().left(),event.pos().y()+self.graphicsview.sceneRect().top(),self.graphicsview.transform())
        if founditem != None:
            self.draggedframe = founditem.data(0)
        else:
            updateplaybackframe(event.pos().x())
            self.updateplaybackcursor(event.pos().x())
            self.parentclass.updateviewport()
        return super().mousePressEvent(event)
    def releaseEvent(self, event:QMouseEvent) -> None:
        if self.draggedframe:
            keyframes.setframe(self.draggedframe,event.pos().x())
            self.keyframes[self.draggedframe].setPos(self.draggedframe.frame,0)
            self.draggedframe = None
            self.parentclass.updateviewport()
        return super().mouseReleaseEvent(event)
    
        #return super().mouseReleaseEvent(event)
    def resizeEvent(self, event) -> None:
        #self.scene.setSceneRect(self.rect())
        self.graphicsview.setFixedSize(self.size())
        self.graphicsview.setSceneRect(QRectF(QPoint(0,-self.height()/2),self.size()-QSize(5,5)))
        super().resizeEvent(event)
        self.playbackcursor.setLine(QLine(playbackframe,self.graphicsview.sceneRect().top(),playbackframe,self.graphicsview.sceneRect().bottom()))
    
    def addKeyframe(self,keyframe:Keyframe):
        self.keyframes[keyframe] = self.scene.addRect(QRectF(-9,-9,18,18),QPen(QColor(0,0,0),0),self.coolgradient)
        self.keyframes[keyframe].setRotation(45)
        self.keyframes[keyframe].setPos(keyframe.frame,0)
        self.keyframes[keyframe].setData(0,keyframe)
    #def paintEvent(self, event) -> None:
    #    painter = QPainter(self)
    #    painter.setViewport()
        #self.scene.render(painter,aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
        #return super().paintEvent(event)
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("fgdf")
        self.setGeometry(100,100,400,400)
        button = QRedButton(self,"yeah",4,4,lambda: print("pressed"))
        self.setStyleSheet("background-color: qradialgradient(spread:pad, cx:4.5, cy:4.5, radius:7, fx:4.5, fy:4.5, stop:0 rgba(255, 0, 0, 255), stop:1 rgba(0, 0, 0, 255))")
        hozsplitter = QSplitter(Qt.Orientation.Vertical,self)
        topsplitter = QSplitter(hozsplitter)
        self.keyframeoptions = CzeKeyframeOptions(topsplitter)
        self.viewport = CzeViewport(topsplitter)
        self.timeline = CzeTimeline(hozsplitter,self)
        self.setCentralWidget(hozsplitter)
        self.show()
    def updateviewport(self):
        self.viewport.updateviewportimage(playbackframe)
        self.viewport.update()
app = QApplication([])
window = Window()
sys.exit(app.exec())