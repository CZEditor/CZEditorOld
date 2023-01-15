from PIL import Image
from util import ParamLink,Params
from handles import CzeViewportDraggableHandle
from PySide6.QtCore import QUrl
from OpenGL.GL import *
from time import time
import numpy as np
from math import *
from ctypes import c_void_p
from random import random
from scipy.spatial.transform import Rotation
from properties import *
from openglfunctions import *
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
        "volume":IntProperty(50),
        "secrets":SecretProperty(Params({
            "lastplaying":False
        }))
    })
    def soundeffect(source,params,frame):
        return source
    def __str__(self):
        return self.name
class Unholy():
    name = "Unholy"
    params = Params({
        "x":IntProperty(0),
        "y":IntProperty(0),
        "z":IntProperty(0),
        "size":SizeProperty(1280,720,1280,720),
        "Xrotation":IntProperty(0),
        "Yrotation":IntProperty(0),
        "Zrotation":IntProperty(0),
        "relativewidth":IntProperty(100),
        "relativeheight":IntProperty(100),
        "secrets":SecretProperty(Params({
            "textureid":0,
            "vbo":0,
            "vao":0,
            "pbo":0,
            "lastsize":(32,32)
        }))
    })
    
    def composite(imageparam,params,parentclass,keyframe,frame):
        width,height = params.params.size()
        img,size = imageparam.function().image(imageparam.params,parentclass,frame)
        imgdata = img.flatten()
        
        positions = np.array([[-width/2,-height/2,0.0],
        [width/2,  -height/2, 0.0],
        [width/2,  height/2, 0.0],
        [-width/2,  -height/2, 0.0],
        [-width/2,  height/2, 0.0],
        [width/2,  height/2, 0.0]])
        positions = Rotation.from_euler("xyz",(params.params.Xrotation(),params.params.Yrotation(),params.params.Zrotation()),True).apply(positions)
        secrets = params.params.secrets()
        #print(positions)
        vertexes = np.array([
             positions[0][0]-1280/2+params.params.x(),  positions[0][1]-720/2+params.params.y(), positions[0][2]+params.params.z(), 0.0, 0.0,
             positions[1][0]-1280/2+params.params.x(),  positions[1][1]-720/2+params.params.y(), positions[1][2]+params.params.z(), 1.0, 0.0,
             positions[2][0]-1280/2+params.params.x(),  positions[2][1]-720/2+params.params.y(), positions[2][2]+params.params.z(), 1.0, 1.0,
             positions[3][0]-1280/2+params.params.x(),  positions[3][1]-720/2+params.params.y(), positions[3][2]+params.params.z(), 0.0, 0.0,
             positions[4][0]-1280/2+params.params.x(),  positions[4][1]-720/2+params.params.y(), positions[4][2]+params.params.z(), 0.0, 1.0,
             positions[5][0]-1280/2+params.params.x(),  positions[5][1]-720/2+params.params.y(), positions[5][2]+params.params.z(), 1.0, 1.0],dtype=np.float32)
        if(not secrets.vao):
            #Create a pbo
            params.params.size.setbase(size)
            secrets.pbo = glGenBuffers(1)
            glBindBuffer(GL_PIXEL_UNPACK_BUFFER, secrets.pbo)
            CopyToBuffer(imgdata.ctypes.data,size[0]*size[1]*4)
            #Generate a texture
            secrets.textureid = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D,secrets.textureid)
            CreateTexture(0,size)
            glBindTexture(GL_TEXTURE_2D,0)
            glBindBuffer(GL_PIXEL_UNPACK_BUFFER, 0)
            #Generate a vertex array
            secrets.vao = glGenVertexArrays(1)
            glBindVertexArray(secrets.vao)
            #Generate a vertex buffer
            secrets.vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER,secrets.vbo)
            #Set geometry of the quad
            glBufferData(GL_ARRAY_BUFFER,vertexes,GL_DYNAMIC_DRAW)
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,20,c_void_p(0))
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1,2,GL_FLOAT,GL_FALSE,20,c_void_p(12))
            glBindBuffer(GL_ARRAY_BUFFER,0)
            glBindVertexArray(0)
            secrets.lastsize = size
        elif secrets.lastsize[0] != size[0] or secrets.lastsize[1] != size[1]:
            params.params.size.setbase(size)
            glBindTexture(GL_TEXTURE_2D,0)
            #Delete the buffer
            glDeleteBuffers(1,[secrets.pbo])

            #Make a new buffer
            secrets.pbo = glGenBuffers(1)
            
            glBindTexture(GL_TEXTURE_2D,secrets.textureid)
            CreateTexture(0,size)
            glBindTexture(GL_TEXTURE_2D,0)

            glBindBuffer(GL_PIXEL_UNPACK_BUFFER, 0)
            secrets.lastsize = size
        else:
            #print(glIsTexture(params.params.textureid))
            glBindBuffer(GL_ARRAY_BUFFER,secrets.vbo)
            #Set geometry of the quad
            glBufferData(GL_ARRAY_BUFFER,np.array(vertexes,dtype=np.float32),GL_DYNAMIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER,0)
            glBindBuffer(GL_PIXEL_UNPACK_BUFFER, secrets.pbo)
            glBindTexture(GL_TEXTURE_2D,secrets.textureid)
            UpdateTextureWithBuffer(imgdata.ctypes.data,size[0]*size[1]*4,size)
            #glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,size[0],size[1],0,GL_RGBA,GL_UNSIGNED_BYTE,c_void_p(0))
            
            glBindBuffer(GL_PIXEL_UNPACK_BUFFER, 0)
            #Draw the quad
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glUniform1i(glGetUniformLocation(parentclass.viewport.videorenderer.shader,"image"),0)
            glActiveTexture(GL_TEXTURE0)
            glBindVertexArray(secrets.vao)
            glDrawArrays(GL_TRIANGLES,0,6)
            glBindVertexArray(0)
            glBindTexture(GL_TEXTURE_2D,0)
    def onupdate(self,imageparam,params,parentclass,keyframe):
        img = imageparam.function().image(imageparam.params,parentclass)
        params.params.width.set(int(img.size[0]*params.params.relativewidth/100))
        params.params.height.set(int(img.size[1]*params.params.relativeheight/100))
    def handle(keyframe,parentclass,params):
        return [CzeViewportDraggableHandle(None,parentclass,params.params.x,params.params.y)]
    def __str__(self):
        return self.name

compositingfunctionsdropdown = [["Sound",SoundFile],["Unholy",Unholy]]
#["Normal Media",ImageComposite],

"""vertexes = np.array([
        params.params.x-1280/2,  params.params.y-720/2, sin(parentclass.playbackframe/10)/20, 0.0, 0.0,
        params.params.width+params.params.x-1280/2,  params.params.y-720/2, sin(parentclass.playbackframe/11.9)/20, 1.0, 0.0,
        params.params.width+params.params.x-1280/2,  params.params.height+params.params.y-720/2, cos(parentclass.playbackframe/12.5)/20, 1.0, 1.0,
        params.params.x-1280/2,  params.params.y-720/2, sin(parentclass.playbackframe/10)/20, 0.0, 0.0,
        params.params.x-1280/2,  params.params.height+params.params.y-720/2, cos(parentclass.playbackframe/13.1)/20, 0.0, 1.0,
        params.params.width+params.params.x-1280/2,  params.params.height+params.params.y-720/2, cos(parentclass.playbackframe/12.5)/20, 1.0, 1.0],dtype=np.float32)"""
"""
r = lambda: (random()-0.5)/64
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