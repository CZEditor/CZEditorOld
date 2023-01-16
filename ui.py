from generate import *
from PIL import Image
from functools import cache
from util import *
from PySide6.QtWidgets import QWidget,QGraphicsScene,QGraphicsView,QGraphicsItem,QGraphicsRectItem,QGraphicsLineItem,QToolButton,QPushButton,QComboBox,QFrame,QSizePolicy,QScrollArea,QPlainTextEdit,QSpinBox,QLineEdit
from PySide6.QtGui import QPen,QColor,QRadialGradient,QResizeEvent,QMouseEvent,QWheelEvent,QDrag,QDragEnterEvent,QDragLeaveEvent,QDragMoveEvent,QDropEvent,QTextOption,QKeyEvent
from PySide6.QtCore import QSize,Qt,QRectF,QPoint,QLine,QMimeData,Qt
from keyframes import *
from copy import deepcopy
playbackframe = 100

def updateplaybackframe(frame):
    global playbackframe
    playbackframe = frame

@cache
def CreateRedButton(text,style):
    styles = ["editor/Button.png","editor/Button Highlighted.png","editor/Button Pressed.png"]
    Button = Image.open(styles[style]).convert("RGBA")
    col = (0,0,0,255)
    textsize = measuretext7(text,"7/fonts/text/",kerningadjust=-1)
    Button = resize(Button,max(textsize[0]+16,86),max(24,textsize[1]+9),3,3,3,3,Image.NEAREST)
    Button = createtext7(Button,w(Button)//2-textsize[0]//2,4,text,"7/fonts/text/",color=(255,128,128),kerningadjust=-1)
    return Button

@cache
def CreateRedStretchableButton(text,style,width):
    styles = ["editor/Button.png","editor/Button Highlighted.png","editor/Button Pressed.png"]
    Button = Image.open(styles[style]).convert("RGBA")
    col = (0,0,0,255)
    textsize = measuretext7(text,"7/fonts/text/",kerningadjust=-1)
    Button = resize(Button,max(textsize[0]+16,width),max(24,textsize[1]+9),3,3,3,3,Image.NEAREST)
    Button = createtext7(Button,w(Button)//2-textsize[0]//2,4,text,"7/fonts/text/",color=(255,128,128),kerningadjust=-1)
    return Button

@cache
def CreateRedSmallButton(text,style):
    styles = ["editor/Button.png","editor/Button Highlighted.png","editor/Button Pressed.png"]
    Button = Image.open(styles[style]).convert("RGBA")
    col = (0,0,0,255)
    textsize = measuretext7(text,"7/fonts/text/",kerningadjust=-1)
    Button = resize(Button,textsize[0]+16,max(24,textsize[1]+9),3,3,3,3,Image.NEAREST)
    Button = createtext7(Button,w(Button)//2-textsize[0]//2,4,text,"7/fonts/text/",color=(255,128,128),kerningadjust=-1)
    return Button

def CreateRedTab(text,active=True):
    if active:
        TabImg = Image.open("editor/Selected Tab.png").convert("RGBA").transpose(Image.ROTATE_90)
    else:
        TabImg = Image.open("editor/Unselected Tab.png").convert("RGBA").transpose(Image.ROTATE_90)
    textsize = measuretext7(text,"7/fonts/text/",kerningadjust=-1)
    Tab = resize(TabImg,textsize[0]+10,textsize[1]+9,3,3,3,3,Image.NEAREST)
    Tab = createtext7(Tab,5,4,text,"7/fonts/text/",color=(255,128,128),kerningadjust=-1)
    return Tab.transpose(Image.ROTATE_270)




class QGraphicsViewEvent(QGraphicsView):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.setAcceptDrops(True)
        self.onpress = dummyfunction
        self.onmove = dummyfunction
        self.onrelease = dummyfunction
        self.onscroll = dummyfunction
        self.dragenter = dummyfunction
        self.dragmove = dummyfunction
        self.dragdrop = dummyfunction
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

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        self.dragenter(event)

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        self.dragmove(event)

    def dropEvent(self, event:QDropEvent) -> None:
        self.dragdrop(event)


class CzeTimeline(QWidget):
    coolgradient = QRadialGradient(50,50,90)
    coolgradient.setColorAt(1,QColor(255,255,255))
    coolgradient.setColorAt(0,QColor(255,0,0))
    selectedcoolgradient = QRadialGradient(30,30,60)
    selectedcoolgradient.setColorAt(1,QColor(255,127,127))
    selectedcoolgradient.setColorAt(0,QColor(255,0,0))

    def __init__(self,parent,parentclass):
        global keyframes
        self.keyframes = {}
        super().__init__(parent)
        self.parentclass = parentclass
        
        #self.setSizePolicy(QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Ignored)
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
        self.lastm1pos = None
        self.setAcceptDrops(True)
        self.graphicsview.setAcceptDrops(True)
        self.graphicsview.viewport().setAcceptDrops(True)
        self.graphicsview.dragenter = self.dragEnterEvent
        self.graphicsview.dragdrop = self.dropEvent
        self.graphicsview.dragmove = self.dragMoveEvent
    def sizeHint(self):
        return QSize(self.size().width(),150)
    def updateplaybackcursor(self,frame):
        boundingrect = self.graphicsview.mapToScene(self.graphicsview.viewport().geometry()).boundingRect()
        self.playbackcursor.setLine(QLine(frame,boundingrect.top(),frame,boundingrect.bottom()))
    
    def mmoveEvent(self, event:QMouseEvent,prevpos:QPoint) -> None:
        if event.buttons() & Qt.MouseButton.MiddleButton:
            delta = (event.pos()-prevpos)*(self.graphicsview.sceneRect().width()/self.size().width())
            self.graphicsview.translate(delta.x(),delta.y())
            boundingrect = self.graphicsview.mapToScene(self.graphicsview.viewport().geometry()).boundingRect()
            self.playbackcursor.setLine(QLine(playbackframe,boundingrect.top(),playbackframe,boundingrect.bottom()))
        if self.draggedframe and self.graphicsview.geometry().contains(event.pos()):
            keyframes.setframe(self.draggedframe,int(self.graphicsview.mapToScene(event.pos().x(),0).x()))
            self.keyframes[self.draggedframe].setPos(self.draggedframe.frame,0)
            self.parentclass.updateviewport(self.parentclass.playbackframe)
        return super().mouseMoveEvent(event)
    
    def pressEvent(self, event:QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            founditem:QGraphicsItem = self.graphicsview.itemAt(event.pos().x(),event.pos().y())
            if isinstance(founditem,QGraphicsLineItem):
                return super().mousePressEvent(event)
            if founditem != None:
                if event.pos() == self.lastm1pos:
                    self.parentclass.draggedpreset = founditem.data(0).params.copy()
                    drag = QDrag(self)
                    mime = QMimeData()
                    drag.setMimeData(mime)
                    drag.exec_(Qt.MoveAction)
                else:
                    self.draggedframe = founditem.data(0)
                    if self.parentclass.selectedframe:
                        self.keyframes[self.parentclass.selectedframe].setBrush(self.coolgradient)
                    founditem.setBrush(self.selectedcoolgradient)
                    self.parentclass.selectedframe = founditem.data(0)
                    self.parentclass.regeneratekeyframeoptions()
                    self.parentclass.viewport.updatehandles()
                
            else:
                self.parentclass.seek(self.graphicsview.mapToScene(event.pos().x(),0).x())
                self.updateplaybackcursor(self.graphicsview.mapToScene(event.pos().x(),0).x())
                self.parentclass.updateviewport(self.parentclass.playbackframe)
                if event.pos() == self.lastm1pos:
                    
                    if self.parentclass.selectedframe:
                        self.keyframes[self.parentclass.selectedframe].setBrush(self.coolgradient)
                        self.parentclass.selectedframe = None
                        self.parentclass.updatekeyframeoptions()
            self.lastm1pos = event.pos()
       
        return super().mousePressEvent(event)
    
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        event.accept()
    
    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        event.accept()
    
    def dropEvent(self, event: QDropEvent) -> None:
        #print(self.parentclass.draggedpreset)
        if self.parentclass.draggedpreset and not self.draggedframe:
            keyframe = Keyframe(int(self.graphicsview.mapToScene(event.pos().x(),0).x()),self.parentclass.draggedpreset)
            keyframes.add(keyframe)
            self.addKeyframe(keyframe)
            self.parentclass.draggedpreset = None
        event.accept()
        return super().dropEvent(event)
    
    def releaseEvent(self, event:QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if self.draggedframe:
                keyframes.setframe(self.draggedframe,int(self.graphicsview.mapToScene(event.pos().x(),0).x()))
                self.keyframes[self.draggedframe].setPos(self.draggedframe.frame,0)
                self.draggedframe = None
                self.parentclass.updateviewport(self.parentclass.playbackframe)
        return super().mouseReleaseEvent(event)
    
        #return super().mouseReleaseEvent(event)
    
    def resizeEvent(self, event:QResizeEvent) -> None:
        #self.scene.setSceneRect(self.rect())
        r = self.graphicsview.sceneRect()
        r.setSize(event.size()/self.graphicsview.transform().m11()+QSize(1000,1000))  #hacky workaround, if this wasnt here it would snap to 0,0 every time you shrinked the view by more than 1 pixel per frame
        self.graphicsview.setSceneRect(r)
        #self.graphicsview.setFixedSize(event.size())
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

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.text() == "k":
            self.addKeyframe(keyframes.create(self.parentclass.playbackframe))
        elif event.key() == Qt.Key.Key_Delete:
            self.scene.removeItem(self.keyframes[self.parentclass.selectedframe])
            keyframes.remove(self.parentclass.selectedframe)
            self.parentclass.selectedframe = None
            self.parentclass.regeneratekeyframeoptions()
            self.parentclass.viewport.updatehandles()
            self.parentclass.updateviewport(self.parentclass.playbackframe)
        return super().keyPressEvent(event)

class CzePresets(QWidget):
    coolgradient = QRadialGradient(50,50,90)
    coolgradient.setColorAt(1,QColor(255,255,255))
    coolgradient.setColorAt(0,QColor(255,0,0))
    selectedcoolgradient = QRadialGradient(30,30,60)
    selectedcoolgradient.setColorAt(1,QColor(255,127,127))
    selectedcoolgradient.setColorAt(0,QColor(255,0,0))
    
    def __init__(self,parent,parentclass):
        super().__init__(parent)
        self.parentclass = parentclass
        self.scene = QGraphicsScene(self)
        self.graphicsview = QGraphicsViewEvent(self)
        self.graphicsview.setScene(self.scene)
        self.keyframes = []
        self.drawnkeyframes = {}
        i = 0
        for keyframe in self.keyframes:
            self.drawnkeyframes[keyframe] = self.scene.addRect(QRectF(-9,-9,18,18),QPen(QColor(0,0,0),0),self.coolgradient)
            self.drawnkeyframes[keyframe].setRotation(45)
            self.drawnkeyframes[keyframe].setPos((i%6)*25,floor(i/6)*25)
            self.drawnkeyframes[keyframe].setData(0,keyframe)
            i+=1
        self.graphicsview.onpress = self.pressEvent
        self.setAcceptDrops(True)
        self.graphicsview.setAcceptDrops(True)
        self.graphicsview.viewport().setAcceptDrops(True)
        self.graphicsview.dragenter = self.dragEnterEvent
        self.graphicsview.dragmove = self.dragMoveEvent
        self.graphicsview.dragdrop = self.dropEvent
    
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
        #boundingrect = self.graphicsview.mapToScene(self.graphicsview.viewport().geometry()).boundingRect()
        #self.playbackcursor.setLine(QLine(playbackframe,boundingrect.top(),playbackframe,boundingrect.bottom()))
    
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        event.accept()
    
    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        event.accept()
    
    def dropEvent(self, event: QDropEvent) -> None:
        if self.parentclass.draggedpreset:
            #print(self.parentclass.draggedpreset)
            if self.parentclass.draggedpreset in self.keyframes:
                self.parentclass.draggedpreset = None
                return super().mouseReleaseEvent(event)
            keyframe = self.parentclass.draggedpreset.copy()
            i = len(self.keyframes)
            self.keyframes.append(self.parentclass.draggedpreset.copy())
            self.drawnkeyframes[keyframe] = self.scene.addRect(QRectF(-9,-9,18,18),QPen(QColor(0,0,0),0),self.coolgradient)
            self.drawnkeyframes[keyframe].setRotation(45)
            self.drawnkeyframes[keyframe].setPos((i%6)*25,floor(i/6)*25)
            self.drawnkeyframes[keyframe].setData(0,keyframe)
            self.parentclass.draggedpreset = None
        event.accept()
    
    def pressEvent(self, event:QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            founditem:QGraphicsItem = self.graphicsview.itemAt(event.pos().x(),event.pos().y())
            if founditem != None:
                self.parentclass.draggedpreset = founditem.data(0).copy()
                #print(self.parentclass.draggedpreset)
                drag = QDrag(self)
                mime = QMimeData()
                drag.setMimeData(mime)
                drag.exec_(Qt.MoveAction)
                
        return super().mouseReleaseEvent(event)
