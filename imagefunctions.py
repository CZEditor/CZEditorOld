from PIL import Image
from util import *
from generate import CreateXPWindow
from graphics import *
#import ffmpeg
from PySide6.QtCore import QByteArray,QBuffer,QIODevice
import pyspng
import pims
import numpy as np
from properties import *
import os
from moviepy.editor import AudioFileClip
from timelineitems import *
loadedimages = {}
class NormalImage():
    name = "Image"
    params = Params(
        {
            "imagepath":FileProperty("")
        }
    )
    def image(param:Params,parentclass,frame):
        path = param.imagepath()
        if(path in loadedimages):
            img = loadedimages[path]
            return img,(img.shape[1],img.shape[0])
        try:
            with open(path,"rb") as file:
                img = pyspng.load(file.read())
            loadedimages[path] = img
            if(len(loadedimages.keys()) > 300):
                del loadedimages[loadedimages.keys()[0]]

            return img,(img.shape[1],img.shape[0])
        except:
            return np.array([[[0,0,0,0]]]),(1,1)
    def __str__(self):
        return self.name
    def gethashstring(self,param:Params,parentclass):
        return self.name+str(param)
class FilledRectangle():
    name = "Filled Rectangle"
    params = Params(
        {
            "width":IntProperty(32),
            "height":IntProperty(32),
            "color":[192,255,192,255]
        }
    )
    def image(param:Params,parentclass,frame):
        #return CreateFilledRectangle((param.width,param.height),tuple(param.color))
        made = np.full((param.width(),param.height(),4),np.array(param.color,dtype=np.uint8))
        return made,(param.width(),param.height())
    def __str__(self):
        return self.name
class XPError():
    name = "Windows XP Error"
    params = Params(
        {
            "text":"",
            "title":"",
            "buttons":StringList([]),
            "buttonstyles":emptylist(0),
            "erroricon":Selectable(1,[
                ["Critical Error","xp/Critical Error.png"],
                ["Exclamation","xp/Exclamation.png"],
                ["Information","xp/Information.png"],
                ["Question","xp/Question.png"],
                ["None",""]])
        }
    )
    def image(param:Params,parentclass,frame):
        #fillindefaults(param,{"text":"","title":"","buttons":[],"buttonstyles":emptylist(0),"erroricon":Selectable(1,[["Critical Error","xp/Critical Error.png"],["Exclamation","xp/Exclamation.png"],["Information","xp/Information.png"],["Question","xp/Question.png"],["None",""]])})
        generated = CreateXPWindow(param)
        return np.array(generated),generated.size
    def __str__(self):
        return self.name
class SoundFile():
    name = "Sound"
    params = Params(
        {
            "path":""
        }
    )
    def image(param:Params,parentclass,frame):
        return np.array(emptyimage),(1,1)
    def __str__(self):
        return self.name
class ImageSequence():
    name = "Image Sequence"
    params = Params({
        "imagespath":FileProperty("")
    })
    def image(param:Params,parentclass,frame):
        #return Image.open(param.imagespath.replace("*",str(int(parentclass.playbackframe))))
        with open(param.imagespath().replace("*",str(int(frame))),"rb") as file:
            img = pyspng.load(file.read())
        return img,(img.shape[1],img.shape[0])
    def __str__(self):
        return self.name
class Video():
    name = "Video"
    params = Params({
        "videopath":FileProperty(""),
        "startframe":IntProperty(0),
        "duration":IntProperty(0),
        "secrets":SecretProperty(Params({
            "pimsobject":None,
            "moviepyobject":None,
            "decodedaudio":None,
            "maxduration":0,
            "lastpath":""}))
    })
    def image(param:Params,parentclass,frame):
        #return Image.open(param.imagespath.replace("*",str(int(parentclass.playbackframe))))
        secrets = param.secrets()
        if(not os.path.exists(param.videopath())):
            param.duration.set(0)
            return np.array(emptyimage),(1,1)
        if(param.videopath() != secrets.lastpath or secrets.pimsobject == None):
            if(secrets.pimsobject != None):
                secrets.pimsobject.close()
                secrets.moviepyobject.close()
            secrets.pimsobject = pims.PyAVVideoReader(param.videopath())
            secrets.moviepyobject = AudioFileClip(param.videopath(),nbytes=2,fps=48000)
            secrets.lastpath = param.videopath()
            param.duration.set(int(len(secrets.pimsobject)/secrets.pimsobject.frame_rate*60)-param.startframe())
            secrets.maxduration = int(len(secrets.pimsobject)/secrets.pimsobject.frame_rate*60)
            #print(len(secrets.pimsobject)/secrets.pimsobject.frame_rate*60)
        frame += param.startframe()
        frame = int(frame/60*secrets.pimsobject.frame_rate)
        if(frame >= len(secrets.pimsobject) or frame < 0):
            return np.array(emptyimage),(1,1)
        img = secrets.pimsobject[int(frame)]
        img = np.pad(img,((0,0),(0,0),(0,1)),mode="constant",constant_values=255) # TODO : Maybe support alpha videos?
        return img,(img.shape[1],img.shape[0])
    def sound(param:Params,sample):
        secrets = param.secrets()
        if(not os.path.exists(param.videopath())):
            return np.array((0)),1
        if(param.videopath() != secrets.lastpath or secrets.moviepyobject == None):
            if(secrets.moviepyobject != None):
                secrets.pimsobject.close()
                secrets.moviepyobject.close()
            secrets.pimsobject = pims.PyAVVideoReader(param.videopath())
            secrets.moviepyobject = AudioFileClip(param.videopath(),nbytes=2,fps=48000)
            secrets.lastpath = param.videopath()
            param.duration.set(int(len(secrets.pimsobject)/secrets.pimsobject.frame_rate*60)-param.startframe())
            secrets.maxduration = int(len(secrets.pimsobject)/secrets.pimsobject.frame_rate*60)
            #print(len(secrets.pimsobject)/secrets.pimsobject.frame_rate*60)
        sample += int(param.startframe()/60*secrets.moviepyobject.fps)
        if secrets.moviepyobject.reader.pos != sample:
            secrets.moviepyobject.reader.seek(sample)
            secrets.moviepyobject.reader.pos = sample
        chunk = secrets.moviepyobject.reader.read_chunk(1024)
        return chunk,secrets.moviepyobject.fps
    def timelineitem(param:Params,keyframe,windowClass):
        return [TimelineDurationLineItem(param,windowClass,keyframe),TimelineDurationHandleItem(param,windowClass,keyframe),TimelineStartFrameHandleItem(param,windowClass,keyframe)]
        #print(chunk)
        #print(sample,secrets.moviepyobject.reader.pos,secrets.moviepyobject.reader.nframes)
        
        #print(secrets.avobject.streams.audio[0].duration)
        #print(frame/60/secrets.avobject.streams.audio[0].time_base)
        #secrets.avobject.seek(int(frame/60/secrets.avobject.streams.audio[0].time_base),any_frame=True)
        #buffer = np.array([])
        #first = True
        #for audioframe in secrets.avobject.decode(secrets.avobject.streams.audio[0]):
            #print(frame.to_ndarray())
            #print(float(audioframe.pts*secrets.avobject.streams.audio[0].time_base))
            #if first:
            #    buffer = np.append(buffer,audioframe.to_ndarray()[0])
            #    first = False
            #if(audioframe.pts*secrets.avobject.streams.audio[0].time_base < (frame+1)/60):
            #    buffer = np.append(buffer,audioframe.to_ndarray()[0])
            #else:
            #return audioframe.to_ndarray()[0],secrets.avobject.streams.audio[0]
        
    def __str__(self):
        return self.name
imagefunctionsdropdown = [["Image",NormalImage],["Windows XP Error",XPError],["Filled Rectangle",FilledRectangle],["Sound",SoundFile],["Image Sequence",ImageSequence],["Video",Video]]