from multiprocessing import dummy
import numpy as np
import moviepy.editor as mpy
import moviepy.config as mpyconfig
from imagefunctions import NormalImage,XPError
from statefunctions import NormalKeyframe
from compositingfunctions import ImageComposite
from util import *
from PySide6.QtWidgets import QAbstractButton,QMainWindow,QApplication,QFrame,QScrollArea,QSplitter,QWidget,QGraphicsScene,QGraphicsView,QGraphicsItem,QGraphicsSceneMouseEvent,QComboBox,QPlainTextEdit,QLabel,QVBoxLayout,QHBoxLayout,QSizePolicy,QFormLayout,QLineEdit,QGridLayout,QSpinBox,QGraphicsPixmapItem
from PySide6.QtGui import QPixmap,QPainter,QPen,QBrush,QColor,QRadialGradient,QResizeEvent,QMouseEvent,QWheelEvent,QTextOption,QKeyEvent
from PySide6.QtCore import QSize,Qt,QRectF,QPoint,QLine,SIGNAL,QTimerEvent
from PIL import Image,ImageQt
from ui import *
from typing import *
import sys
from keyframes import *
from time import time


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
class QRedSpinBox(QSpinBox):
    def __init__(self,parent,onchange=dummyfunction):
        super().__init__(parent)
        self.onchange = onchange
        self.setStyleSheet("border-image:url(editor/Text Box.png) 2; border-width:2;")
        self.setMaximum(50000)
        self.setMinimum(-50000)
        self.valueChanged.connect(self.change)
    def change(self) -> None:
        self.onchange(self.value()) 
class QRedComboBox(QComboBox):
    def __init__(self,parent,elements=[],onchange=dummyfunction):
        super().__init__(parent)
        self.onchange = onchange
        
        self.setStyleSheet("border-image:url(editor/Text Box.png) 2; border-width:2;")
        self.addItems(elements)
        self.currentIndexChanged.connect(self.valuechanged)
    def valuechanged(self,index) -> None:
        self.onchange(self.currentText(),self.currentIndex()) 
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
        window.updateviewport(window.playbackframe)
    def updatetextbox(self):
        self.textbox.onchange = dummyfunction
        self.textbox.setPlainText(self.param[self.index])
        self.textbox.onchange = self.updateproperty
class QRedNumberProperty(QRedFrame):
    def __init__(self,parent,param:Params,index):
        super().__init__(parent)
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
        window.updateviewport(window.playbackframe)
    def updatetextbox(self):
        self.textbox.onchange = dummyfunction
        self.textbox.setValue(self.param[self.index])
        self.textbox.onchange = self.updateproperty
class QRedSelectableProperty(QRedFrame):
    def __init__(self,parent,param:Selectable,override=None):
        super().__init__(parent)
        if override==None:
            override = self.updateproperty
        self.param = param
        self.widgets = QHBoxLayout()
        self.combobox = QRedComboBox(self,self.param.names,override)
        self.combobox.setCurrentIndex(self.param.index)
        self.widgets.addWidget(self.combobox)
        
        self.setLayout(self.widgets)
        self.setStyleSheet("border-width:0px;")
    def updateproperty(self,name,index):
        #print("setting:",value)
        self.param.index = index
        window.updateviewport(window.playbackframe)
    def updateself(self):
        self.combobox.onchange = dummyfunction
        self.combobox.setCurrentIndex(self.param.index)
        self.combobox.onchange = self.updateproperty
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
        window.updateviewport(window.playbackframe)
    def updatetextbox(self):
        self.textbox.onchange = dummyfunction
        self.textbox.setText(self.param[self.index])
        self.textbox.onchange = self.updateproperty
        window.updateviewport(window.playbackframe)
class QRedTextListProperty(QRedFrame):
    def __init__(self,parent,thelist):
        super().__init__(parent)
        
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
            arow.addWidget(QRedButton(None,"/\\",0,0,self.moveup,CreateRedSmallButton,False,arow))
            arow.addWidget(QRedButton(None,"\\/",0,0,self.movedown,CreateRedSmallButton,False,arow))
            arow.addWidget(QRedButton(None,"-",0,0,self.remove,CreateRedSmallButton,False,arow))
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
        arow.addWidget(QRedButton(None,"/\\",0,0,self.moveup,CreateRedSmallButton,False,arow))
        arow.addWidget(QRedButton(None,"\\/",0,0,self.movedown,CreateRedSmallButton,False,arow))
        arow.addWidget(QRedButton(None,"-",0,0,self.remove,CreateRedSmallButton,False,arow))
        self.widgets.addRow("button",arow)
        window.updateviewport(window.playbackframe)
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
    def __init__(self,parent,name:str,params:Params):
        super().__init__(parent,name)
        self.whole.insertWidget(0,QRedSelectableProperty(None,params.function,self.rebuild))
        self.params = params
        self.iterate(self.params.params)
    def rebuild(self,name,index):
        #print(vars(self))
        self.params.function.index = index
        for i in range(self.widgets.rowCount()):
            self.widgets.removeRow(0)
        self.params.params = self.params.function().params.copy()
        self.iterate(self.params.params)
        window.updateviewport(window.playbackframe)
    def changekeyframe(self,name,params):
        self.whole.removeWidget(self.whole.children()[0])
        self.whole.insertWidget(0,QRedSelectableProperty(None,params.function,self.rebuild))
        for i in range(self.widgets.rowCount()):
            self.widgets.removeRow(0)
        self.params = params
        self.iterate(self.params.params)
        window.updateviewport(window.playbackframe)
    def iterate(self,params):
        for key in vars(params).keys():     
            param = params[key]
            #print(key,type(param),param.__class__)
            if isinstance(param,str):
                self.widgets.addRow(key,QRedTextProperty(None,params,key))
            elif isinstance(param,StringList):
                self.widgets.addRow(key,QRedTextListProperty(None,param))
            elif isinstance(param,list):
                self.iteratelist(param)
            elif isinstance(param,Params):
                self.iterate(param)
            elif isinstance(param,int):
                self.widgets.addRow(key,QRedNumberProperty(None,params,key))
            elif isinstance(param,Selectable):
                self.widgets.addRow(key,QRedSelectableProperty(None,param))
    def iteratelist(self,thelist):
        i = 0
        for param in thelist:
            #print(type(param))
            if isinstance(param,str):
                self.widgets.addRow("",QRedTextProperty(None,thelist,i))
            
            elif isinstance(param,StringList):
                self.widgets.addRow("",QRedTextListProperty(None,param))
            elif isinstance(param,list):
                self.iteratelist(param)
            elif isinstance(param,Params):
                self.iterate(param)
            elif isinstance(param,int):
                self.widgets.addRow("",QRedNumberProperty(None,thelist,i))
            elif isinstance(param,Selectable):
                self.widgets.addRow("",QRedSelectableProperty(None,param))
            i+=1
class CzeKeyframeOptionCategoryList(QRedFrame):
    def __init__(self,parent,thelist,baseparam):
        super().__init__(parent)
        self.baseparam = baseparam
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
            self.entries.append(CzeKeyframeOptionCategory(None,"expand/collapse",self.thelist[i]))
            arow = QHBoxLayout()
            arow.addWidget(self.entries[i])
            arow.addWidget(QRedButton(None,"/\\",0,0,self.moveup,CreateRedSmallButton,False,arow))
            arow.addWidget(QRedButton(None,"\\/",0,0,self.movedown,CreateRedSmallButton,False,arow))
            arow.addWidget(QRedButton(None,"-",0,0,self.remove,CreateRedSmallButton,False,arow))
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
        
        self.thelist.append(self.baseparam.copy())
        i = len(self.thelist)-1
        self.entries.append(CzeKeyframeOptionCategory(None,"expand/collapse",self.thelist[i]))
        arow = QHBoxLayout()
        arow.addWidget(self.entries[i])
        arow.addWidget(QRedButton(None,"/\\",0,0,self.moveup,CreateRedSmallButton,False,arow))
        arow.addWidget(QRedButton(None,"\\/",0,0,self.movedown,CreateRedSmallButton,False,arow))
        arow.addWidget(QRedButton(None,"-",0,0,self.remove,CreateRedSmallButton,False,arow))
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
        self.params = keyframes[0].params
        super().__init__(parent)
        self.parentclass = parentclass
        self.viewframe = QRedFrame(None)
        #self.alayout = QVBoxLayout()
        self.widgets = QVBoxLayout()
        #dropdo = QRedDropDownFrame(None,"yo")
        self.iterate(self.params)
        #dropdo2 = QRedDropDownListFrame(None)
        #self.widgets.addWidget(dropdo2)
        self.viewframe.setLayout(self.widgets)
        self.widgets.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setWidget(self.viewframe)
        self.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Preferred)
        
        #self.widgets.setAlignment(Qt.AlignmentFlag.AlignTop)
        #self.alayout.addWidget(self.viewframe)
        self.setWidgetResizable(True)
    def changeEvent(self, arg__1) -> None:
        self.setMaximumWidth(self.widgets.contentsRect().width()+self.verticalScrollBar().width())
        return super().changeEvent(arg__1)
    def iterate(self,params):
        for key in vars(params).keys():
            param = params[key]
            if isinstance(param,Params):
                self.widgets.addWidget(CzeKeyframeOptionCategory(None,"Expand/Collapse",param)) #Make it display the actual name!
            elif isinstance(param,list):
                self.widgets.addWidget(CzeKeyframeOptionCategoryList(None,param,baseparams[key]))
                #for i in param:
                #    if isinstance(i,Params):
                #        self.widgets.addWidget(CzeKeyframeOptionCategory(None,"Expand/Collapse",i))
                #Add a + button here to add more entries
    
    def rebuild(self):
        if self.parentclass.selectedframe:
            self.params = self.parentclass.selectedframe.params
            for i in range(self.widgets.count()):
                self.widgets.itemAt(0).widget().setParent(None)
            self.iterate(self.params)
        else:
            for i in range(self.widgets.count()):
                self.widgets.itemAt(0).widget().setParent(None)


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
class CzeViewport(QWidget):
    def __init__(self,parent,parentclass):
        super().__init__(parent)
        self.timestamp = 100
        self.scene = QGraphicsScene(self)
        self.graphicsview = QGraphicsView(self)
        self.graphicsview.setScene(self.scene)
        self.viewportimage = self.scene.addPixmap(QPixmap.fromImage(ImageQt.ImageQt(getviewportimage(self.timestamp))))
        self.parentclass = parentclass
        self.updateviewportimage(self.timestamp)
        
        #self.thelayout = QHBoxLayout()
       # self.setLayout(self.thelayout)
        #self.setMaximumSize(1280,720)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Ignored)
        self.handles = []
        #self.startTimer(0.01,Qt.TimerType.PreciseTimer)
       # self.isplaying = False
        #self.somehandle = CzeViewportDraggableHandle(None,self,ParamLink(keyframes[0].params.compositing[0].params,"x"),ParamLink(keyframes[0].params.compositing[0].params,"y"))
        #self.scene.addItem(self.somehandle)
    
    def updateviewportimage(self,i):
        image:Image.Image = getviewportimage(i)
        #image = image.resize(self.size().toTuple(),Image.Resampling.NEAREST)
        self.picture = QPixmap.fromImage(ImageQt.ImageQt(image))
        self.picture = self.picture.scaled(QSize(min(self.size().width(),1280),min(self.size().height(),720)),Qt.AspectRatioMode.KeepAspectRatio)
        self.timestamp = i
        self.viewportimage.setPixmap(self.picture)
    def createhandle(self,keyframe,function,param):  #self , keyframe of the handle , function of the param , param itself
        #print(vars(function))
        if hasattr(function,"handle"):
            handle = function.handle(keyframe,self,param)
            self.handles.append(handle)
            self.scene.addItem(handle)
    def updatehandles(self):
        for handle in self.handles:
            self.scene.removeItem(handle)
        self.createhandle(self.parentclass.selectedframe,self.parentclass.selectedframe.params.image.function(),self.parentclass.selectedframe.params)
        for param in self.parentclass.selectedframe.params.compositing:
            self.createhandle(self.parentclass.selectedframe,param.function(),param)
        for param in self.parentclass.selectedframe.params.states:
            self.createhandle(self.parentclass.selectedframe,param.function(),param)
        #self.viewportimage.setPos((self.width()-pic.width())/2,(self.height()-pic.height())/2)
    #def paintEvent(self, e):
    #    painter = QPainter(self)
    #   # print(self.size(),QSize(self.size().width(),self.size().height()))
    #    pic = self.picture.scaled(QSize(min(self.size().width(),1280),min(self.size().height(),720)),Qt.AspectRatioMode.KeepAspectRatio)
    #    painter.drawPixmap((self.width()-pic.width())/2,(self.height()-pic.height())/2,pic)
    #    self.somehandle.paint(painter)
    def resizeEvent(self, event:QResizeEvent) -> None:
        self.updateviewportimage(self.timestamp)
        self.graphicsview.setFixedSize(event.size())
        self.scene.setSceneRect(0,0,self.picture.width()-2,self.picture.height()-2)
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
        #rightsplitter = QSplitter(hozsplitter)
        topsplitter = QSplitter(hozsplitter)
        
        self.keyframeoptions = CzeKeyframeOptions(topsplitter,self)
        self.viewport = CzeViewport(topsplitter,self)
        self.presets = CzePresets(topsplitter,self)
        self.timeline = CzeTimeline(hozsplitter,self)
        self.selectedframe = None
        self.setCentralWidget(hozsplitter)
        self.show()
        self.playbackframe = 100
        self.draggedpreset = None
        self.startTimer(0.01,Qt.TimerType.PreciseTimer)
        self.isplaying = False
        self.starttime = time()
        self.startframe = self.playbackframe
    def updateviewport(self,theframe):
        self.viewport.updateviewportimage(theframe)
        #self.viewport.update()
    def updatekeyframeoptions(self):
        self.keyframeoptions.rebuild()
    def keyPressEvent(self, event: QKeyEvent) -> None:
        print(event.text())
        if event.text() == " ":
            self.isplaying = not self.isplaying
            self.starttime = time()
            self.startframe = self.playbackframe
        return super().keyPressEvent(event)
    def timerEvent(self, event: QTimerEvent) -> None:
        if self.isplaying:
            self.playbackframe = self.startframe+int((time()-self.starttime)*60)
            self.viewport.updateviewportimage(self.playbackframe)
            self.timeline.updateplaybackcursor(self.playbackframe)
        return super().timerEvent(event)
app = QApplication([])
window = Window()
sys.exit(app.exec())