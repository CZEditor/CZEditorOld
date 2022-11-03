from multiprocessing import dummy
from turtle import update
import numpy as np
import moviepy.editor as mpy
import moviepy.config as mpyconfig
from imagefunctions import NormalImage,XPError
from statefunctions import NormalKeyframe
from compositingfunctions import ImageComposite
from util import *
from PySide6.QtWidgets import QAbstractButton,QMainWindow,QApplication,QFrame,QScrollArea,QSplitter,QWidget,QGraphicsScene,QGraphicsView,QGraphicsItem,QGraphicsSceneMouseEvent,QComboBox,QPlainTextEdit,QLabel,QVBoxLayout,QHBoxLayout,QSizePolicy,QFormLayout
from PySide6.QtGui import QPixmap,QPainter,QPen,QBrush,QColor,QRadialGradient,QResizeEvent,QMouseEvent,QWheelEvent,QTextOption
from PySide6.QtCore import QSize,Qt,QRectF,QPoint,QLine
from PIL import Image,ImageQt
from ui import *
from typing import *
import sys
keyframes = []

class Keyframe():
    def image(self):
        return self.imageparams.function.image(self.imageparams.params)
    def state(self, statetomodify):
        for stateparam in self.stateparams:
            statetomodify = stateparam.function.state(statetomodify,self)
        return statetomodify
    def composite(self, canvas, image):
        for compositingparam in self.compositingparams:
            canvas = compositingparam.function.composite(canvas,image,compositingparam)
        return canvas
    def __init__(self, frame, param):
        self.frame = frame
        self.params = param
        self.imageparams = param.image
        self.stateparams = param.states
        self.compositingparams = param.compositing

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

keyframes = Keyframelist()
keyframes.append(Keyframe(10, Params({"image":{"function":XPError,"params":{"text":"smoke","buttons":["yeah","lets go","Cancel"]}},"states":[{"function":NormalKeyframe,"params":{}}],"compositing":[{"function":ImageComposite,"params":{"x":100,"y":200}}]})))
keyframes.append(Keyframe(70, Params({"image":{"function":XPError,"params":{"text":"gdfgjdlgrgrelhjrtklhjgreg","buttons":["OK"]}},"states":[{"function":NormalKeyframe,"params":{}}],"compositing":[{"function":ImageComposite,"params":{"x":120,"y":220}}]})))
keyframes.append(Keyframe(130, Params({"image":{"function":XPError,"params":{"title":"Error","erroricon":"xp/Exclamation.png","buttons":["Yes","No"]}},"states":[{"function":NormalKeyframe,"params":{}}],"compositing":[{"function":ImageComposite,"params":{"x":140,"y":240}}]})))


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
    def changeEvent(self, e) -> None:
        self.onchange(self.toPlainText())
        return super().changeEvent(e)
        
class QRedTextProperty(QRedFrame):
    def __init__(self,parent,param:Params,index):
        super().__init__(parent)
        self.param = param
        self.widgets = QHBoxLayout()
        self.index = index
        self.textbox = QRedTextBox(self,self.updateproperty)
        self.textbox.setPlainText(getattr(param,index))
        self.widgets.addWidget(self.textbox)
        self.setLayout(self.widgets)
        
    def updateproperty(self,value:str):
        setattr(self.param,self.index,value)
    def updatetextbox(self):
        self.textbox.onchange = dummyfunction
        self.textbox.setPlainText(getattr(self.param,self.index))
        self.textbox.onchange = self.updateproperty
class QRedDropDownFrame(QRedFrame):
    def __init__(self,parent,name):
        super().__init__(parent)
        self.whole = QVBoxLayout(self)
        self.collapseButton = QRedButton(None,name,0,0,self.collapse)
        self.mainView = QRedFrame(self)        
        self.widgets = QFormLayout(self.mainView)
        self.widgets.addRow("text",QRedTextProperty(None,keyframes.get(0).imageparams,"text"))
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
        self.setMaximumHeight(200)
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
        dropdo2 = QRedDropDownFrame(None,"yo2")
        self.widgets.addWidget(dropdo2)
        self.viewframe.setLayout(self.widgets)
        self.widgets.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setWidget(self.viewframe)
        #self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,QSizePolicy.Policy.MinimumExpanding)
        #self.widgets.setAlignment(Qt.AlignmentFlag.AlignTop)
        #self.alayout.addWidget(self.viewframe)
        self.setWidgetResizable(True)
        
    
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
        self.onscroll = dummyfunction
        self.previousmouse = QPoint(0,0)
    def mousePressEvent(self, event) -> None:
        #print(event)
        self.onpress(event)
        self.previousmouse = event.pos()
        return super().mousePressEvent(event)
    def mouseReleaseEvent(self, event) -> None:
        self.onrelease(event)
        return super().mouseReleaseEvent(event)
    def mouseMoveEvent(self, event:QMouseEvent) -> None:
        self.onmove(event,self.previousmouse)
        #print(event)
        self.previousmouse = event.pos()
        return super().mouseMoveEvent(event)
    def wheelEvent(self, event) -> None:
        self.onscroll(event)
        return super().wheelEvent(event)

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
        self.graphicsview = QGraphicsViewEvent(self)
        #self.graphicsview.setSceneRect(QRectF(0,0,200,2000))
        self.graphicsview.setScene(self.scene)
        self.graphicsview.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphicsview.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphicsview.horizontalScrollBar().disconnect(self.graphicsview)
        self.graphicsview.verticalScrollBar().disconnect(self.graphicsview)
        #kefrmae = self.scene.addRect(QRectF(0,0,18,18),QPen(QColor(0,0,0),0),coolgradient)
        #self.scene.addLine(QLine(0,0,0,self.scene.height()),QPen(QColor(0,0,0),0))
        self.graphicsview.setStyleSheet("border-image:url(editor/Square Frame.png) 2; border-width:2;")
        #self.graphicsview.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        for keyframe in keyframes:
            self.addKeyframe(keyframe)
        boundingrect = self.graphicsview.mapToScene(self.graphicsview.viewport().geometry()).boundingRect()
        self.playbackcursor = self.scene.addLine(QLine(playbackframe,boundingrect.top(),playbackframe,boundingrect.bottom()),QPen(QColor(255,0,0),0))
        self.draggedframe = None
        self.graphicsview.onpress = self.pressEvent
        self.graphicsview.onrelease = self.releaseEvent
        self.graphicsview.onmove = self.mmoveEvent
        self.graphicsview.onscroll = self.zoom
        #self.graphicsview.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        #self.graphicsview.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.graphicsview.verticalScrollBar().setMaximum(200000000)
        self.graphicsview.horizontalScrollBar().setMaximum(200000000)
        
    def updateplaybackcursor(self,frame):
        boundingrect = self.graphicsview.mapToScene(self.graphicsview.viewport().geometry()).boundingRect()
        self.playbackcursor.setLine(QLine(frame,boundingrect.top(),frame,boundingrect.bottom()))
    def mmoveEvent(self, event:QMouseEvent,prevpos:QPoint) -> None:
        if event.buttons() & Qt.MouseButton.MiddleButton:
            delta = event.pos()-prevpos
            self.graphicsview.translate(delta.x(),delta.y())
            boundingrect = self.graphicsview.mapToScene(self.graphicsview.viewport().geometry()).boundingRect()
            self.playbackcursor.setLine(QLine(playbackframe,boundingrect.top(),playbackframe,boundingrect.bottom()))
        if self.draggedframe:
            keyframes.setframe(self.draggedframe,self.graphicsview.mapToScene(event.pos().x(),0).x())
            self.keyframes[self.draggedframe].setPos(self.draggedframe.frame,0)
            self.parentclass.updateviewport()
        return super().mouseMoveEvent(event)
    def pressEvent(self, event:QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            founditem:QGraphicsItem = self.graphicsview.itemAt(event.pos().x(),event.pos().y())
            if founditem != None:
                self.draggedframe = founditem.data(0)
            else:
                updateplaybackframe(self.graphicsview.mapToScene(event.pos().x(),0).x())
                self.updateplaybackcursor(self.graphicsview.mapToScene(event.pos().x(),0).x())
                self.parentclass.updateviewport()
       
        return super().mousePressEvent(event)
    def releaseEvent(self, event:QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if self.draggedframe:
                keyframes.setframe(self.draggedframe,self.graphicsview.mapToScene(event.pos().x(),0).x())
                self.keyframes[self.draggedframe].setPos(self.draggedframe.frame,0)
                self.draggedframe = None
                self.parentclass.updateviewport()
        return super().mouseReleaseEvent(event)
    
        #return super().mouseReleaseEvent(event)
    def resizeEvent(self, event:QResizeEvent) -> None:
        #self.scene.setSceneRect(self.rect())
        r = self.graphicsview.sceneRect()
        r.setSize(event.size()/self.graphicsview.transform().m11()+QSize(1000,1000))  #hacky workaround, if this wasnt here it would snap to 0,0 every time you shrinked the view by more than 1 pixel per frame
        self.graphicsview.setSceneRect(r)
        self.graphicsview.setFixedSize(event.size())
        r = self.graphicsview.sceneRect()
        r.setSize(event.size()/self.graphicsview.transform().m11())
        self.graphicsview.setSceneRect(r)
        #print(r)
        #print(self.graphicsview.)
        super().resizeEvent(event)
        boundingrect = self.graphicsview.mapToScene(self.graphicsview.viewport().geometry()).boundingRect()
        self.playbackcursor.setLine(QLine(playbackframe,boundingrect.top(),playbackframe,boundingrect.bottom()))
    
    def addKeyframe(self,keyframe:Keyframe):
        self.keyframes[keyframe] = self.scene.addRect(QRectF(-9,-9,18,18),QPen(QColor(0,0,0),0),self.coolgradient)
        self.keyframes[keyframe].setRotation(45)
        self.keyframes[keyframe].setPos(keyframe.frame,0)
        self.keyframes[keyframe].setData(0,keyframe)
    def zoom(self,event:QWheelEvent):
        oldpos = self.graphicsview.mapToScene(event.position().toPoint())
        factor = 1.05
        self.graphicsview.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        self.graphicsview.scale((factor if event.angleDelta().y() > 0 else 1/factor),(factor if event.angleDelta().y() > 0 else 1/factor))
        r = self.graphicsview.sceneRect()
        r.setSize(self.size()/self.graphicsview.transform().m11())
        self.graphicsview.setSceneRect(r)
        newpos = self.graphicsview.mapToScene(event.position().toPoint())
        delta = newpos-oldpos
        self.graphicsview.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        
        self.graphicsview.translate(delta.x(),delta.y())
        boundingrect = self.graphicsview.mapToScene(self.graphicsview.viewport().geometry()).boundingRect()
        self.playbackcursor.setLine(QLine(playbackframe,boundingrect.top(),playbackframe,boundingrect.bottom()))
    
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