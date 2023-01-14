from PIL import Image
from util import ParamLink,Params
from handles import CzeViewportDraggableHandle
from PySide6.QtCore import QUrl
from PySide6.QtGui import QOpenGLContext
from OpenGL.GL import *
from time import time
import numpy as np
from math import *
from ctypes import c_void_p
from random import random
from scipy.spatial.transform import Rotation
imagecache = {}
"""def cachecomposite(func,parentclass,width,height):
    global imagecache
    strparam = func.function().gethashstring(func.function(),func.params,parentclass)
    if strparam not in imagecache:
        imagecache[strparam] = func.function().image(func.params,parentclass).resize((width,height))
    return imagecache[strparam]"""

class ImageComposite():
    name = "Normal Media"
    params = Params({
        "x":0,
        "y":0,
        "width":1280,
        "height":720,
        "relativewidth":100,
        "relativeheight":100
    })
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
    params = Params({
        "x":0,
        "y":0,
        "z":0,
        "width":1280,
        "height":720,
        "Xrotation":0,
        "Yrotation":0,
        "Zrotation":0,
        "relativewidth":100,
        "relativeheight":100,
        "textureid":0,
        "vbo":0,
        "vao":0,
        "pbo":0,
        "lastsize":(32,32)
    })
    
    def composite(imageparam,params,parentclass,keyframe):
        img,size = imageparam.function().image(imageparam.params,parentclass)
        imgdata = img.flatten()
        """vertexes = np.array([
             params.params.x-1280/2,  params.params.y-720/2, sin(parentclass.playbackframe/10)/20, 0.0, 0.0,
             params.params.width+params.params.x-1280/2,  params.params.y-720/2, sin(parentclass.playbackframe/11.9)/20, 1.0, 0.0,
             params.params.width+params.params.x-1280/2,  params.params.height+params.params.y-720/2, cos(parentclass.playbackframe/12.5)/20, 1.0, 1.0,
             params.params.x-1280/2,  params.params.y-720/2, sin(parentclass.playbackframe/10)/20, 0.0, 0.0,
             params.params.x-1280/2,  params.params.height+params.params.y-720/2, cos(parentclass.playbackframe/13.1)/20, 0.0, 1.0,
             params.params.width+params.params.x-1280/2,  params.params.height+params.params.y-720/2, cos(parentclass.playbackframe/12.5)/20, 1.0, 1.0],dtype=np.float32)"""
        """def r():
            return (random()-0.5)/64
        topleftx = r()
        toplefty = r()
        topleftz = r()
        bottomrightx = r()
        bottomrighty = r()
        bottomrightz = r()
        vertexes = np.array([
             params.params.x-1280/2+topleftx,  params.params.y-720/2+toplefty, topleftz, 0.0, 0.0,
             params.params.width+params.params.x-1280/2+r(),  params.params.y-720/2+r(), r(), 1.0, 0.0,
             params.params.width+params.params.x-1280/2+bottomrightx,  params.params.height+params.params.y-720/2+bottomrighty, bottomrightz, 1.0, 1.0,
             params.params.x-1280/2+topleftx,  params.params.y-720/2+toplefty, topleftz, 0.0, 0.0,
             params.params.x-1280/2+r(),  params.params.height+params.params.y-720/2+r(), r(), 0.0, 1.0,
             params.params.width+params.params.x-1280/2+bottomrightx,  params.params.height+params.params.y-720/2+bottomrighty, bottomrightz, 1.0, 1.0],dtype=np.float32)"""
        positions = np.array([[-params.params.width/2,-params.params.height/2,0.0],
        [params.params.width/2,  -params.params.height/2, 0.0],
        [params.params.width/2,  params.params.height/2, 0.0],
        [-params.params.width/2,  -params.params.height/2, 0.0],
        [-params.params.width/2,  params.params.height/2, 0.0],
        [params.params.width/2,  params.params.height/2, 0.0]])
        positions = Rotation.from_euler("xyz",(params.params.Xrotation,params.params.Yrotation,params.params.Zrotation),True).apply(positions)
        #print(positions)
        vertexes = np.array([
             positions[0][0]-1280/2+params.params.x,  positions[0][1]-720/2+params.params.y, positions[0][2]+params.params.z, 0.0, 0.0,
             positions[1][0]-1280/2+params.params.x,  positions[1][1]-720/2+params.params.y, positions[1][2]+params.params.z, 1.0, 0.0,
             positions[2][0]-1280/2+params.params.x,  positions[2][1]-720/2+params.params.y, positions[2][2]+params.params.z, 1.0, 1.0,
             positions[3][0]-1280/2+params.params.x,  positions[3][1]-720/2+params.params.y, positions[3][2]+params.params.z, 0.0, 0.0,
             positions[4][0]-1280/2+params.params.x,  positions[4][1]-720/2+params.params.y, positions[4][2]+params.params.z, 0.0, 1.0,
             positions[5][0]-1280/2+params.params.x,  positions[5][1]-720/2+params.params.y, positions[5][2]+params.params.z, 1.0, 1.0],dtype=np.float32)
        if(not params.params.vao):
            #Create a pbo
            params.params.width = size[0]
            params.params.height = size[1]
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
            glBufferData(GL_ARRAY_BUFFER,vertexes,GL_DYNAMIC_DRAW)
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,20,c_void_p(0))
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1,2,GL_FLOAT,GL_FALSE,20,c_void_p(12))
            glBindBuffer(GL_ARRAY_BUFFER,0)
            glBindVertexArray(0)
            params.params.lastsize = size
        elif params.params.lastsize[0] != size[0] or params.params.lastsize[1] != size[1]:
            params.params.width = size[0]
            params.params.height = size[1]
            glBindTexture(GL_TEXTURE_2D,0)
            #Delete the buffer
            glDeleteBuffers(1,[params.params.pbo])

            #Make a new buffer
            params.params.pbo = glGenBuffers(1)
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
            params.params.lastsize = size
        else:
            #print(glIsTexture(params.params.textureid))
            glBindBuffer(GL_ARRAY_BUFFER,params.params.vbo)
            #Set geometry of the quad
            glBufferData(GL_ARRAY_BUFFER,np.array(vertexes,dtype=np.float32),GL_DYNAMIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER,0)
            glBindBuffer(GL_PIXEL_UNPACK_BUFFER, params.params.pbo)
            glBufferData(GL_PIXEL_UNPACK_BUFFER, size[0]*size[1]*4,None, GL_STREAM_DRAW)
            glBindTexture(GL_TEXTURE_2D,params.params.textureid)
            data = glMapBuffer(GL_PIXEL_UNPACK_BUFFER,GL_WRITE_ONLY)
            array = (GLubyte*size[0]*size[1]*4).from_address(data)
            ctypes.memmove(array,imgdata.ctypes.data,size[0]*size[1]*4)
            glUnmapBuffer(GL_PIXEL_UNPACK_BUFFER)
            glTexSubImage2D(GL_TEXTURE_2D,0,0,0,size[0],size[1],GL_RGBA,GL_UNSIGNED_BYTE,c_void_p(0))
            #glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,size[0],size[1],0,GL_RGBA,GL_UNSIGNED_BYTE,c_void_p(0))
            
            glBindBuffer(GL_PIXEL_UNPACK_BUFFER, 0)
            #Draw the quad
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
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