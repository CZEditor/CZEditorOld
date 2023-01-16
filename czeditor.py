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
baseparams = Params({
    "image":{
        "function":Selectable(0,imagefunctionsdropdown),
        "params":Selectable(0,imagefunctionsdropdown)().params.copy()
    },
    "states":{
        "function":Selectable(0,statefunctionsdropdown),
        "params":Selectable(0,statefunctionsdropdown)().params.copy()
    },
    "compositing":{
        "function":Selectable(0,compositingfunctionsdropdown),
        "params":Selectable(0,compositingfunctionsdropdown)().params.copy()
    }
})

# TODO : Move these into the Window class

def stateprocessor(keyframes):
    state = []
    for keyframe in keyframes:
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
            break
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
    processedkeyframes = frameprocessor(i, keyframes)
    return stateprocessor(processedkeyframes)

def getviewportimage(state,parentclass):
    composite(state,parentclass)
    #return image
def getsound(state,sample):
    first = True
    buffer = np.zeros((1024,2))
    for keyframe in state:
        #if first:
        #    buffer = keyframe.sound(sample)[0]
        #    first = False
        #    continue
        gotten = keyframe.sound(sample)[0]
        gotten = np.pad(gotten,((0,1024-gotten.shape[0]),(0,0)),"constant",constant_values=(0,0))
        buffer += gotten
    return buffer
    
mpyconfig.FFMPEG_BINARY = "ffmpeg"
def render(filename, length, keyframes):

    clip = mpy.VideoClip(getframeimage, duration=length / 60)
    #clip.write_videofile(filename=filename, fps=60, codec="libx264rgb", ffmpeg_params=["-strict","-2"]) perfection, doesnt embed | don't delete this
    clip.write_videofile(filename=filename, fps=60, codec="libvpx-vp9",ffmpeg_params=["-pix_fmt","yuv444p"],write_logfile=True) #perfection, embeds only on pc

#render("video.mp4", 150, keyframes)
def dummyfunction(*args,**kwargs):
    pass




class QRedTextProperty(QRedFrame):
    def __init__(self,parent,param:Params,index,parentclass):
        super().__init__(parent)
        self.parentclass = parentclass
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
        self.parentclass.updateviewport(self.parentclass.playbackframe)
    def updateself(self):
        self.textbox.onchange = dummyfunction
        self.textbox.setPlainText(self.param[self.index])
        self.textbox.onchange = self.updateproperty
class QRedNumberProperty(QRedFrame):
    def __init__(self,parent,param:Params,index,parentclass):
        super().__init__(parent)
        self.parentclass = parentclass
        self.param = param
        self.widgets = QHBoxLayout()
        self.index = index
        self.textbox = QRedSpinBox(self,self.updateproperty)
        self.textbox.setValue(param[index])
        self.widgets.addWidget(self.textbox)
        self.setLayout(self.widgets)
        self.setStyleSheet("border-width:0px;")
    def updateproperty(self,value:int):
        #print("setting:",value)
        self.param[self.index] = value
        self.parentclass.updateviewport(self.parentclass.playbackframe)
    def updateself(self):
        self.textbox.onchange = dummyfunction
        self.textbox.setValue(self.param[self.index])
        self.textbox.onchange = self.updateproperty
class QRedSelectableProperty(QRedFrame):
    def __init__(self,parent,param:Selectable,parentclass,override=None):
        super().__init__(parent)
        self.parentclass = parentclass
        if override==None:
            override = self.updateproperty
        self.param = param
        self.widgets = QHBoxLayout()
        self.combobox = QRedComboBox(self,self.param.names)
        self.combobox.setCurrentIndex(self.param.index)
        self.combobox.onchange = override
        self.widgets.addWidget(self.combobox)
        
        self.setLayout(self.widgets)
        self.setStyleSheet("border-width:0px;")
    def updateproperty(self,name,index):
        #print("setting:",value)
        self.param.index = index
        self.parentclass.updateviewport(self.parentclass.playbackframe)
    def updateself(self):
        self.combobox.onchange = dummyfunction
        self.combobox.setCurrentIndex(self.param.index)
        self.combobox.onchange = self.updateproperty
class QRedTextEntryListProperty(QRedFrame):
    def __init__(self,parent,param:Params,index,parentclass):
        super().__init__(parent)
        self.param = param
        self.widgets = QHBoxLayout()
        self.index = index
        self.textbox = QRedTextEntry(self,self.updateproperty)
        self.textbox.setText(param[index])
        self.widgets.addWidget(self.textbox)
        self.setLayout(self.widgets)
        self.setStyleSheet("border-width:0px;")
        self.parentclass = self.parentclass
    def updateproperty(self,value:str):
        #print("setting:",value)
        self.param[self.index] = value
        self.parentclass.updateviewport(self.parentclass.playbackframe)
    def updateself(self):
        self.textbox.onchange = dummyfunction
        self.textbox.setText(self.param[self.index])
        self.textbox.onchange = self.updateproperty
        self.parentclass.updateviewport(self.parentclass.playbackframe)
class QRedTextListProperty(QRedFrame):
    def __init__(self,parent,thelist,parentclass):
        super().__init__(parent)
        self.parentclass = parentclass
        self.whole = QVBoxLayout(self)
        self.collapseButton = QRedExpandableButton(None,"expand",self.collapse)
        self.collapseButton.sizePolicy().setHorizontalPolicy(QSizePolicy.Policy.MinimumExpanding)
        self.collapseButton.setMinimumWidth(60)
        self.mainView = QRedFrame(self)
        self.withbuttons = QGridLayout()
        self.widgets = QFormLayout()
        self.thelist = thelist
        self.entries = []
        self.widgetbuttons = QGridLayout()
        for i in range(len(self.thelist)):
            self.entries.append(QRedTextEntryListProperty(None,self.thelist,i))
            arow = QHBoxLayout()
            arow.addWidget(self.entries[i])
            arow.addWidget(QRedButton(None,"/\\",0,0,self.moveup,False,arow))
            arow.addWidget(QRedButton(None,"\\/",0,0,self.movedown,False,arow))
            arow.addWidget(QRedButton(None,"-",0,0,self.remove,False,arow))
            self.widgets.addRow("",arow)
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
        window.updateviewport(window.playbackframe)
    def movedown(self,arow):
        index = self.widgets.getLayoutPosition(arow)[0]
        if index == len(self.thelist)-1:
            return
        self.thelist[index],self.thelist[index+1] = self.thelist[index+1],self.thelist[index]
        self.entries[index].updatetextbox()
        self.entries[index+1].updatetextbox()
        window.updateviewport(window.playbackframe)
    def remove(self,arow):
        index = self.widgets.getLayoutPosition(arow)[0] #no idea why it has to be [0]. it returns a tuple that looks like this (4, <ItemRole.FieldRole: 1>)
        self.thelist.pop(index)
        self.widgets.removeRow(index)
        self.entries.pop(index)
        window.updateviewport(window.playbackframe)
    def add(self):
        
        self.thelist.append("")
        i = len(self.thelist)-1
        self.entries.append(QRedTextEntryListProperty(None,self.thelist,i))
        arow = QHBoxLayout()
        arow.addWidget(self.entries[i])
        arow.addWidget(QRedButton(None,"/\\",0,0,self.moveup,False,arow))
        arow.addWidget(QRedButton(None,"\\/",0,0,self.movedown,False,arow))
        arow.addWidget(QRedButton(None,"-",0,0,self.remove,False,arow))
        self.widgets.addRow("button",arow)
        self.parentclass.updateviewport(self.parentclass.playbackframe)
        #print(self.thelist)
class QRedDropDownFrame(QRedFrame):
    def __init__(self,parent,name):
        super().__init__(parent)
        
        self.whole = QVBoxLayout(self)
        self.collapseButton = QRedExpandableButton(None,name,self.collapse)
        self.mainView = QRedFrame(self)
        self.widgets = QFormLayout(self.mainView)
        
        self.mainView.setLayout(self.widgets)
        self.mainView.sizePolicy().setVerticalPolicy(QSizePolicy.Policy.Minimum)
        self.mainView.sizePolicy().setHorizontalPolicy(QSizePolicy.Policy.Preferred)
        self.whole.addWidget(self.collapseButton)
        self.whole.addWidget(self.mainView)
        self.setLayout(self.whole)
        self.collapsed = False
        self.whole.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.whole.setSizeConstraint(QVBoxLayout.SizeConstraint.SetNoConstraint)
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




class CzeKeyframeOptionCategory(QRedDropDownFrame):
    def __init__(self,parent,name:str,params:Params,parentclass):
        super().__init__(parent,name)
        self.parentclass = parentclass
        self.params = params
        
        self.whole.insertWidget(0,QRedSelectableProperty(None,params.function,self.parentclass,self.rebuild))
        self.iterate(self.params.params)
    def rebuild(self,name,index):
        self.params.function.index = index
        for i in range(self.widgets.rowCount()):
            self.widgets.removeRow(0)
        self.params.params = self.params.function().params.copy()
        self.iterate(self.params.params)
        
        self.parentclass.updateviewport(self.parentclass.playbackframe)
    def updateParam(self):
        for i in range(self.widgets.rowCount()):
            self.widgets.itemAt(i,QFormLayout.FieldRole).widget().updateself()
        
            
            
    def regenerate(self,params):
        toremove = self.whole.itemAt(0).widget()
        self.whole.removeItem(self.whole.itemAt(0))
        toremove.setParent(None)
        toremove.destroy()
        self.whole.insertWidget(0,QRedSelectableProperty(None,params.function,self.parentclass,self.rebuild))
        for i in range(self.widgets.rowCount()):
            self.widgets.removeRow(0)
        self.params = params
        self.iterate(self.params.params)
        self.parentclass.updateviewport(self.parentclass.playbackframe)
    def iterate(self,params):

        for key in vars(params).keys():     
            param = params[key]
            #print(key,type(param),param.__class__)
            if(hasattr(param,"widget")):
                self.widgets.addRow(key,param.widget())
            """if isinstance(param,str):
                self.widgets.addRow(key,QRedTextProperty(None,params,key,self.parentclass))
            elif isinstance(param,StringList):
                self.widgets.addRow(key,QRedTextListProperty(None,param,self.parentclass))
            elif isinstance(param,list):
                self.iteratelist(param)
            elif isinstance(param,Params):
                self.iterate(param)
            elif isinstance(param,int):
                self.widgets.addRow(key,QRedNumberProperty(None,params,key,self.parentclass))
            elif isinstance(param,Selectable):
                self.widgets.addRow(key,QRedSelectableProperty(None,param,self.parentclass))"""
    def iteratelist(self,thelist):
        i = 0
        for param in thelist:
            #print(type(param))
            if isinstance(param,str):
                self.widgets.addRow("",QRedTextProperty(None,thelist,i,self.parentclass))
            
            elif isinstance(param,StringList):
                self.widgets.addRow("",QRedTextListProperty(None,param,self.parentclass))
            elif isinstance(param,list):
                self.iteratelist(param)
            elif isinstance(param,Params):
                self.iterate(param)
            elif isinstance(param,int):
                self.widgets.addRow("",QRedNumberProperty(None,thelist,i,self.parentclass))
            elif isinstance(param,Selectable):
                self.widgets.addRow("",QRedSelectableProperty(None,param,self.parentclass))
            i+=1
class CzeKeyframeOptionCategoryList(QRedFrame):
    def __init__(self,parent,thelist,baseparam,parentclass):
        super().__init__(parent)
        self.parentclass = parentclass
        self.baseparam = baseparam
        self.whole = QVBoxLayout(self)
        self.whole.setSpacing(2)
        self.whole.setContentsMargins(2,2,2,2)
        self.collapseButton = QRedExpandableButton(None,"expand",self.collapse)
        self.collapseButton.sizePolicy().setHorizontalPolicy(QSizePolicy.Policy.MinimumExpanding)
        self.collapseButton.setMinimumWidth(60)
        self.mainView = QRedFrame(self)
        self.withbuttons = QGridLayout()
        self.withbuttons.setSpacing(2)
        self.withbuttons.setContentsMargins(2,2,2,2)
        self.widgets = QFormLayout()
        self.widgets.setSpacing(2)
        self.widgets.setContentsMargins(2,2,2,2)
        self.thelist = thelist
        self.entries = []
        self.widgetbuttons = QGridLayout()
        for i in range(len(self.thelist)):
            self.entries.append(CzeKeyframeOptionCategory(None,"expand/collapse",self.thelist[i],parentclass))
            arow = QHBoxLayout()
            arow.addWidget(self.entries[i])
            buttons = QVBoxLayout()
            buttons.addWidget(QRedButton(None,"/\\",0,0,self.moveup,False,arow))
            buttons.addWidget(QRedButton(None,"\\/",0,0,self.movedown,False,arow))
            buttons.addWidget(QRedButton(None,"-",0,0,self.remove,False,arow))
            arow.addLayout(buttons)
            self.widgets.addRow("",arow)
        self.withbuttons.addLayout(self.widgets,0,0)
        self.withbuttons.addLayout(self.widgetbuttons,0,1)
        self.withbuttons.addWidget(QRedExpandableButton(None,"+",self.add),1,0)
        self.mainView.setLayout(self.withbuttons)
        self.mainView.sizePolicy().setVerticalPolicy(QSizePolicy.Policy.Minimum)
        self.mainView.sizePolicy().setHorizontalPolicy(QSizePolicy.Policy.Preferred)
        self.whole.addWidget(self.collapseButton)
        self.whole.addWidget(self.mainView)
        #self.whole.addWidget(QRedExpandableButton(None,"+",self.add))
        self.setLayout(self.whole)
        self.collapsed = False
        self.whole.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.whole.setSizeConstraint(QVBoxLayout.SizeConstraint.SetNoConstraint)
        #print(self.mainView.maximumHeight())
        #self.setMaximumHeight(200)
        self.mainView.setStyleSheet("border-width:0px; background:none;")
    def updateParam(self):
        for widget in self.entries:
            widget.updateParam()
    def regenerate(self,thelist,baseparam):
        self.baseparam = baseparam
        self.thelist = thelist
        i = 0
        
        for element in thelist:
            self.entries[i].regenerate(element)
            i+=1
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
        #self.entries[index].updatetextbox()
        #self.entries[index-1].updatetextbox()
        window.updateviewport(window.playbackframe)
    def movedown(self,arow):
        index = self.widgets.getLayoutPosition(arow)[0]
        if index == len(self.thelist)-1:
            return
        self.thelist[index],self.thelist[index+1] = self.thelist[index+1],self.thelist[index]
        #self.entries[index].updatetextbox()
        #self.entries[index+1].updatetextbox()
        window.updateviewport(window.playbackframe)
    def remove(self,arow):
        index = self.widgets.getLayoutPosition(arow)[0] #no idea why it has to be [0]. it returns a tuple that looks like this (4, <ItemRole.FieldRole: 1>)
        self.thelist.pop(index)
        self.widgets.removeRow(index)
        self.entries.pop(index)
        window.updateviewport(window.playbackframe)
    def add(self):
        
        self.thelist.append(self.baseparam.copy())
        i = len(self.thelist)-1
        self.entries.append(CzeKeyframeOptionCategory(None,"expand/collapse",self.thelist[i],self.parentclass))
        #print([self.thelist[i].params],[self.baseparam.params])
        arow = QHBoxLayout()
        arow.addWidget(self.entries[i])
        buttons = QVBoxLayout()
        buttons.addWidget(QRedButton(None,"/\\",0,0,self.moveup,False,arow))
        buttons.addWidget(QRedButton(None,"\\/",0,0,self.movedown,False,arow))
        buttons.addWidget(QRedButton(None,"-",0,0,self.remove,False,arow))
        arow.addLayout(buttons)
        self.widgets.addRow("button",arow)
        window.updateviewport(window.playbackframe)
"""class CzeKeyframeOptionCategoryList(QRedDropDownFrame):
    def __init__(self,parent,name,parentclass,listofparams):
        super().__init__(parent,name)
        self.parentclass = parentclass
        self.listofparams = listofparams
        self.iterate(listofparams)
    def iterate(self,listofparams):
        for param in listofparams:
            if isinstance(param,Params):
                self.widgets()"""
class CzeKeyframeOptions(QRedScrollArea):
    def __init__(self,parent,parentclass):
        #self.params = keyframes[0].params
        self.params = Params({})
        super().__init__(parent)
        self.parentclass = parentclass
        self.viewframe = QRedFrame(None)
        #self.alayout = QVBoxLayout()
        self.widgets = QVBoxLayout()
        self.widgets.setSpacing(2)
        self.widgets.setContentsMargins(2,2,2,2)
        #dropdo = QRedDropDownFrame(None,"yo")
        self.iterate(self.params)
        #dropdo2 = QRedDropDownListFrame(None)
        #self.widgets.addWidget(dropdo2)
        self.viewframe.setLayout(self.widgets)
        self.widgets.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setWidget(self.viewframe)
        self.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Expanding)
        
        #self.widgets.setAlignment(Qt.AlignmentFlag.AlignTop)
        #self.alayout.addWidget(self.viewframe)
        self.setWidgetResizable(True)
    def sizeHint(self):
        return QSize(1280,250)
    def changeEvent(self, arg__1) -> None:
        if(hasattr(self,"viewframe")):
            self.setMaximumWidth(self.viewframe.contentsRect().width()+self.verticalScrollBar().width())
        return super().changeEvent(arg__1)
    def resizeEvent(self, arg__1) -> None:
        if(hasattr(self,"viewframe")):
            self.setMaximumWidth(self.viewframe.contentsRect().width()+self.verticalScrollBar().width())
        return super().resizeEvent(arg__1)
    def iterate(self,params):
        for key in vars(params).keys():
            param = params[key]
            if isinstance(param,Params):
                self.widgets.addWidget(CzeKeyframeOptionCategory(None,"Expand/Collapse",param,self.parentclass)) #Make it display the actual name!
            elif isinstance(param,list):
                self.widgets.addWidget(CzeKeyframeOptionCategoryList(None,param,baseparams[key],self.parentclass))
                #for i in param:
                #    if isinstance(i,Params):
                #        self.widgets.addWidget(CzeKeyframeOptionCategory(None,"Expand/Collapse",i))
                #Add a + button here to add more entries
    def iterateUpdate(self,params):
        i = 0
        for key in vars(params).keys():
            param = params[key]
            if isinstance(param,Params):
                self.widgets.itemAt(i).widget().updateParam()
            elif isinstance(param,list):
                self.widgets.itemAt(i).widget().updateParam()
            i += 1
    def iterateRegenerate(self,params):
        if(self.widgets.count() == 0):
            self.params = params
            self.rebuild()
            return
        i = 0
        for key in vars(params).keys():
            param = params[key]
            if isinstance(param,Params):
                self.widgets.itemAt(i).widget().regenerate(param)
            elif isinstance(param,list):
                self.widgets.itemAt(i).widget().regenerate(param,baseparams[key])
            i += 1
        self.setMaximumWidth(self.viewframe.contentsRect().width()+self.verticalScrollBar().width())
    def rebuild(self):
        if self.parentclass.selectedframe:
            self.params = self.parentclass.selectedframe.params
            for i in range(self.widgets.count()):
                self.widgets.itemAt(0).widget().setParent(None)
            self.iterate(self.params)
        else:
            for i in range(self.widgets.count()):
                self.widgets.itemAt(0).widget().setParent(None)
        self.setMaximumWidth(self.viewframe.contentsRect().width()+self.verticalScrollBar().width())
    def update(self):
        if self.parentclass.selectedframe:
            self.params = self.parentclass.selectedframe.params
            self.iterateUpdate(self.params)
        else:
            for i in range(self.widgets.count()):
                self.widgets.itemAt(0).widget().setParent(None)
    def regenerate(self):
        if self.parentclass.selectedframe:
            self.params = self.parentclass.selectedframe.params
            self.iterateRegenerate(self.params)
        else:
            for i in range(self.widgets.count()):
                self.widgets.itemAt(0).widget().setParent(None)
        self.setMaximumWidth(self.viewframe.contentsRect().width()+self.verticalScrollBar().width())
class CzeViewportDraggableBox(QGraphicsItem):
    def __init__(self,parent,parentclass,params,x,y):
        super().__init__(parent)
        self.params = params
        self.xparam = x
        self.yparam = y
        self.parentclass = parentclass
        #self.setPos(self.x,self.y)
        self.setCursor(Qt.CursorShape.CrossCursor)
    def boundingRect(self) -> QRectF:
        return QRectF(-4,-4,7,7)
    def paint(self, painter: QPainter, option, widget: Optional[QWidget] = ...) -> None:
        self.setPos(self.params[self.xparam]/1280*self.parentclass.picture.width(),self.params[self.yparam]/720*self.parentclass.picture.height())
        painter.setPen(QPen(QColor(255,255,255),1))
        painter.drawEllipse(QRectF(-4,-4,7,7))
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
    def updateviewport(self,theframe):
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