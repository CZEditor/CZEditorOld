from generate import *
from PIL import Image
from functools import cache
from util import *
from PySide6.QtWidgets import QWidget,QGraphicsScene,QGraphicsView,QGraphicsItem,QGraphicsRectItem,QGraphicsLineItem,QToolButton,QPushButton,QComboBox,QFrame,QSizePolicy,QScrollArea,QPlainTextEdit,QSpinBox,QLineEdit,QFormLayout
from PySide6.QtGui import QPen,QColor,QRadialGradient,QResizeEvent,QMouseEvent,QWheelEvent,QDrag,QDragEnterEvent,QDragLeaveEvent,QDragMoveEvent,QDropEvent,QTextOption,QKeyEvent
from PySide6.QtCore import QSize,Qt,QRectF,QPoint,QLine,QMimeData,Qt
from keyframes import *
from copy import deepcopy
from base_ui import *
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
        self.parentclass.updateviewport()

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
        self.parentclass.updateviewport()

    def updateself(self):
        self.textbox.onchange = dummyfunction
        self.textbox.setText(self.param[self.index])
        self.textbox.onchange = self.updateproperty
        self.parentclass.updateviewport()

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
        self.parentclass.updateviewport()

    def movedown(self,arow):
        index = self.widgets.getLayoutPosition(arow)[0]
        if index == len(self.thelist)-1:
            return
        self.thelist[index],self.thelist[index+1] = self.thelist[index+1],self.thelist[index]
        self.entries[index].updatetextbox()
        self.entries[index+1].updatetextbox()
        self.parentclass.updateviewport()

    def remove(self,arow):
        index = self.widgets.getLayoutPosition(arow)[0] #no idea why it has to be [0]. it returns a tuple that looks like this (4, <ItemRole.FieldRole: 1>)
        self.thelist.pop(index)
        self.widgets.removeRow(index)
        self.entries.pop(index)
        self.parentclass.updateviewport()

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
        self.parentclass.updateviewport()

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
        
        self.parentclass.updateviewport()

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
        self.parentclass.updateviewport()

    def iterate(self,params):
        for key in vars(params).keys():     
            param = params[key]
            if(hasattr(param,"widget")):
                self.widgets.addRow(key,param.widget())
        
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
        self.parentclass.updateviewport()

    def movedown(self,arow):
        index = self.widgets.getLayoutPosition(arow)[0]
        if index == len(self.thelist)-1:
            return
        self.thelist[index],self.thelist[index+1] = self.thelist[index+1],self.thelist[index]
        #self.entries[index].updatetextbox()
        #self.entries[index+1].updatetextbox()
        self.parentclass.updateviewport()

    def remove(self,arow):
        index = self.widgets.getLayoutPosition(arow)[0] #no idea why it has to be [0]. it returns a tuple that looks like this (4, <ItemRole.FieldRole: 1>)
        self.thelist.pop(index)
        self.widgets.removeRow(index)
        self.entries.pop(index)
        self.parentclass.updateviewport()

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
        self.parentclass.updateviewport()

class CzeKeyframeOptions(QRedScrollArea):
    baseparams = Params({  #BAD!!! TODO : While we wont support anything else than sources, effects and actions, but we can still generalize this.
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
    def __init__(self,parent,parentclass):
        self.params = Params({})

        super().__init__(parent)

        self.parentclass = parentclass
        self.viewframe = QRedFrame(None)

        self.widgets = QVBoxLayout()
        self.widgets.setSpacing(2)
        self.widgets.setContentsMargins(2,2,2,2)

        self.iterate(self.params)

        self.viewframe.setLayout(self.widgets)

        self.widgets.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setWidget(self.viewframe)

        self.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Expanding)
        
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
                self.widgets.addWidget(CzeKeyframeOptionCategoryList(None,param,self.baseparams[key],self.parentclass))

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
                self.widgets.itemAt(i).widget().regenerate(param,self.baseparams[key])
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
            self.parentclass.updateviewport()
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
                self.parentclass.updateviewport()
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
                self.parentclass.updateviewport()
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
            self.parentclass.updateviewport()
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
