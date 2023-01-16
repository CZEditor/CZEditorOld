from multiprocessing import dummy
import numpy as np
import moviepy.editor as mpy
import moviepy.config as mpyconfig
from imagefunctions import NormalImage,XPError
from statefunctions import NormalKeyframe
from compositingfunctions import ImageComposite
from util import *
from PySide6.QtWidgets import QAbstractButton,QMainWindow,QApplication,QFrame,QScrollArea,QSplitter,QWidget,QGraphicsScene,QGraphicsView,QGraphicsItem,QGraphicsSceneMouseEvent,QComboBox,QPlainTextEdit,QLabel,QVBoxLayout,QHBoxLayout,QSizePolicy,QFormLayout,QLineEdit,QGridLayout,QSpinBox,QGraphicsPixmapItem,QStyle,QPushButton,QToolButton
from PySide6.QtGui import QPixmap,QPainter,QPen,QBrush,QColor,QRadialGradient,QResizeEvent,QMouseEvent,QWheelEvent,QTextOption,QKeyEvent,QImage,QMatrix4x4
from PySide6.QtCore import QSize,Qt,QRectF,QPoint,QLine,SIGNAL,QTimerEvent
from PySide6.QtMultimedia import QMediaPlayer,QAudioOutput
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL.shaders import compileProgram,compileShader
from PIL import Image,ImageQt
from ui import *
from typing import *
import sys
from keyframes import *
from time import time,perf_counter
from ctypes import c_void_p
from base_ui import *
import sounddevice
import traceback

UIDropdownLists = [
    [NormalImage,XPError],
    [NormalKeyframe],
    [ImageComposite]
]


# TODO : Move these into the Window class

def stateprocessor(frame,keyframes):
    state = []
    for keyframe in keyframes:
        if keyframe.frame > frame:
            return state
        state = keyframe.state(state)
    return state
    

def composite(state,parentclass):
    for keyframe in state:
        keyframe.composite(keyframe.imageparams,parentclass)

def frameprocessor(frame, keyframes):
    returnkeyframes = []
    for keyframe in keyframes:
        if keyframe.frame < frame:
            returnkeyframes.append(keyframe)
        else:
            return returnkeyframes

    
    



def getframeimage(i):
    global keyframes
    i = i * 60
    processedkeyframes = frameprocessor(i, keyframes)
    state = stateprocessor(processedkeyframes)
    image:Image = composite(state)
    return np.asarray(image.convert("RGB"))

def getstate(i,parentclass):
    global keyframes
    return stateprocessor(i,keyframes)

def getviewportimage(state,parentclass):
    composite(state,parentclass)

def getsound(state,sample):
    first = True
    buffer = np.zeros((1024,2))
    for keyframe in state:
        gotten = keyframe.sound(sample)[0]
        if(len(gotten.shape) != 0):
            gotten = np.pad(gotten,((0,1024-gotten.shape[0]),(0,0)),"constant",constant_values=(0,0))
            buffer += gotten
    return buffer
    
mpyconfig.FFMPEG_BINARY = "ffmpeg"
def render(filename, length, keyframes):

    clip = mpy.VideoClip(getframeimage, duration=length / 60)
    #clip.write_videofile(filename=filename, fps=60, codec="libx264rgb", ffmpeg_params=["-strict","-2"]) perfection, doesnt embed | don't delete this
    clip.write_videofile(filename=filename, fps=60, codec="libvpx-vp9",ffmpeg_params=["-pix_fmt","yuv444p"],write_logfile=True) #perfection, embeds only on pc








rendered = None
class CzeVideoView(QOpenGLWidget):
    def __init__(self,parentclass,parent=None):
        #print(parentclass,parent)
        super().__init__(parent)
        self.state = []
        self.parentclass =parentclass
    def initializeGL(self):
        #super().initializeGL(self)
        self.shader = compileProgram(compileShader("""#version 450 core
layout (location=0) in vec3 vertexPos;
layout (location=1) in vec2 vertexColor;
uniform highp mat4 matrix;
out vec2 fragmentColor;
void main()
{
    //gl_Position = round(matrix*vec4(vertexPos, 1.0)*256)/256;
    gl_Position = matrix*vec4(vertexPos, 1.0);
    fragmentColor = vertexColor;
}""",GL_VERTEX_SHADER),
compileShader("""#version 450 core
in vec2 fragmentColor;
uniform sampler2D image;
out vec4 color;
void main()
{
    color = texture(image,fragmentColor);
    //color = vec4(fragmentColor,0.0,1.0);
}""",GL_FRAGMENT_SHADER))
        #self.fbo = glGenFramebuffers(1)
        #self.renderbuffer = glGenRenderbuffers(1)
        #glBindRenderbuffer(GL_RENDERBUFFER,self.renderbuffer)
        #glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA8, 1280,720)
        #glBindFramebuffer(GL_DRAW_FRAMEBUFFER,self.fbo)
        #glFramebufferRenderbuffer(GL_DRAW_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_RENDERBUFFER,self.renderbuffer)
    def sizeHint(self):
        return QSize(1280,720)
    #def resizeGL(self, w: int, h: int) -> None:
        #glViewport(-1280/2,-720/2,1280,720)
        #return super().resizeGL(1280, 720)
    def paintGL(self):
        global rendered
        #glBindFramebuffer(GL_DRAW_FRAMEBUFFER,self.fbo)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.1,0.2,0.2,1.0)
        glLoadIdentity()
        glUseProgram(self.shader)
        projection = QMatrix4x4()
        projection.frustum(-1280/32,1280/32,720/32,-720/32,64,4096)
        projection.translate(0,0,-1024)
        glUniformMatrix4fv(glGetUniformLocation(self.shader,"matrix"),1,GL_FALSE,np.array(projection.data(),dtype=np.float32))
        getviewportimage(self.state,self.parentclass)

        rendered = glReadPixels(0,0,1280,720,GL_RGBA,GL_UNSIGNED_BYTE,None)

class CzeViewport(QWidget):
    def __init__(self,parent,parentclass):
        super().__init__(parent)
        self.videorenderer = CzeVideoView(parentclass,self)
        self.timestamp = 100
        self.scene = QGraphicsScene(self)
        self.graphicsview = QGraphicsViewEvent(self)
        self.graphicsview.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphicsview.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphicsview.horizontalScrollBar().disconnect(self.graphicsview)
        self.graphicsview.verticalScrollBar().disconnect(self.graphicsview)
        self.graphicsview.verticalScrollBar().setMaximum(200000000)
        self.graphicsview.horizontalScrollBar().setMaximum(200000000)
        self.graphicsview.setScene(self.scene)
        self.infolabel = QLabel(self)
        self.infolabel.raise_()
        self.infolabel.setStyleSheet("background: transparent;")
        self.parentclass = parentclass
        
        self.updateviewportimage(getstate(self.parentclass.playbackframe,self.parentclass))
        self.picture = QPixmap(1280,720)
        #self.viewportimage = self.scene.addPixmap(QPixmap.fromImage(ImageQt.ImageQt(getviewportimage(self.timestamp,self.parentclass))))
        self.viewportimage = self.scene.addPixmap(self.picture)
        
        #self.thelayout = QHBoxLayout()
       # self.setLayout(self.thelayout)
        #self.setMaximumSize(1280,720)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.handles = []
        #self.startTimer(0.01,Qt.TimerType.PreciseTimer)
       # self.isplaying = False
        #self.somehandle = CzeViewportDraggableHandle(None,self,ParamLink(keyframes[0].params.compositing[0].params,"x"),ParamLink(keyframes[0].params.compositing[0].params,"y"))
        #self.scene.addItem(self.somehandle)
        self.graphicsview.onmove = self.mmoveEvent
        self.graphicsview.onscroll = self.scrollEvent
    def sizeHint(self):
        return QSize(1280,720)
    def updateviewportimage(self,state):
        global rendered
        self.videorenderer.state = state
        self.videorenderer.update()
        if(rendered):
            img = QImage(rendered,1280,720,QImage.Format_RGBA8888)
            img.mirror(False,True)
            self.picture = QPixmap.fromImage(img)
            #self.picture = self.picture.scaled(QSize(min(self.size().width(),1280),min(self.size().height(),720)),Qt.AspectRatioMode.KeepAspectRatio)
            self.viewportimage.setPixmap(self.picture)
    def createhandle(self,keyframe,function,param):  #self , keyframe of the handle , function of the param , param itself
        #print(vars(function))
        if hasattr(function,"handle"):
            handles = function.handle(keyframe,self.parentclass,param)
            for handle in handles:
                self.handles.append(handle)
                self.scene.addItem(handle)
    def updatehandles(self):
        for handle in self.handles:
            self.scene.removeItem(handle)
        self.handles = []
        if(self.parentclass.selectedframe):
            self.createhandle(self.parentclass.selectedframe,self.parentclass.selectedframe.params.image.function(),self.parentclass.selectedframe.params)
            for param in self.parentclass.selectedframe.params.compositing:
                self.createhandle(self.parentclass.selectedframe,param.function(),param)
            for param in self.parentclass.selectedframe.params.states:
                self.createhandle(self.parentclass.selectedframe,param.function(),param)


    def resizeEvent(self, event:QResizeEvent) -> None:
        self.updateviewportimage(getstate(self.parentclass.playbackframe,self.parentclass))
        self.graphicsview.setFixedSize(event.size())
        self.scene.setSceneRect(0,0,self.picture.width()-2,self.picture.height()-2)
        r = self.graphicsview.sceneRect()
        r.setSize(self.size()/self.graphicsview.transform().m11()*1.25)
        self.graphicsview.setSceneRect(r)
        #size = event.size()
        #croppedevent = QResizeEvent(QSize(min(size.width(),size.height()/self.picture.size().width()*self.picture.size().height()),min(size.height(),size.width()/self.picture.size().height()*self.picture.size().width())),event.oldSize())
        return super().resizeEvent(event)

    def mmoveEvent(self, event:QMouseEvent,prevpos:QPoint) -> None:
        
        if event.buttons() & Qt.MouseButton.MiddleButton:
            self.graphicsview.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
            delta = (event.pos()-prevpos)*(self.graphicsview.sceneRect().width()/self.size().width())
            self.graphicsview.translate(delta.x(),delta.y())
            #self.graphicsview.setTransform(self.graphicsview.transform().translate(delta.x(),delta.y()))
        return super().mouseMoveEvent(event)
    def scrollEvent(self, event:QWheelEvent):
        """self.graphicsview.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        oldpos = self.graphicsview.mapToScene(event.position().toPoint())
        
        factor = 1.05
        scale = (factor if event.angleDelta().y() > 0 else 1/factor)
        self.graphicsview.scale(scale,scale)
        #self.graphicsview.setTransform(self.graphicsview.transform().translate(int((self.viewportimage.pos().x()-oldpos.x())*(scale-1)),int((self.viewportimage.pos().y()-oldpos.y())*(scale-1))))
        r = self.graphicsview.sceneRect()
        r.setSize(self.size()/self.graphicsview.transform().m11())
        self.graphicsview.setSceneRect(r)"""
        oldpos = self.graphicsview.mapToScene(event.position().toPoint())
        factor = 1.125
        self.graphicsview.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        self.graphicsview.scale((factor if event.angleDelta().y() > 0 else 1/factor),(factor if event.angleDelta().y() > 0 else 1/factor))
        r = self.graphicsview.sceneRect()
        r.setSize(self.size()/self.graphicsview.transform().m11()*factor)
        self.graphicsview.setSceneRect(r)
        newpos = self.graphicsview.mapToScene(event.position().toPoint())
        delta = newpos-oldpos
        self.graphicsview.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        
        self.graphicsview.translate(delta.x(),delta.y())
        self.showInfo(f"Scale: {round(self.graphicsview.transform().m11(),3)}")
        #self.viewportimage.setScale(self.viewportimage.scale()*scale)
        #thepos = QPoint(self.viewportimage.pos().x()+(self.viewportimage.pos().x()-oldpos.x())*(scale-1),self.viewportimage.pos().y()+(self.viewportimage.pos().y()-oldpos.y())*(scale-1))
        #self.viewportimage.setPos(thepos)
        #self.viewportimage.setTransformOriginPoint(self.viewportimage.scenePos())

    def showInfo(self,text):
        self.infolabel.setText(text)
        #self.infolabel.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.infolabel.setFixedSize(self.infolabel.sizeHint())
    
    #def paintEvent(self, event) -> None:
    #    painter = QPainter(self)
    #    painter.setViewport()
        #self.scene.render(painter,aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
        #return super().paintEvent(event)
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.playbackframe = 100
        self.setWindowTitle("fgdf")
        self.setGeometry(100,100,1280,720)
        #button = QRedButton(self,"yeah",4,4,lambda: print("pressed"))
        self.setStyleSheet("background-color: qradialgradient(spread:pad, cx:4.5, cy:4.5, radius:7, fx:4.5, fy:4.5, stop:0 rgba(255, 0, 0, 255), stop:1 rgba(0, 0, 0, 255));  color: rgb(255,192,192);")
        hozsplitter = QSplitter(Qt.Orientation.Vertical,self)
        #rightsplitter = QSplitter(hozsplitter)
        topsplitter = QSplitter(hozsplitter)
        
        self.keyframeoptions = CzeKeyframeOptions(topsplitter,self)
        self.viewport = CzeViewport(topsplitter,self)
        self.presets = CzePresets(topsplitter,self)
        self.timeline = CzeTimeline(hozsplitter,self)
    
        self.selectedframe = None
        self.setCentralWidget(hozsplitter)
        self.show()
        
        self.draggedpreset = None
        self.startTimer(0.016,Qt.TimerType.PreciseTimer)
        self.lastframetime = perf_counter()
        self.isplaying = False
        self.starttime = perf_counter()
        self.startframe = self.playbackframe
        self.needtoupdate = True
        self.currentframestate = []
        #self.stream = self.pyaudio.open(format=self.pyaudio.get_format_from_width(1),channels=1,rate=48000,output=True)
        sounddevice.default.samplerate = 48000
        sounddevice.default.channels = 1
        sounddevice.play(np.zeros(1024))
        self.stream = sounddevice.OutputStream(channels=2,samplerate=48000,blocksize=1024,callback=self.getnextsoundchunk)
        self.stream.start()
        self.playbacksample = int(self.playbackframe/60*48000)
    def updateviewport(self):
        self.needtoupdate = True
        #self.viewport.update()
    def updatekeyframeoptions(self):
        self.keyframeoptions.update()
    def regeneratekeyframeoptions(self):
        self.keyframeoptions.regenerate()
    def keyPressEvent(self, event: QKeyEvent) -> None:
        #print(event.text())
        if event.text() == " ":
            self.isplaying = not self.isplaying
            self.starttime = perf_counter()
            self.startframe = self.playbackframe
        return super().keyPressEvent(event)
    def getnextsoundchunk(self,outdata,frames,time,status):
        if self.isplaying:
            try:
                outdata[:] = getsound(self.currentframestate,self.playbacksample)
            except Exception:
                traceback.print_exc()
                outdata[:] = np.zeros((1024,1))
            self.playbacksample += 1024
        else:
            outdata[:] = np.zeros((1024,1))
            self.playbacksample = int(self.playbackframe/60*48000)
    def seek(self,frame):
        self.playbackframe = frame
        self.playbacksample = int(frame/60*48000)
    def timerEvent(self, event: QTimerEvent) -> None:
        
        if self.isplaying:
            self.playbackframe = self.startframe+int((perf_counter()-self.starttime)*60)
            self.currentframestate = getstate(self.playbackframe,self)
            self.viewport.updateviewportimage(self.currentframestate)
            self.timeline.updateplaybackcursor(self.playbackframe)
            self.needtoupdate = False
        if self.needtoupdate:
            self.viewport.updateviewportimage(getstate(self.playbackframe,self))
            self.needtoupdate = False
        return super().timerEvent(event)
    def showInfo(self, text):
        self.viewport.showInfo(text)
app = QApplication([])
window = Window()
sys.exit(app.exec())