import os

import numpy as np
import pyspng
import sounddevice
from moviepy.audio.io.AudioFileClip import AudioFileClip
from PIL import Image
from PySide6.QtCore import QFileInfo

from czeditor.avreader import PyAVSeekableVideoReader
from czeditor.generate import CreateXPWindow
from czeditor.graphics import *
from czeditor.properties import *
from czeditor.timelineitems import *
from czeditor.util import *

loadedimages = {}
emptyimage = Image.new("RGBA", (1, 1), (0, 0, 0, 0))

sourcefunctionsdropdown = []

class Source:
    def __init_subclass__(cls) -> None:
        sourcefunctionsdropdown.append(SelectableItem(cls.name, cls))


class NormalImage(Source):
    name = "Image"
    params = Params(
        {
            "imagepath": FileProperty("")
        }
    )

    def image(param: Params, parentclass, frame):
        path = param.imagepath()
        if (path in loadedimages):
            img = loadedimages[path]
            return img
        try:
            if (os.path.splitext(path)[1] == ".png"):
                with open(path, "rb") as file:
                    img = pyspng.load(file.read())
            else:
                img = np.array(Image.open(
                    QFileInfo(path).canonicalFilePath()).convert("RGBA"))
            loadedimages[path] = img
            if (len(loadedimages.keys()) > 300):
                del loadedimages[loadedimages.keys()[0]]

            return img
        except:
            return np.array([[[0, 0, 0, 0]]])

    def __str__(self):
        return self.name

    def gethashstring(self, param: Params, parentclass):
        return self.name+str(param)


class FilledRectangle(Source):
    name = "Filled Rectangle"
    params = Params(
        {
            "width": IntProperty(32),
            "height": IntProperty(32),
            "color": [192, 255, 192, 255]
        }
    )

    def image(param: Params, parentclass, frame):
        # return CreateFilledRectangle((param.width,param.height),tuple(param.color))
        made = np.full((param.height(), param.width(), 4),
                       np.array(param.color, dtype=np.uint8))
        return made

    def __str__(self):
        return self.name


class XPError(Source):
    name = "Windows XP Error"
    params = Params(
        {
            "text": StringProperty(""),
            "title": StringProperty(""),
            "buttons": StringList(["OK"]),
            "buttonstyles": emptylist(0),
            "erroricon": SelectableProperty([
                SelectableItem(
                    "Critical Error", "Wxp:Critical Error.png", "Wxp:Critical Error.png"),
                SelectableItem(
                    "Exclamation", "Wxp:Exclamation.png", "Wxp:Exclamation.png"),
                SelectableItem(
                    "Information", "Wxp:Information.png", "Wxp:Information.png"),
                SelectableItem("Question", "Wxp:Question.png",
                               "Wxp:Question.png"),
                SelectableItem("None", "")]),
            "transient": TransientProperty(Params({
                "cached": None,
                "lastParams": None
            }))
        }
    )

    def image(param: Params, parentclass, frame):
        # fillindefaults(param,{"text":"","title":"","buttons":[],"buttonstyles":emptylist(0),"erroricon":Selectable(1,[["Critical Error","xp/Critical Error.png"],["Exclamation","xp/Exclamation.png"],["Information","xp/Information.png"],["Question","xp/Question.png"],["None",""]])})
        transient = param.transient()
        if (transient.lastParams != str(param)):
            transient.cached = np.array(CreateXPWindow(param))
            transient.lastParams = str(param)
        return transient.cached

    def __str__(self):
        return self.name


"""class SoundFile():
    name = "Sound"
    params = Params(
        {
            "path": ""
        }
    )

    def __str__(self):
        return self.name"""


class ImageSequence(Source):
    name = "Image Sequence"
    params = Params({
        "imagespath": FileProperty("")
    })

    def image(param: Params, parentclass, frame):
        # return Image.open(param.imagespath.replace("*",str(int(parentclass.playbackframe))))
        with open(param.imagespath().replace("*", str(int(frame))), "rb") as file:
            img = pyspng.load(file.read())
        return img

    def __str__(self):
        return self.name


class Video(Source):
    name = "Video"
    params = Params({
        "videopath": FileProperty("", "Video Files (*.mp4 *.mov *.mkv *.avi *.webm)"),
        "startframe": IntProperty(0),
        "duration": IntProperty(0),
        "transient": TransientProperty(Params({
            "pyavobject": None,
            "moviepyobject": None,
            "decodedaudio": None,
            "maxduration": 0,
            "entirevideo": None,
            "lastpath": "",
            "handleHeight": 0}))
    })
    """
    Return the current frame the cursor is on in a video file
    """

    def image(param: Params, parentclass, frame):
        # return Image.open(param.imagespath.replace("*",str(int(parentclass.playbackframe))))
        transient = param.transient()
        if (not os.path.exists(param.videopath())):
            param.duration.set(0)
            return np.array(emptyimage)
        if (param.videopath() != transient.lastpath or transient.pyavobject == None):
            if (transient.pyavobject != None):
                transient.pyavobject.close()
                transient.moviepyobject.close()

            # transient.pyavobject = PyAVReaderTimed(param.videopath(),cache_size=32)
            transient.pyavobject = PyAVSeekableVideoReader(
                param.videopath())
            transient.moviepyobject = AudioFileClip(
                param.videopath(), nbytes=2, fps=48000)
            transient.lastpath = param.videopath()
            param.duration.set(int(
                len(transient.pyavobject)/transient.pyavobject.frame_rate*60)-param.startframe())
            transient.maxduration = int(
                len(transient.pyavobject)/transient.pyavobject.frame_rate*60)
            print(transient.maxduration)
        # Add the beginning frame offset
        frame += param.startframe()

        # Correct the framerate from 60 fps to video fps
        frame = int(frame/60*transient.pyavobject.frame_rate)
        if (frame >= len(transient.pyavobject) or frame < 0):  # Check if its after or before
            return np.array(emptyimage)
        img = transient.pyavobject[int(frame)]
        return img

    def sound(param: Params, sample):
        transient = param.transient()
        if (not os.path.exists(param.videopath())):
            return np.array((0)), 1
        if (param.videopath() != transient.lastpath or transient.moviepyobject == None):
            if (transient.moviepyobject != None):
                transient.pyavobject.close()
                transient.moviepyobject.close()

            transient.pyavobject = PyAVSeekableVideoReader(
                param.videopath())
            transient.moviepyobject = AudioFileClip(
                param.videopath(), nbytes=2, fps=48000)
            transient.lastpath = param.videopath()
            param.duration.set(int(
                len(transient.pyavobject)/transient.pyavobject.frame_rate*60)-param.startframe())
            transient.maxduration = int(
                len(transient.pyavobject)/transient.pyavobject.frame_rate*60)

        sample += int(param.startframe()/60*transient.moviepyobject.fps)
        if transient.moviepyobject.reader.pos != sample:
            transient.moviepyobject.reader.seek(sample)
            transient.moviepyobject.reader.pos = sample
        chunk = transient.moviepyobject.reader.read_chunk(512)
        return chunk, transient.moviepyobject.fps

    def timelineitem(param: Params, keyframe, windowClass):
        return [TimelineDurationLineItem(param, windowClass, keyframe), TimelineDurationHandleItem(param, windowClass, keyframe), TimelineStartFrameHandleItem(param, windowClass, keyframe), TimelineVerticalLineItem(param, windowClass, keyframe)]

    def seek(params: Params, frame):
        if (frame < params.transient().maxduration):
            params.transient().pyavobject[int(
                max(params.startframe(), frame)/60*params.transient().pyavobject.frame_rate)]
            params.transient().moviepyobject.reader.seek(
                int(max(params.startframe(), frame)/60*params.transient().moviepyobject.fps))

    def initialize(param: Params):
        transient = param.transient()
        if (param.videopath() != transient.lastpath or transient.moviepyobject == None):
            if (transient.moviepyobject != None):
                transient.pyavobject.close()
                transient.moviepyobject.close()
            transient.pyavobject = PyAVSeekableVideoReader(
                param.videopath())
            transient.moviepyobject = AudioFileClip(
                param.videopath(), nbytes=2, fps=48000)
            transient.lastpath = param.videopath()
            param.duration.set(int(
                len(transient.pyavobject)/transient.pyavobject.frame_rate*60)-param.startframe())
            transient.maxduration = int(
                len(transient.pyavobject)/transient.pyavobject.frame_rate*60)
        # print(chunk)
        # print(sample,secrets.moviepyobject.reader.pos,secrets.moviepyobject.reader.nframes)

        # print(secrets.avobject.streams.audio[0].duration)
        # print(frame/60/secrets.avobject.streams.audio[0].time_base)
        # secrets.avobject.seek(int(frame/60/secrets.avobject.streams.audio[0].time_base),any_frame=True)
        # buffer = np.array([])
        # first = True
        # for audioframe in secrets.avobject.decode(secrets.avobject.streams.audio[0]):
            # print(frame.to_ndarray())
            # print(float(audioframe.pts*secrets.avobject.streams.audio[0].time_base))
            # if first:
            #    buffer = np.append(buffer,audioframe.to_ndarray()[0])
            #    first = False
            # if(audioframe.pts*secrets.avobject.streams.audio[0].time_base < (frame+1)/60):
            #    buffer = np.append(buffer,audioframe.to_ndarray()[0])
            # else:
            # return audioframe.to_ndarray()[0],secrets.avobject.streams.audio[0]

    def __str__(self):
        return self.name


class Record(Source):
    name = "Record"
    params = Params({
        "transient": TransientProperty(Params({
            "sounddevice": None
        }
        ))
    })

    def sound(param: Params, sample):
        transient = param.transient()
        if transient.sounddevice is None:
            transient.sounddevice = sounddevice.rec(512, 48000, 1)
        sounddevice.wait()
        samples = transient.sounddevice
        transient.sounddevice = sounddevice.rec(512, 48000, 1)
        return samples, 48000

    def __str__(self):
        return self.name



