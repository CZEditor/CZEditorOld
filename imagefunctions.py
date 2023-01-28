from PIL import Image
from util import *
from generate import CreateXPWindow
from graphics import *
#import ffmpeg
from PySide6.QtCore import QByteArray,QBuffer,QIODevice
import pyspng
from pims import PyAVReaderTimed
import numpy as np
from properties import *
import os
from moviepy.audio.io.AudioFileClip import AudioFileClip
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
            return img
        try:
            if(os.path.splitext(path)[1] == ".png"):
                with open(path,"rb") as file:
                    img = pyspng.load(file.read())
            else:
                img = np.array(Image.open(path).convert("RGBA"))
            loadedimages[path] = img
            if(len(loadedimages.keys()) > 300):
                del loadedimages[loadedimages.keys()[0]]

            return img
        except:
            return np.array([[[0,0,0,0]]])

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
        made = np.full((param.height(),param.width(),4),np.array(param.color,dtype=np.uint8))
        return made

    def __str__(self):
        return self.name


class XPError():
    name = "Windows XP Error"
    params = Params(
        {
            "text":StringProperty(""),
            "title":StringProperty(""),
            "buttons":StringList(["OK"]),
            "buttonstyles":emptylist(0),
            "erroricon":Selectable(0,[
                ["Critical Error","xp/Critical Error.png"],
                ["Exclamation","xp/Exclamation.png"],
                ["Information","xp/Information.png"],
                ["Question","xp/Question.png"],
                ["None",""]]),
            "transient":TransientProperty(Params({
                "cached":None,
                "lastParams":None
            }))
        }
    )

    def image(param:Params,parentclass,frame):
        #fillindefaults(param,{"text":"","title":"","buttons":[],"buttonstyles":emptylist(0),"erroricon":Selectable(1,[["Critical Error","xp/Critical Error.png"],["Exclamation","xp/Exclamation.png"],["Information","xp/Information.png"],["Question","xp/Question.png"],["None",""]])})
        transient = param.transient()
        if(transient.lastParams != str(param)):
            transient.cached = np.array(CreateXPWindow(param))
            transient.lastParams = str(param)
        return transient.cached

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
        return np.array(emptyimage)

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
        return img

    def __str__(self):
        return self.name


class Video():
    name = "Video"
    params = Params({
        "videopath":FileProperty(""),
        "startframe":IntProperty(0),
        "duration":IntProperty(0),
        "transient":TransientProperty(Params({
            "pimsobject":None,
            "moviepyobject":None,
            "decodedaudio":None,
            "maxduration":0,
            "entirevideo":None,
            "lastpath":"",
            "handleHeight":0}))
    })
    """
    Return the current frame the cursor is on in a video file
    """
    
    def image(param:Params,parentclass,frame):
        #return Image.open(param.imagespath.replace("*",str(int(parentclass.playbackframe))))
        transient = param.transient()
        if(not os.path.exists(param.videopath())):
            param.duration.set(0)
            return np.array(emptyimage)
        if(param.videopath() != transient.lastpath or transient.pimsobject == None):
            if(transient.pimsobject != None):
                transient.pimsobject.close()
                transient.moviepyobject.close()
            transient.pimsobject = PyAVReaderTimed(param.videopath(),cache_size=32)
            transient.moviepyobject = AudioFileClip(param.videopath(),nbytes=2,fps=48000)
            transient.lastpath = param.videopath()
            param.duration.set(int(len(transient.pimsobject)/transient.pimsobject.frame_rate*60)-param.startframe())
            transient.maxduration = int(len(transient.pimsobject)/transient.pimsobject.frame_rate*60)

        # Add the beginning frame offset
        frame += param.startframe()

        # Correct the framerate from 60 fps to video fps
        frame = int(frame/60*transient.pimsobject.frame_rate)
        if(frame >= len(transient.pimsobject) or frame < 0): #Check if its after or before
            return np.array(emptyimage)
        img = transient.pimsobject[int(frame)]
        img = np.pad(img,((0,0),(0,0),(0,1)),mode="constant",constant_values=255) # Add alpha 255, TODO : Maybe support alpha videos?
        return img

    def sound(param:Params,sample):
        transient = param.transient()
        if(not os.path.exists(param.videopath())):
            return np.array((0)),1
        if(param.videopath() != transient.lastpath or transient.moviepyobject == None):
            if(transient.moviepyobject != None):
                transient.pimsobject.close()
                transient.moviepyobject.close()
            transient.pimsobject = PyAVReaderTimed(param.videopath(),cache_size=32)
            transient.moviepyobject = AudioFileClip(param.videopath(),nbytes=2,fps=48000)
            transient.lastpath = param.videopath()
            param.duration.set(int(len(transient.pimsobject)/transient.pimsobject.frame_rate*60)-param.startframe())
            transient.maxduration = int(len(transient.pimsobject)/transient.pimsobject.frame_rate*60)
        sample += int(param.startframe()/60*transient.moviepyobject.fps)
        if transient.moviepyobject.reader.pos != sample:
            transient.moviepyobject.reader.seek(sample)
            transient.moviepyobject.reader.pos = sample
        chunk = transient.moviepyobject.reader.read_chunk(1024)
        return chunk,transient.moviepyobject.fps

    def timelineitem(param:Params,keyframe,windowClass):
        return [TimelineDurationLineItem(param,windowClass,keyframe),TimelineDurationHandleItem(param,windowClass,keyframe),TimelineStartFrameHandleItem(param,windowClass,keyframe),TimelineVerticalLineItem(param,windowClass,keyframe)]

    def seek(params:Params,frame):
        if(frame<params.transient().maxduration):
            params.transient().pimsobject[int(max(params.startframe(),frame)/60*params.transient().pimsobject.frame_rate)]
            params.transient().moviepyobject.reader.seek(int(max(params.startframe(),frame)/60*params.transient().moviepyobject.fps))

    def initialize(param:Params):
        transient = param.transient()
        if(param.videopath() != transient.lastpath or transient.moviepyobject == None):
            if(transient.moviepyobject != None):
                transient.pimsobject.close()
                transient.moviepyobject.close()
            transient.pimsobject = PyAVReaderTimed(param.videopath(),cache_size=32)
            transient.moviepyobject = AudioFileClip(param.videopath(),nbytes=2,fps=48000)
            transient.lastpath = param.videopath()
            param.duration.set(int(len(transient.pimsobject)/transient.pimsobject.frame_rate*60)-param.startframe())
            transient.maxduration = int(len(transient.pimsobject)/transient.pimsobject.frame_rate*60)
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