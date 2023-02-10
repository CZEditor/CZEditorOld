from czeditor.generate import *
from PIL import Image
from functools import cache
from czeditor.util import *
from PySide6.QtWidgets import QWidget,QGraphicsScene,QGraphicsView,QGraphicsItem,QGraphicsRectItem,QGraphicsLineItem,QToolButton,QPushButton,QComboBox,QFrame,QSizePolicy,QScrollArea,QPlainTextEdit,QSpinBox,QLineEdit,QFormLayout,QGraphicsItemGroup,QGraphicsTextItem
from PySide6.QtGui import QPen,QColor,QRadialGradient,QResizeEvent,QMouseEvent,QWheelEvent,QDrag,QDragEnterEvent,QDragLeaveEvent,QDragMoveEvent,QDropEvent,QTextOption,QKeyEvent,QFont
from PySide6.QtCore import QSize,Qt,QRectF,QPoint,QLine,QMimeData,Qt,QEvent
from czeditor.keyframes import *
from czeditor.compositingfunctions import *
from czeditor.imagefunctions import *
from czeditor.statefunctions import *
from copy import deepcopy
from czeditor.base_ui import *
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
        if(params.function):
            self.whole.insertWidget(0,QRedSelectableProperty(None,params.function,self.parentclass,self.rebuild))
        self.iterate(self.params.params)
        self.parentclass.timeline.createKeyframeItem(self.parentclass.selectedframe,params)

    def rebuild(self,name,index):
        
        self.parentclass.timeline.deleteKeyframeItem(self.parentclass.selectedframe,self.params)
        self.params.function.index = index
        for i in range(self.widgets.rowCount()):
            self.widgets.removeRow(0)
        self.params.params = self.params.function().params.copy()
        self.iterate(self.params.params)
        self.parentclass.timeline.createKeyframeItem(self.parentclass.selectedframe,self.params)
        self.parentclass.updateviewport()

    def updateParam(self):
        for i in range(self.widgets.rowCount()):
            self.widgets.itemAt(i,QFormLayout.FieldRole).widget().updateself()
        
    def regenerate(self,params):
        if(params.function):
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
            buttons.addWidget(QRedButton(None,"/\\",self.moveup,arow))
            buttons.addWidget(QRedButton(None,"\\/",self.movedown,arow))
            buttons.addWidget(QRedButton(None,"-",self.remove,arow))
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
            if(i>=len(self.entries)):
                self.entries.append(CzeKeyframeOptionCategory(None,"expand/collapse",element,self.parentclass))
                arow = QHBoxLayout()
                arow.addWidget(self.entries[i])
                buttons = QVBoxLayout()
                buttons.addWidget(QRedButton(None,"/\\",self.moveup,arow))
                buttons.addWidget(QRedButton(None,"\\/",self.movedown,arow))
                buttons.addWidget(QRedButton(None,"-",self.remove,arow))
                arow.addLayout(buttons)
                self.widgets.addRow("",arow)
            else:
                self.entries[i].regenerate(element)
            i+=1
        
        initialLength = len(self.entries)

        if(len(thelist)<initialLength):
            while i < initialLength:
                self.widgets.removeRow(len(thelist))
                self.entries.pop(len(thelist))
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
        self.entries[index].regenerate(self.thelist[index])
        self.entries[index-1].regenerate(self.thelist[index-1])
        self.parentclass.updateviewport()

    def movedown(self,arow):
        index = self.widgets.getLayoutPosition(arow)[0]
        if index == len(self.thelist)-1:
            return
        self.thelist[index],self.thelist[index+1] = self.thelist[index+1],self.thelist[index]
        self.entries[index].regenerate(self.thelist[index])
        self.entries[index+1].regenerate(self.thelist[index+1])
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
        
        self.thelist.append(self.baseparam.copy())
        i = len(self.thelist)-1
        self.entries.append(CzeKeyframeOptionCategory(None,"expand/collapse",self.thelist[i],self.parentclass))
        #print([self.thelist[i].params],[self.baseparam.params])
        arow = QHBoxLayout()
        arow.addWidget(self.entries[i])
        buttons = QVBoxLayout()
        buttons.addWidget(QRedButton(None,"/\\",self.moveup,arow))
        buttons.addWidget(QRedButton(None,"\\/",self.movedown,arow))
        buttons.addWidget(QRedButton(None,"-",self.remove,arow))
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

        #self.whole = QVBoxLayout()

        #self.whole.addWidget(self.keyframeNameWidget)

        self.widgets = QVBoxLayout()
        self.widgets.setSpacing(2)
        self.widgets.setContentsMargins(2,2,2,2)

        self.iterate(self.params)

        #self.whole.addLayout(self.widgets)

        self.viewframe.setLayout(self.widgets)

        self.widgets.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setWidget(self.viewframe)

        self.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Expanding)
        
        self.setWidgetResizable(True)

    def sizeHint(self):
        return QSize(400,720)

    
    """def changeEvent(self, arg__1) -> None:
        if(hasattr(self,"viewframe")):
            self.setMaximumWidth(self.viewframe.contentsRect().width()+self.verticalScrollBar().width())
        return super().changeEvent(arg__1)

    def resizeEvent(self, arg__1) -> None:
        if(hasattr(self,"viewframe")):
            self.setMaximumWidth(self.viewframe.contentsRect().width()+self.verticalScrollBar().width())
        return super().resizeEvent(arg__1)"""

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
            self.rebuild(params)
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

    def rebuild(self,params=None):
        if params:
            self.params = params
            for i in range(self.widgets.count()):
                self.widgets.itemAt(0).widget().setParent(None)
            self.iterate(self.params)
        elif self.parentclass.selectedframe:
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

    def regenerate(self,keyframe=None):
        if keyframe:
            self.params = keyframe.params
            self.iterateRegenerate(self.params)
        elif self.parentclass.selectedframe:
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
        self.ondoubleclick = dummyfunction
        self.onscroll = dummyfunction
        self.dragenter = dummyfunction
        self.dragmove = dummyfunction
        self.dragdrop = dummyfunction
        self.setMouseTracking(True)
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
        self.previousmouse = event.pos()
        return super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:

        self.ondoubleclick(event)
        self.previousmouse = event.pos()
        return super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event) -> None:
        self.onscroll(event)
        return super().wheelEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        self.dragenter(event)

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        self.dragmove(event)

    def dropEvent(self, event:QDropEvent) -> None:
        self.dragdrop(event)
    


class CzeTimelineKeyframeItem(QGraphicsItem):
    coolgradient = QRadialGradient(50,50,90)
    coolgradient.setColorAt(1,QColor(255,255,255))
    coolgradient.setColorAt(0,QColor(255,0,0))
    selectedcoolgradient = QRadialGradient(30,30,60)
    selectedcoolgradient.setColorAt(1,QColor(255,127,127))
    selectedcoolgradient.setColorAt(0,QColor(255,0,0))

    def __init__(self,keyframe):
        super().__init__()
        self.keyframe = keyframe
        self.currentBrush = self.coolgradient

    def boundingRect(self):
        return QRectF(-30,-15,60,48)

    def paint(self, painter: QPainter, option, widget) -> None:
        painter.setPen(QPen(QColor(0,0,0),0))
        painter.setBrush(self.currentBrush)
        painter.drawPolygon([QPoint(-15,0),QPoint(0,-15),QPoint(15,0),QPoint(0,15)])
        painter.setPen(QPen(QColor(255,255,255),0))
        painter.setFont(QFont("Arial",8))
        painter.drawText(QRectF(-30,16,60,32),self.keyframe.params.properties.params.name(),Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

    def setBrush(self, brush):
        self.currentBrush = brush





class CzeTimeline(QWidget):
    coolgradient = QRadialGradient(50,50,90)
    coolgradient.setColorAt(1,QColor(255,255,255))
    coolgradient.setColorAt(0,QColor(255,0,0))
    selectedcoolgradient = QRadialGradient(30,30,60)
    selectedcoolgradient.setColorAt(1,QColor(255,127,127))
    selectedcoolgradient.setColorAt(0,QColor(255,0,0))
    hovergradient = QRadialGradient(50,50,120)
    hovergradient.setColorAt(1,QColor(255,255,255))
    hovergradient.setColorAt(0,QColor(255,0,0))
    def __init__(self,parent,parentclass):
        self.keyframes = {}
        self.keyframeitems = {}
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
        for keyframe in self.parentclass.keyframes:
            self.addKeyframe(keyframe)
        boundingrect = self.graphicsview.mapToScene(self.graphicsview.viewport().geometry()).boundingRect()
        self.playbackcursor = self.scene.addLine(QLine(playbackframe,boundingrect.top(),playbackframe,boundingrect.bottom()),QPen(QColor(255,0,0),0))
        self.draggedframe = None
        self.graphicsview.onpress = self.pressEvent
        self.graphicsview.onrelease = self.releaseEvent
        self.graphicsview.onmove = self.mmoveEvent
        self.graphicsview.onscroll = self.zoom
        self.graphicsview.ondoubleclick = self.doubleClickEvent
        #self.graphicsview.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        #self.graphicsview.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.graphicsview.verticalScrollBar().setMaximum(200000000)
        self.graphicsview.horizontalScrollBar().setMaximum(200000000)
        
        self.setAcceptDrops(True)
        self.graphicsview.setAcceptDrops(True)
        self.graphicsview.viewport().setAcceptDrops(True)
        self.graphicsview.dragenter = self.dragEnterEvent
        self.graphicsview.dragdrop = self.dropEvent
        self.graphicsview.dragmove = self.dragMoveEvent
        self.seekingBackground = None
        self.seekingText = None
        self.startTimer(0.25,Qt.TimerType.CoarseTimer)
        self.hoveredkeyframe = None

    def timerEvent(self, event) -> None:
        self.updateSeekingState()
        return super().timerEvent(event)

    def sizeHint(self):
        return QSize(self.size().width(),150)

    def updateplaybackcursor(self,frame):
        boundingrect = self.graphicsview.mapToScene(self.graphicsview.viewport().geometry()).boundingRect()
        self.playbackcursor.setLine(QLine(frame,boundingrect.top(),frame,boundingrect.bottom()))

    def updateSeekingState(self):
        if self.parentclass.seeking and not self.seekingBackground:
            self.seekingBackground = self.scene.addPolygon(self.graphicsview.mapToScene(self.rect()),QColor(127,127,127,127),QColor(127,127,127,127))
            self.seekingText = self.scene.addText("Seeking...",QFont("Arial",12))
            self.seekingText.setPos(self.graphicsview.mapToScene(self.rect().center()))
        elif not self.parentclass.seeking and self.seekingBackground:
            self.scene.removeItem(self.seekingBackground)
            self.scene.removeItem(self.seekingText)
            self.seekingBackground = None
            self.seekingText = None

    def mmoveEvent(self, event:QMouseEvent,prevpos:QPoint) -> None:

        if event.buttons() & Qt.MouseButton.MiddleButton:

            delta = (event.pos()-prevpos)*(self.graphicsview.sceneRect().width()/self.size().width())
            self.graphicsview.translate(delta.x(),delta.y())

            boundingrect = self.graphicsview.mapToScene(self.graphicsview.viewport().geometry()).boundingRect()
            self.playbackcursor.setLine(QLine(self.parentclass.playbackframe,boundingrect.top(),self.parentclass.playbackframe,boundingrect.bottom()))

        if not (event.buttons() & Qt.MouseButton.LeftButton):

                

            founditem:QGraphicsItem = self.graphicsview.itemAt(event.pos())
            if isinstance(founditem,CzeTimelineKeyframeItem):
                if founditem != self.hoveredkeyframe and self.hoveredkeyframe:
                    self.hoveredkeyframe.setBrush(self.coolgradient)
                    if founditem.currentBrush == self.coolgradient:
                        founditem.setBrush(self.hovergradient)
                        self.hoveredkeyframe = founditem
                    self.graphicsview.update()
                else:
                    if founditem.currentBrush == self.coolgradient:
                        founditem.setBrush(self.hovergradient)
                        self.hoveredkeyframe = founditem
                        self.graphicsview.update()
            else:
                if founditem != self.hoveredkeyframe and self.hoveredkeyframe:
                    if(self.hoveredkeyframe.currentBrush == self.hovergradient):
                        self.hoveredkeyframe.setBrush(self.coolgradient)
                    self.hoveredkeyframe = None
                    self.graphicsview.update()

        if self.draggedframe and self.graphicsview.geometry().contains(event.pos()):

            mapped = self.graphicsview.mapToScene(event.pos())

            self.parentclass.keyframes.setframe(self.draggedframe,int(mapped.x()))
            self.parentclass.keyframes.setlayer(self.draggedframe,-round(mapped.y()/25))

            self.keyframes[self.draggedframe].setPos(self.draggedframe.frame,-self.draggedframe.layer*25)

            self.parentclass.updateviewport()

        return super().mouseMoveEvent(event)
    
    def deselectFrame(self):
        if self.parentclass.selectedframe:
            self.keyframes[self.parentclass.selectedframe].setBrush(self.coolgradient)
            self.parentclass.selectedframe = None
            self.parentclass.updatekeyframeoptions()
            self.parentclass.viewport.updatehandles()
            self.graphicsview.update()

    def doubleClickEvent(self,event:QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            founditem:QGraphicsItem = self.graphicsview.itemAt(event.pos().x(),event.pos().y())
            if isinstance(founditem,CzeTimelineKeyframeItem):
                self.parentclass.draggedpreset = founditem.keyframe.copy()
                drag = QDrag(self)
                mime = QMimeData()
                drag.setMimeData(mime)
                drag.exec_(Qt.MoveAction)
            else:
                self.deselectFrame()
    def pressEvent(self, event:QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            founditem:QGraphicsItem = self.graphicsview.itemAt(event.pos().x(),event.pos().y())
            if isinstance(founditem,CzeTimelineKeyframeItem) or founditem is None:
                if founditem != None:
                    self.draggedframe = founditem.keyframe
                    if self.parentclass.selectedframe:
                        self.keyframes[self.parentclass.selectedframe].setBrush(self.coolgradient)
                    founditem.setBrush(self.selectedcoolgradient)
                    self.parentclass.selectedframe = founditem.keyframe
                    self.parentclass.regeneratekeyframeoptions()
                    self.parentclass.viewport.updatehandles()
                    self.graphicsview.update()
                    
                else:
                    self.parentclass.seek(self.graphicsview.mapToScene(event.pos().x(),0).x())
                    self.updateplaybackcursor(self.graphicsview.mapToScene(event.pos().x(),0).x())
                    self.parentclass.updateviewport()
                    self.graphicsview.update()
                    
            #elif hasattr(founditem,"pressEvent"):
            #    founditem.pressEvent(event,self.graphicsview.mapToScene(event.pos().x(),0).toPoint()) # TODO : Give more parameters to the function

            self.lastm1pos = event.pos()
       
        return super().mousePressEvent(event)
    
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        event.accept()
    
    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        event.accept()
    
    def dropEvent(self, event: QDropEvent) -> None:
        #print(self.parentclass.draggedpreset)
        if self.parentclass.draggedpreset and not self.draggedframe:
            mapped = self.graphicsview.mapToScene(event.pos())
            keyframe = Keyframe(int(mapped.x()),-round(mapped.y()/25),self.parentclass.draggedpreset.params.copy())
            self.parentclass.keyframes.add(keyframe)
            self.addKeyframe(keyframe)
        self.parentclass.draggedpreset = None
        event.accept()
        return super().dropEvent(event)
    
    def releaseEvent(self, event:QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if self.draggedframe:
                mapped = self.graphicsview.mapToScene(event.pos())

                self.parentclass.keyframes.setframe(self.draggedframe,int(mapped.x()))
                self.parentclass.keyframes.setlayer(self.draggedframe,-round(mapped.y()/25))

                self.keyframes[self.draggedframe].setPos(self.draggedframe.frame,-self.draggedframe.layer*25)
                self.draggedframe = None
                self.parentclass.updateviewport()
            #elif hasattr(founditem,"pressEvent"):
            #    founditem.pressEvent(event,self.graphicsview.mapToScene(event.pos().x(),0).toPoint())
        return super().mouseReleaseEvent(event)
    
        #return super().mouseReleaseEvent(event)
    
    def resizeEvent(self, event:QResizeEvent) -> None:
        self.scene.setSceneRect(self.rect())
        r = self.graphicsview.sceneRect()
        r.setSize(event.size()/self.graphicsview.transform().m11()+QSize(1000,1000))  #hacky workaround, if this wasnt here it would snap to 0,0 every time you shrinked the view by more than 1 pixel per frame
        self.graphicsview.setSceneRect(r)
        self.graphicsview.setFixedSize(event.size())
        self.graphicsview.size().setHeight(event.size().height())
        self.graphicsview.size().setWidth(event.size().width())
        #self.graphicsview.adjustSize()
        r = self.graphicsview.sceneRect()
        r.setSize(event.size()/self.graphicsview.transform().m11())
        self.graphicsview.setSceneRect(r)
        #print(r)
        #print(self.graphicsview.)
        super().resizeEvent(event)
        boundingrect = self.graphicsview.mapToScene(self.graphicsview.viewport().geometry()).boundingRect()
        self.playbackcursor.setLine(QLine(self.parentclass.playbackframe,boundingrect.top(),self.parentclass.playbackframe,boundingrect.bottom()))
    
    def addKeyframe(self,keyframe:Keyframe):
        #self.keyframes[keyframe] = self.scene.addRect(QRectF(-9,-9,18,18),QPen(QColor(0,0,0),0),self.coolgradient)
        #self.keyframes[keyframe].setRotation(45)
        #
        #self.keyframes[keyframe].setData(0,keyframe)
        self.keyframes[keyframe] = CzeTimelineKeyframeItem(keyframe)
        self.scene.addItem(self.keyframes[keyframe])
        self.keyframes[keyframe].setPos(keyframe.frame,-keyframe.layer*25)
        self.createKeyframeItem(keyframe,keyframe.params.image)
        for action in keyframe.params.states:
            self.createKeyframeItem(keyframe,action)
        for effect in keyframe.params.compositing:
            self.createKeyframeItem(keyframe,effect)
    
    def createKeyframeItem(self,keyframe:Keyframe,param:Params):
        if(keyframe is None):
            return
        if param.function and hasattr(param.function(),"timelineitem"):
            items = param.function().timelineitem(param,keyframe,self.parentclass)
            if(keyframe not in self.keyframeitems):
                self.keyframeitems[keyframe] = {}
                self.keyframeitems[keyframe][param] = []
            elif param not in self.keyframeitems[keyframe]:
                self.keyframeitems[keyframe][param] = []
            for item in items:
                self.keyframeitems[keyframe][param].append(item)
                self.scene.addItem(item)

    def deleteKeyframeItem(self,keyframe,param):
        if(keyframe is None):
            return
        if(keyframe in self.keyframeitems and param in self.keyframeitems[keyframe]):
            for item in self.keyframeitems[keyframe][param]:
                self.scene.removeItem(item)
            del self.keyframeitems[keyframe][param]

    def deleteKeyframeItems(self,keyframe):
        if(keyframe is None):
            return
        if(keyframe in self.keyframeitems):
            for param in self.keyframeitems[keyframe].keys():
                for item in self.keyframeitems[keyframe][param]:
                    self.scene.removeItem(item)
            del self.keyframeitems[keyframe]

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
        self.playbackcursor.setLine(QLine(self.parentclass.playbackframe,boundingrect.top(),self.parentclass.playbackframe,boundingrect.bottom()))

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.text() == "k":
            self.addKeyframe(self.parentclass.keyframes.create(self.parentclass.playbackframe))
        elif event.key() == Qt.Key.Key_Delete and not self.parentclass.rendering and not self.parentclass.seeking:
            if(self.parentclass.selectedframe == self.draggedframe):
                self.draggedframe = None
            self.deleteKeyframeItems(self.parentclass.selectedframe)
            self.scene.removeItem(self.keyframes[self.parentclass.selectedframe])
            self.parentclass.keyframes.remove(self.parentclass.selectedframe)
            del self.keyframes[self.parentclass.selectedframe]
            self.parentclass.selectedframe = None
            self.parentclass.regeneratekeyframeoptions()
            self.parentclass.viewport.updatehandles()
            self.parentclass.updateviewport()
            
        return super().keyPressEvent(event)


class CzePresetKeyframeItem(QGraphicsItem):
    coolgradient = QRadialGradient(50,50,90)
    coolgradient.setColorAt(1,QColor(255,255,255))
    coolgradient.setColorAt(0,QColor(255,0,0))
    selectedcoolgradient = QRadialGradient(30,30,60)
    selectedcoolgradient.setColorAt(1,QColor(255,127,127))
    selectedcoolgradient.setColorAt(0,QColor(255,0,0))
    selectedcoolgradientbackground = QRadialGradient(40,40,90)
    selectedcoolgradientbackground.setColorAt(1,QColor(255,127,127,63))
    selectedcoolgradientbackground.setColorAt(0,QColor(255,0,0,63))
    hoveredcoolgradientbackground = QRadialGradient(40,40,80)
    hoveredcoolgradientbackground.setColorAt(1,QColor(255,127,127,32))
    hoveredcoolgradientbackground.setColorAt(0,QColor(255,0,0,32))
    def __init__(self,keyframe):
        super().__init__()
        self.keyframe = keyframe
        self.name = keyframe.params.properties.params.name
        self.selected = False
        self.hovered = False

    def boundingRect(self):
        return QRectF(-30,-20,60,45)
    
    def setSelect(self,value):
        self.selected = value
    
    def setHovered(self,value):
        self.hovered = value

    def paint(self, painter: QPainter, option, widget) -> None:
        
        if(self.selected):
            painter.setBrush(self.selectedcoolgradientbackground)
            painter.setPen(QPen(QColor(255,192,192,64),0))
            painter.drawRect(-30,-20,60,45)
            painter.setBrush(self.selectedcoolgradient)
            painter.setPen(QPen(QColor(0,0,0),0))
            painter.drawPolygon([QPoint(10,0),QPoint(0,10),QPoint(-10,0),QPoint(0,-10)])
        elif(self.hovered):
            painter.setBrush(self.hoveredcoolgradientbackground)
            painter.setPen(QPen(QColor(255,192,192,32),0))
            painter.drawRect(-30,-20,60,45)
            painter.setBrush(self.coolgradient)
            painter.setPen(QPen(QColor(0,0,0),0))
            painter.drawPolygon([QPoint(10,0),QPoint(0,10),QPoint(-10,0),QPoint(0,-10)])
        else:
            painter.setBrush(self.coolgradient)
            painter.setPen(QPen(QColor(0,0,0),0))
            painter.drawPolygon([QPoint(10,0),QPoint(0,10),QPoint(-10,0),QPoint(0,-10)])
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(255,192,192,64),0))
        painter.drawRect(-20,-20,40,40)
        painter.setPen(QPen(QColor(255,192,192),0))
        painter.setFont(QFont("Arial",8))
        painter.drawText(QRectF(-30,21,60,35),self.name(),Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

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
        self.keyframes = [Keyframe(0,0,Params({
            "properties":{
                "params":{
                    "name":LineStringProperty("Image"),
                }
            },
            "image":
            {
                "function":Selectable(0,self.parentclass.imagefunctionsdropdown),
                "params":Selectable(0,self.parentclass.imagefunctionsdropdown)().params.copy()
            },
            "states":[
                {
                    "function":Selectable(0,self.parentclass.actionfunctionsdropdown),
                    "params":Selectable(0,self.parentclass.actionfunctionsdropdown)().params.copy()
                }
            ],
            "compositing":[
                {
                    "function":Selectable(0,self.parentclass.effectfunctionsdropdown),
                    "params":Selectable(0,self.parentclass.effectfunctionsdropdown)().params.copy().set("x",IntProperty(640)).set("y",IntProperty(360))
                },
                {
                    "function":Selectable(2,self.parentclass.effectfunctionsdropdown),
                    "params":Selectable(2,self.parentclass.effectfunctionsdropdown)().params.copy()
                }
            ]
        })),
        Keyframe(0,0,Params({
            "properties":{
                "params":{
                    "name":LineStringProperty("Video"),
                }
            },
            "image":
            {
                "function":Selectable(5,self.parentclass.imagefunctionsdropdown),
                "params":Selectable(5,self.parentclass.imagefunctionsdropdown)().params.copy()
            },
            "states":[
                {
                    "function":Selectable(0,self.parentclass.actionfunctionsdropdown),
                    "params":Selectable(0,self.parentclass.actionfunctionsdropdown)().params.copy()
                }
            ],
            "compositing":[
                {
                    "function":Selectable(0,self.parentclass.effectfunctionsdropdown),
                    "params":Selectable(0,self.parentclass.effectfunctionsdropdown)().params.copy().set("x",IntProperty(640)).set("y",IntProperty(360))
                },
                {
                    "function":Selectable(2,self.parentclass.effectfunctionsdropdown),
                    "params":Selectable(2,self.parentclass.effectfunctionsdropdown)().params.copy()
                }
            ]
        }))]
        self.drawnkeyframes = {}
        i = 0
        for keyframe in self.keyframes: # TODO : Maybe load from a file?
            self.drawnkeyframes[keyframe] = CzePresetKeyframeItem(keyframe)
            self.scene.addItem(self.drawnkeyframes[keyframe])
            self.drawnkeyframes[keyframe].setPos((i%6)*64+30,floor(i/6)*44+20)
            #self.drawnkeyframes[keyframe] = self.scene.addRect(QRectF(-9,-9,18,18),QPen(QColor(0,0,0),0),self.coolgradient)
            #self.drawnkeyframes[keyframe].setRotation(45)
            #self.drawnkeyframes[keyframe].setPos((i%6)*25,floor(i/6)*25)
            #self.drawnkeyframes[keyframe].setData(0,keyframe)
            i+=1
        self.graphicsview.onpress = self.pressEvent
        self.setAcceptDrops(True)
        self.graphicsview.setAcceptDrops(True)
        self.graphicsview.viewport().setAcceptDrops(True)
        self.graphicsview.dragenter = self.dragEnterEvent
        self.graphicsview.dragmove = self.dragMoveEvent
        self.graphicsview.dragdrop = self.dropEvent
        self.graphicsview.onmove = self.mmoveEvent
        self.selectedpreset = None
        self.hoveredpreset = None

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
            self.keyframes.append(keyframe)
            self.drawnkeyframes[keyframe] = CzePresetKeyframeItem(keyframe)
            self.scene.addItem(self.drawnkeyframes[keyframe])
            self.drawnkeyframes[keyframe].setPos((i%6)*64+30,floor(i/6)*44+20)
            #self.drawnkeyframes[keyframe] = self.scene.addRect(QRectF(-9,-9,18,18),QPen(QColor(0,0,0),0),self.coolgradient)
            #self.drawnkeyframes[keyframe].setRotation(45)
            #self.drawnkeyframes[keyframe].setPos((i%6)*25,floor(i/6)*25)
            #self.drawnkeyframes[keyframe].setData(0,keyframe)
            self.parentclass.draggedpreset = None
        event.accept()
    
    def pressEvent(self, event:QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            founditem:QGraphicsItem = self.graphicsview.itemAt(event.pos())
            if(self.selectedpreset):
                self.selectedpreset.setSelect(False)
            self.selectedpreset = founditem
            if(founditem):
                self.selectedpreset.setSelect(True)
                
                self.parentclass.timeline.deselectFrame()
                self.parentclass.keyframeoptions.regenerate(self.selectedpreset.keyframe)
                
            else:
                self.parentclass.keyframeoptions.regenerate()
            self.graphicsview.update()
            self.parentclass.draggedpreset = None
        return super().mousePressEvent(event)

    def mmoveEvent(self, event:QMouseEvent,prevpos:QPoint) -> None:
        if not self.parentclass.draggedpreset and self.selectedpreset and event.buttons() & Qt.MouseButton.LeftButton:
            self.parentclass.draggedpreset = self.selectedpreset.keyframe.copy()
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.exec_(Qt.MoveAction)
        founditem:QGraphicsItem = self.graphicsview.itemAt(event.pos())
        if founditem != self.hoveredpreset:
            if self.hoveredpreset:
                self.hoveredpreset.setHovered(False)
            if isinstance(founditem,CzePresetKeyframeItem):
                self.hoveredpreset = founditem
                self.hoveredpreset.setHovered(True)
            elif founditem is None:
                self.hoveredpreset = founditem
            self.graphicsview.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if(event.key() == Qt.Key.Key_Delete and self.selectedpreset):
            self.keyframes.pop(self.keyframes.index(self.selectedpreset.keyframe))
            self.drawnkeyframes[self.selectedpreset.keyframe] = None
            self.scene.removeItem(self.selectedpreset)
            self.selectedpreset = None

