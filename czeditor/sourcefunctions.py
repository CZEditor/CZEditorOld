import os

import numpy as np
import scipy.interpolate
import pyspng
import sounddevice
from moviepy.audio.io.AudioFileClip import AudioFileClip
from PIL import Image, ImageFont, ImageDraw
from PySide6.QtCore import QFileInfo, QRect
from PySide6.QtGui import QRawFont, QImage, QFontMetrics

from czeditor.avreader import PyAVSeekableVideoReader
from czeditor.generate import CreateXPWindow
from czeditor.graphics import *
from czeditor.properties import *
from czeditor.timelineitems import *
from czeditor.util import *
import czeditor.shared

import traceback
loadedimages = {}
emptyimage = Image.new("RGBA", (1, 1), (0, 0, 0, 0))


class Source:
    def __init_subclass__(cls) -> None:
        czeditor.shared.sourceFunctions[cls.__name__] = cls


class NormalImage(Source):
    name = "Image"
    params = Params(
        {
            "imagepath": FileProperty("")
        }
    )
    icon = "editor:sources/Image.png"

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
    icon = "editor:sources/Filled Rectangle.png"

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
    icon = "editor:sources/Windows Error.png"

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
    icon = "editor:sources/Image Sequence.png"


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
        "duration": IntProperty(-1),
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
    icon = "editor:sources/Video.png"
    def image(param: Params, parentclass, frame):
        # return Image.open(param.imagespath.replace("*",str(int(parentclass.playbackframe))))
        transient = param.transient()
        if (not os.path.exists(param.videopath())):
            param.duration.set(-1)
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
            if param.duration() == -1:
                param.duration.set(int(
                    len(transient.pyavobject)/transient.pyavobject.frame_rate*60)-param.startframe())
            transient.maxduration = int(
                len(transient.pyavobject)/transient.pyavobject.frame_rate*60)
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

    def timelineitem(params: Params, keyframe, windowClass):
        # return [TimelineDurationLineItem(param, windowClass, keyframe), TimelineDurationHandleItem(param, windowClass, keyframe), TimelineStartFrameHandleItem(param, windowClass, keyframe), TimelineVerticalLineItem(param, windowClass, keyframe)]
        return [TimelineDurationItem(params, keyframe)]

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
            if param.duration() == -1:
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

    def updateParams(params):
        transient = params.transient()
        if (not os.path.exists(params.videopath())):
            params.duration.set(-1)
            return
        if (params.videopath() != transient.lastpath or transient.moviepyobject == None):
            if (transient.moviepyobject != None):
                transient.pyavobject.close()
                transient.moviepyobject.close()
            transient.pyavobject = PyAVSeekableVideoReader(
                params.videopath())
            transient.moviepyobject = AudioFileClip(
                params.videopath(), nbytes=2, fps=48000)
            transient.lastpath = params.videopath()
            if params.duration() == -1:
                params.duration.set(int(
                    len(transient.pyavobject)/transient.pyavobject.frame_rate*60)-params.startframe())
            transient.maxduration = int(
                len(transient.pyavobject)/transient.pyavobject.frame_rate*60)

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
    icon = "editor:sources/Record.png"
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


class RadialGradient(Source):
    name = "Radial Gradient"
    params = Params({
        "width": IntProperty(100),
        "height": IntProperty(100),
        "Xcenter": FloatProperty(50.0),
        "Ycenter": FloatProperty(50.0),
        "radius": FloatProperty(100.0),
        "color_inner": RGBProperty(255, 0, 0, 255),
        "color_outer": RGBProperty(0, 0, 0, 255)
    })
    icon = "editor:Rounded Frame.png"

    def image(params:Params, windowObject, frame):
        x = np.arange(params.width())
        y = np.arange(params.height())
        xx, yy = np.meshgrid(x, y)
        dist = np.hypot(xx - params.Xcenter(frame), yy - params.Ycenter(frame))
        radius = [0,params.radius(frame)]
        i_r,i_g,i_b,i_a = params.color_inner()
        o_r,o_g,o_b,o_a = params.color_outer()
        f_r = scipy.interpolate.interp1d(radius,[i_r,o_r], bounds_error = False, fill_value=(i_r,o_r))
        f_g = scipy.interpolate.interp1d(radius,[i_g,o_g], bounds_error = False, fill_value=(i_g,o_g))
        f_b = scipy.interpolate.interp1d(radius,[i_b,o_b], bounds_error = False, fill_value=(i_b,o_b))
        f_a = scipy.interpolate.interp1d(radius,[i_a,o_a], bounds_error = False, fill_value=(i_a,o_a))
        r = f_r(dist).astype(np.uint8)
        g = f_g(dist).astype(np.uint8)
        b = f_b(dist).astype(np.uint8)
        a = f_a(dist).astype(np.uint8)
        return np.dstack((r,g,b,a))


class Text(Source):
    name = "Text"
    params = Params({
        "text": StringProperty(""),
        "font": FontProperty("Trebuchet MS"),
        "size": IntProperty(8),
        "color": RGBProperty(255, 255, 255),
        "transient": TransientProperty(Params({
            "QPainter": None,
            "QImage": None
        }))
    })
    icon = "editor:Text.png"

    def image(params: Params, windowObject, frame):
        transient = params.transient()
        transient.QImage.fill(QColor(0,0,0,0))
        transient.QPainter.begin(transient.QImage)
        transient.QPainter.setPen(QColor(*params.color()))
        font = params.font()
        font.setPointSize(params.size())
        transient.QPainter.setFont(font)
        

        transient.QPainter.drawText(transient.QImage.rect(), Qt.AlignmentFlag.AlignCenter, params.text())
        transient.QPainter.end()

        ptr = transient.QImage.constBits()
        return np.frombuffer(ptr, np.uint8).reshape((transient.QImage.height(), transient.QImage.width(), 4))
    def initialize(params: Params):
        transient = params.transient()
        transient.QImage = QImage(1,1,QImage.Format.Format_RGBA8888)
        transient.QImage.fill(QColor(0,0,0,0))
        transient.QPainter = QPainter()

    def updateParams(params):
        transient = params.transient()
        font = params.font()
        font.setPointSize(params.size())
        rect = QFontMetrics(font).boundingRect(QRect(0,0,10000,10000),Qt.AlignmentFlag.AlignCenter,params.text())
        transient.QImage = QImage(max(1,rect.width()), max(1,rect.height()),QImage.Format.Format_RGBA8888)
        transient.QImage.fill(QColor(0,0,0,0))