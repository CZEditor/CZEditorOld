from PIL import Image
from util import ParamLink,Params
from handles import CzeViewportDraggableHandle
from PySide6.QtCore import QUrl
from PySide6.QtGui import QOpenGLContext
from OpenGL.GL import *
from time import time
import numpy as np
from ctypes import c_void_p
imagecache = {}
"""def cachecomposite(func,parentclass,width,height):
    global imagecache
    strparam = func.function().gethashstring(func.function(),func.params,parentclass)
    if strparam not in imagecache:
        imagecache[strparam] = func.function().image(func.params,parentclass).resize((width,height))
    return imagecache[strparam]"""

class ImageComposite():
    name = "Normal Media"
    params = {
        "x":0,
        "y":0,
        "width":1280,
        "height":720,
        "relativewidth":100,
        "relativeheight":100
    }
    def composite(canvas,imageparam,params,parentclass,keyframe):
        img = imageparam.function().image(imageparam.params,parentclass)
        params.params.width = int(img.size[0]*params.params.relativewidth/100) #put this in the onupdate function! make sure that it gets called only after the image has been updated
        params.params.height = int(img.size[1]*params.params.relativeheight/100)
        canvas.alpha_composite(img.resize((params.params.width,params.params.height),Image.Resampling.NEAREST),(params.params.x,params.params.y))
        return canvas
    def onupdate(self,imageparam,params,parentclass,keyframe):
        img = imageparam.function().image(imageparam.params,parentclass)
        params.params.width = int(img.size[0]*params.params.relativewidth/100)
        params.params.height = int(img.size[1]*params.params.relativeheight/100)
    def handle(keyframe,parentclass,params):
        return [CzeViewportDraggableHandle(None,parentclass,ParamLink(params.params,"x"),ParamLink(params.params,"y"))]
    def __str__(self):
        return self.name
class SoundFile():
    name = "Sound"
    params = Params({
        "volume":50,
        "lastplaying":False
    })
    def composite(canvas,imagefunction,params,parentclass,keyframe):
        if(not parentclass.isplaying):
            if(params.params.lastplaying):
                parentclass.player.pause()
            parentclass.player.setPosition(int(parentclass.playbackframe/60*1000))
            parentclass.player.setSource(QUrl.fromLocalFile(keyframe.imageparams.params.path))
            parentclass.audio_output.setVolume(float(params.params.volume))
            params.params.lastplaying = False
        elif(not params.params.lastplaying):
            parentclass.player.play()
            params.params.lastplaying = True
        return canvas
    def __str__(self):
        return self.name
class Unholy():
    name = "Unholy"
    params = {
        "x":0,
        "y":0,
        "width":1280,
        "height":720,
        "relativewidth":100,
        "relativeheight":100,
        "textureid":0,
        "vbo":0,
        "vao":0,
        "pbo":0,
        "lastsize":(32,32)
    }
    def composite(imageparam,params,parentclass,keyframe):
        img,size = imageparam.function().image(imageparam.params,parentclass)
        imgdata = np.array(img).flatten()
        if(not params.params.vao):
            #Create a pbo
            
            params.params.pbo = glGenBuffers(1)
            glBindBuffer(GL_PIXEL_UNPACK_BUFFER, params.params.pbo)
            glBufferData(GL_PIXEL_UNPACK_BUFFER, size[0]*size[1]*4,None, GL_STREAM_DRAW)
            data = glMapBuffer(GL_PIXEL_UNPACK_BUFFER,GL_WRITE_ONLY)
            array = (GLubyte*size[0]*size[1]*4).from_address(data)
            ctypes.memmove(array,imgdata.ctypes.data,size[0]*size[1]*4)
            glUnmapBuffer(GL_PIXEL_UNPACK_BUFFER)
            #Generate a texture
            params.params.textureid = glGenTextures(1)
            glPixelStorei(GL_UNPACK_ALIGNMENT,1)
            
            glBindTexture(GL_TEXTURE_2D,params.params.textureid)

            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_BORDER)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_BORDER)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_BASE_LEVEL,0)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAX_LEVEL,0)
            
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,size[0],size[1],0,GL_RGBA,GL_UNSIGNED_BYTE,c_void_p(0))
            glBindTexture(GL_TEXTURE_2D,0)
            glBindBuffer(GL_PIXEL_UNPACK_BUFFER, 0)
            #Generate a vertex array
            params.params.vao = glGenVertexArrays(1)
            glBindVertexArray(params.params.vao)
            #Generate a vertex buffer
            params.params.vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER,params.params.vbo)
            #Set geometry of the quad
            glBufferData(GL_ARRAY_BUFFER,np.array([
             0.0,  0.0, 0.0, 0.0,
             params.params.width,  0.0, 1.0, 0.0,
             params.params.width,  params.params.height, 1.0, 1.0,
             0.0,  0.0, 0.0, 0.0,
             0.0,  params.params.height, 0.0, 1.0,
             params.params.width,  params.params.height, 1.0, 1.0],dtype=np.float32),GL_DYNAMIC_DRAW)
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0,2,GL_FLOAT,GL_FALSE,16,c_void_p(0))
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1,2,GL_FLOAT,GL_FALSE,16,c_void_p(8))
            glBindBuffer(GL_ARRAY_BUFFER,0)
            glBindVertexArray(0)
            params.params.lastsize = size
        elif params.params.lastsize[0] != size[0] or params.params.lastsize[1] != size[1]:
            #print(size)
            glBindTexture(GL_TEXTURE_2D,0)
            #Delete the buffer and texture
            glDeleteBuffers(1,[params.params.pbo])
            #glDeleteTextures(1,[params.params.textureid])

            #Make a new buffer
            params.params.pbo = glGenBuffers(1)
            #glBindBuffer(GL_PIXEL_UNPACK_BUFFER, params.params.pbo)
            #glBufferData(GL_PIXEL_UNPACK_BUFFER, size[0]*size[1]*4,None, GL_STREAM_DRAW)
            #data = glMapBuffer(GL_PIXEL_UNPACK_BUFFER,GL_WRITE_ONLY)
            #array = (GLubyte*size[0]*size[1]*4).from_address(data)
            #ctypes.memmove(array,imgdata.ctypes.data,size[0]*size[1]*4)
            #glUnmapBuffer(GL_PIXEL_UNPACK_BUFFER)
            
            #Generate a new texture
            #print(params.params.textureid)
            #print("is valid: ",glIsTexture(params.params.textureid))
            #params.params.textureid = (GLuint * 1)()
            #glGenTextures(1,params.params.textureid)
            #print(params.params.textureid)
            #params.params.textureid = params.params.textureid[0]
            #print(params.params.textureid)
            glPixelStorei(GL_UNPACK_ALIGNMENT,1)
            
            #print("is valid: ",glIsTexture(params.params.textureid))
            glBindTexture(GL_TEXTURE_2D,params.params.textureid)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_BORDER)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_BORDER)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_BASE_LEVEL,0)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAX_LEVEL,0)
            
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,size[0],size[1],0,GL_RGBA,GL_UNSIGNED_BYTE,c_void_p(0))
            glBindTexture(GL_TEXTURE_2D,0)

            glBindBuffer(GL_PIXEL_UNPACK_BUFFER, 0)
            #print("is valid: ",glIsTexture(params.params.textureid))
            params.params.lastsize = size
        else:
            #print(glIsTexture(params.params.textureid))
            glBindBuffer(GL_ARRAY_BUFFER,params.params.vbo)
            #Set geometry of the quad
            glBufferData(GL_ARRAY_BUFFER,np.array([
                0.0,  0.0, 0.0, 1.0,
                params.params.width,  0.0, 1.0, 1.0,
                params.params.width,  params.params.height, 1.0, 0.0,
                0.0,  0.0, 0.0, 1.0,
                0.0,  params.params.height, 0.0, 0.0,
                params.params.width,  params.params.height, 1.0, 0.0],dtype=np.float32),GL_DYNAMIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER,0)
            glBindBuffer(GL_PIXEL_UNPACK_BUFFER, params.params.pbo)
            glBufferData(GL_PIXEL_UNPACK_BUFFER, size[0]*size[1]*4,None, GL_STREAM_DRAW)
            glBindTexture(GL_TEXTURE_2D,params.params.textureid)
            data = glMapBuffer(GL_PIXEL_UNPACK_BUFFER,GL_WRITE_ONLY)
            array = (GLubyte*size[0]*size[1]*4).from_address(data)
            ctypes.memmove(array,imgdata.ctypes.data,size[0]*size[1]*4)
            glUnmapBuffer(GL_PIXEL_UNPACK_BUFFER)
            #glTexSubImage2D(GL_TEXTURE_2D,0,0,0,size[0],size[1],GL_RGBA,GL_UNSIGNED_BYTE,c_void_p(0))
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,size[0],size[1],0,GL_RGBA,GL_UNSIGNED_BYTE,c_void_p(0))
            
            glBindBuffer(GL_PIXEL_UNPACK_BUFFER, 0)
            #Draw the quad
            glUniform1i(glGetUniformLocation(parentclass.viewport.videorenderer.shader,"image"),0)
            glActiveTexture(GL_TEXTURE0)
            glBindVertexArray(params.params.vao)
            glDrawArrays(GL_TRIANGLES,0,6)
            glBindVertexArray(0)
            glBindTexture(GL_TEXTURE_2D,0)
    def onupdate(self,imageparam,params,parentclass,keyframe):
        img = imageparam.function().image(imageparam.params,parentclass)
        params.params.width = int(img.size[0]*params.params.relativewidth/100)
        params.params.height = int(img.size[1]*params.params.relativeheight/100)
    def handle(keyframe,parentclass,params):
        return [CzeViewportDraggableHandle(None,parentclass,ParamLink(params.params,"x"),ParamLink(params.params,"y"))]
    def __str__(self):
        return self.name
compositingfunctionsdropdown = [["Sound",SoundFile],["Unholy",Unholy]]
#["Normal Media",ImageComposite],