from PIL import Image
from util import ParamLink,Params
from handles import CzeViewportDraggableHandle
from PySide6.QtGui import QMatrix4x4
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
from OpenGL.GL.shaders import compileProgram,compileShader
from traceback import print_exc
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
        "secrets":TransientProperty(Params({
            "lastplaying":False
        }))
    })
    def soundeffect(source,params,sample):
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
        "shader":StringProperty("color = texture(image,pos);"),
        "secrets":TransientProperty(Params({
            "textureid":0,
            "vbo":0,
            "vao":0,
            "pbo":0,
            "lastsize":(32,32),
            "lastshader":"",
            "shader":None
        }))
        
    })
    
    def composite(imageparam,params,parentclass,keyframe,frame):
       #composite(image,vertices,shader,windowObject,keyframe,frame) - > (image,vertices,shader)
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
        if(secrets.lastshader != params.params.shader()):
            secrets.shader = compileProgram(compileShader("""#version 450 core
layout (location=0) in vec3 vertexPos;
layout (location=1) in vec2 vertexColor;
uniform highp mat4 matrix;
out vec2 pos;
void main()
{
    //gl_Position = round(matrix*vec4(vertexPos, 1.0)*256)/256;
    gl_Position = matrix*vec4(vertexPos, 1.0);
    pos = vertexColor;
}""",GL_VERTEX_SHADER),
compileShader("""#version 450 core
in vec2 pos;
uniform sampler2D image;
uniform float t;
out vec4 color;
void main()
{
    """+params.params.shader()+"""
}""",GL_FRAGMENT_SHADER))
            secrets.lastshader = params.params.shader()
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
            glUseProgram(secrets.shader)
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            projection = QMatrix4x4()
            projection.frustum(-1280/32,1280/32,720/32,-720/32,64,4096)
            projection.translate(0,0,-1024)
            glUniformMatrix4fv(glGetUniformLocation(secrets.shader,"matrix"),1,GL_FALSE,np.array(projection.data(),dtype=np.float32))
            glUniform1i(glGetUniformLocation(secrets.shader,"image"),0)
            glUniform1f(glGetUniformLocation(secrets.shader,"t"),frame)
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

class Media2D:
    name = "2D Media",
    params = Params({
        "x":IntProperty(0),
        "y":IntProperty(0),
        "rotation":IntProperty(0),
        "size":SizeProperty(1280,720,1280,720),
        "transient":TransientProperty(Params({
            "lastsize":(32,32)
        }))
    })
    def composite(image,vertices,shader,params,windowObject,keyframe,frame):

        transient = params.transient()

        width,height = params.size()

        imageResolution = (image.shape[1],image.shape[0])

        x,y = params.x(), params.y()

        if transient.lastsize[0] != imageResolution[0] or transient.lastsize[1] != imageResolution[1]: #Detect change in image resolution

            params.size.setbase(imageResolution)

            transient.lastsize = imageResolution

            width,height = params.size()
        
        unrotatedVertices = np.array([[-width/2,-height/2,0.0, 0.0, 0.0],
        [width/2,  -height/2, 0.0, 1.0, 0.0],
        [width/2,  height/2, 0.0, 1.0, 1.0],
        [-width/2,  -height/2, 0.0, 0.0, 0.0],
        [-width/2,  height/2, 0.0, 0.0, 1.0],
        [width/2,  height/2, 0.0, 1.0, 1.0]],dtype=np.float32)

        angle = np.deg2rad(params.rotation())

        rotationMatrix = np.array([[np.cos(angle),-np.sin(angle)],
                                   [np.sin(angle),np.cos(angle)]])

        rotatedVertices = np.hstack(((rotationMatrix @ (unrotatedVertices[:,:2].T)).T,unrotatedVertices[:,2:]))

        rotatedVertices[:,:2] += (x,y)
        
        return image,np.concatenate([vertices,rotatedVertices]),shader

    def handle(keyframe,parentclass,params):
        return [CzeViewportDraggableHandle(None,parentclass,params.params.x,params.params.y)]

class Media3D:
    name = "3D Media",
    params = Params({
        "x":IntProperty(0),
        "y":IntProperty(0),
        "z":IntProperty(0),
        "rotationX":IntProperty(0),
        "rotationY":IntProperty(0),
        "rotationZ":IntProperty(0),
        "size":SizeProperty(1280,720,1280,720),
        "transient":TransientProperty(Params({
            "lastsize":(32,32)
        }))
    })
    def composite(image,vertices,shader,params,windowObject,keyframe,frame):

        transient = params.transient()

        width,height = params.size()

        imageResolution = (image.shape[1],image.shape[0])

        x,y,z = params.x(), params.y(), params.z()

        if transient.lastsize[0] != imageResolution[0] or transient.lastsize[1] != imageResolution[1]: #Detect change in image resolution

            params.size.setbase(imageResolution)

            transient.lastsize = imageResolution

            width,height = params.size()
        
        newvertices = np.array([[-width/2,-height/2, 0.0, 0.0, 0.0],
        [width/2,  -height/2, 0.0, 1.0, 0.0],
        [width/2,  height/2, 0.0, 1.0, 1.0],
        [-width/2,  -height/2, 0.0, 0.0, 0.0],
        [-width/2,  height/2, 0.0, 0.0, 1.0],
        [width/2,  height/2, 0.0, 1.0, 1.0]],dtype=np.float32)

        newvertices = np.hstack(
                (
                    Rotation.from_euler("xyz",(
                            params.rotationX(),
                            params.rotationY(),
                            params.rotationZ()),True).apply(
                        newvertices[:,:3]
                    ),
                    newvertices[:,3:]
                )
            )

        newvertices[:,:3] += (x,y,z)
        
        return image,np.concatenate([vertices,newvertices]),shader

    def handle(keyframe,parentclass,params):
        return [CzeViewportDraggableHandle(None,parentclass,params.params.x,params.params.y)]

class BasicShader:
    name = "Basic Shader"
    params = Params({
        "transient":TransientProperty(Params({
            "shader":None
        }))
    })
    def composite(image,vertices,shader,params,windowObject,keyframe,frame):
        transient = params.transient()
        if(transient.shader is None):

            transient.shader = compileShader("""#version 450 core
                void shaderbasic(in vec2 inpos, out vec2 outpos){
                    outpos = inpos;
                }
            """,GL_FRAGMENT_SHADER)
        
        shader.append({"fragmentshader":transient.shader,
                       "fragmentlinetoadd":"shaderbasic($inpos,$outpos);",
                       "fragmentdeclaration":"void shaderbasic(in vec2 inpos, out vec2 outpos);"})
        return image,vertices,shader

class ScrollingShader:
    name = "Scrolling Shader"
    params = Params({
        "speedX":FloatProperty(1.0),
        "speedY":FloatProperty(1.0),
        "transient":TransientProperty(Params({
            "shader":None
        }))
    })
    def composite(image,vertices,shader,params,windowObject,keyframe,frame):
        transient = params.transient()
        if(transient.shader is None):

            transient.shader = compileShader("""#version 450 core
                void shaderscrolling(in vec2 inpos, float frame,float speedx, float speedy, out vec2 outpos){
                    outpos = mod(inpos+vec2(frame*speedx/60,frame*speedy/60),1);
                }
            """,GL_FRAGMENT_SHADER)
        # TODO : Add more complex stuff, like custom equations or scaling the tile effect
        shader.append({"fragmentshader":transient.shader,
                       "fragmentlinetoadd":"shaderscrolling($inpos,frame,"+str(params.speedX())+","+str(params.speedY())+",$outpos);", # TODO : Do not pass in parameters like this (You would have to recompile every time if the properties were animated). Use a uniform.
                       "fragmentdeclaration":"void shaderscrolling(in vec2 inpos, float frame, float speedx, float speedy, out vec2 outpos);"})
        return image,vertices,shader

class TilingShader:
    name = "Tiling Shader"
    params = Params({
        "amountX":FloatProperty(1.0),
        "amountY":FloatProperty(1.0),
        "transient":TransientProperty(Params({
            "shader":None
        }))
    })
    def composite(image,vertices,shader,params,windowObject,keyframe,frame):
        transient = params.transient()
        if(transient.shader is None):

            transient.shader = compileShader("""#version 450 core
                void shadertiling(in vec2 inpos, float amountx, float amounty, out vec2 outpos){
                    outpos = mod(inpos*vec2(amountx,amounty),1);
                }
            """,GL_FRAGMENT_SHADER)
        shader.append({"fragmentshader":transient.shader,
                       "fragmentlinetoadd":"shadertiling($inpos,"+str(params.amountX())+","+str(params.amountY())+",$outpos);",
                       "fragmentdeclaration":"void shadertiling(in vec2 inpos, float amountx, float amounty, out vec2 outpos);"})
        return image,vertices,shader

class CustomShader:
    name = "Custom Shader"
    params = Params({
        "variableA":FloatProperty(0.0),
        "variableB":FloatProperty(0.0),
        "custom":StringProperty("outpos = inpos;"),
        "transient":TransientProperty(Params({
            "shader":None,
            "previousCustom":"",
            "previousIndex":None
        }))
    })
    def composite(image,vertices,shader,params,windowObject,keyframe,frame):
        transient = params.transient()
        index = len(shader) #There may be a better way to avoid function name collisions, but this works, it's just not really efficient.
        if(transient.shader is None or params.custom() != transient.previousCustom or transient.previousIndex != index):

            transient.shader = compileShader("""#version 450 core
                void shadercustom"""+str(index)+"""(in vec2 inpos, float frame, vec3 worldpos, in float spectrum[512], float variableA, float variableB, out vec2 outpos){
                    """+params.custom()+"""
                }
            """,GL_FRAGMENT_SHADER)

            transient.previousCustom = params.custom()
            transient.previousIndex = index

        shader.append({"fragmentshader":transient.shader,
                       "fragmentlinetoadd":"shadercustom"+str(index)+"($inpos,frame,worldPos,spectrum"+str(params.variableA())+","+str(params.variableB())+",$outpos);",
                       "fragmentdeclaration":"void shadercustom"+str(index)+"(in vec2 inpos, float frame, vec3 worldpos, in float spectrum[512], float variableA, float variableB, out vec2 outpos);"})
        return image,vertices,shader

class CustomColorShader:
    name = "Custom Color Shader"
    params = Params({
        "variableA":FloatProperty(0.0),
        "variableB":FloatProperty(0.0),
        "custom":StringProperty("color = texture(image,inpos);"),
        "transient":TransientProperty(Params({
            "shader":None,
            "previousCustom":"",
            "previousIndex":None
        }))
    })
    def composite(image,vertices,shader,params,windowObject,keyframe,frame):
        transient = params.transient()
        index = len(shader) #There may be a better way to avoid function name collisions, but this works, it's just not really efficient.
        if(transient.shader is None or params.custom() != transient.previousCustom or transient.previousIndex != index):

            transient.shader = compileShader("""#version 450 core
                vec4 shadercustom"""+str(index)+"""(in vec2 inpos, float frame, int width, int height, vec3 worldpos, in float spectrum[512], in sampler2D image,float variableA, float variableB){
                    vec4 color = vec4(1,1,1,1);
                    """+params.custom()+"""
                    return color;
                }
            """,GL_FRAGMENT_SHADER)

            transient.previousCustom = params.custom()
            transient.previousIndex = index

        shader.append({"fragmentshader":transient.shader,
                       "fragmentlinetoadd":"shadercustom"+str(index)+"($inpos,frame,width,height,worldPos,spectrum,image,"+str(params.variableA())+","+str(params.variableB())+");",
                       "fragmentdeclaration":"vec4 shadercustom"+str(index)+"(in vec2 inpos, float frame, int width, int height, vec3 worldpos, in float spectrum[512], in sampler2D image,float variableA, float variableB);",
                       "ismultisample":True})
        return image,vertices,shader

class CustomCode:
    name = "Custom Code"
    params = Params({
        "code":StringProperty("")
    })
    def composite(image,vertices,shader,params,windowObject,keyframe,frame):
        try:
            localdict = {"image":image,"vertices":vertices,"shader":shader,"frame":frame,"keyframe":keyframe,"windowObject":windowObject}
            exec(params.code(),globals(),localdict)
            image = localdict["image"]
            vertices = localdict["vertices"]
            shader = localdict["shader"]
            return image,vertices,shader
        except Exception:
            print_exc()
            return image,vertices,shader
"""
class Shader():
    name = "Shader"
    params = Params({
        "shader":StringProperty(""),
        "secrets":SecretProperty(Params({
            "lastshader":""
        }))
    })
    def composite(imageparam,params)"""


class BlurShader:
    name = "Blur Shader"
    params = Params({
        "transient":TransientProperty(Params({
            "shader":None
        }))
    })
    def composite(image,vertices,shader,params,windowObject,keyframe,frame):
        transient = params.transient()
        if(transient.shader is None):

            transient.shader = compileShader("""#version 450 core
                vec4 shaderblur(in vec2 inpos, int width, int height, in sampler2D image){
                    vec4 color = vec4(0,0,0,0); // So you DO have to initialize it...
                    //color = texture(image,inpos+1/vec2(width,height))/9+texture(image,inpos+1/vec2(width,0))/9+texture(image,inpos+1/vec2(width,-height))/9+texture(image,inpos+1/vec2(0,height))/9+texture(image,inpos)/9+texture(image,inpos+1/vec2(0,-height))/9+texture(image,inpos+1/vec2(-width,height))/9+texture(image,inpos+1/vec2(-width,0))/9+texture(image,inpos+1/vec2(-width,-height))/9;
                    for(int x = -1; x<=1;x++){
                        for(int y = -1; y<=1; y++){
                            color = color+texture(image,inpos+vec2(x,y)/vec2(width,height))/9;
                        }
                    }
                    return color;
                }
            """,GL_FRAGMENT_SHADER)
        shader.append({"fragmentshader":transient.shader,
                       "fragmentlinetoadd":"shaderblur($inpos,width,height,image);",
                       "fragmentdeclaration":"vec4 shaderblur(in vec2 inpos, int width, int height, in sampler2D image);",
                       "ismultisample":True})
        return image,vertices,shader


class GlitchShader:
    name = "Glitch Shader"
    params = Params({
        "amount":IntProperty(1),
        "transient":TransientProperty(Params({
            "shader":None
        }))
    })
    def composite(image,vertices,shader,params,windowObject,keyframe,frame):
        transient = params.transient()
        if(transient.shader is None):

            transient.shader = compileShader("""#version 450 core
                vec4 shaderglitch(in vec2 inpos, int amount, in sampler2D image){
                    vec4 color;
                    for(int i=0; i<amount; i++){
                        vec4 color += texture(image,inpos)/amount;
                    }
                    return color;
                }
            """,GL_FRAGMENT_SHADER)
        shader.append({"fragmentshader":transient.shader,
                       "fragmentlinetoadd":"shaderglitch($inpos,"+str(params.amount())+",image);", 
                       "fragmentdeclaration":"vec4 shaderglitch(in vec2 inpos, int amount, in sampler2D image);",
                       "ismultisample":True})
        return image,vertices,shader

class CustomVertexShader:
    name = "Custom Vertex Shader"
    params = Params({
        "variableA":FloatProperty(0.0),
        "variableB":FloatProperty(0.0),
        "custom":StringProperty("outpos = inpos;"),
        "transient":TransientProperty(Params({
            "shader":None,
            "previousCustom":"",
            "previousIndex":None
        }))
    })
    def composite(image,vertices,shader,params,windowObject,keyframe,frame):
        transient = params.transient()
        index = len(shader) #There may be a better way to avoid function name collisions, but this works, it's just not really efficient.
        if(transient.shader is None or params.custom() != transient.previousCustom or transient.previousIndex != index):

            transient.shader = compileShader("""#version 450 core
                void shadercustom"""+str(index)+"""(in vec3 inpos, in vec2 vertexColor, in float spectrum[512], float variableA, float variableB, float frame, out vec3 outpos){
                    """+params.custom()+"""
                }
            """,GL_VERTEX_SHADER)

            transient.previousCustom = params.custom()
            transient.previousIndex = index

        shader.append({"vertexshader":transient.shader,
                       "vertexlinetoadd":"shadercustom"+str(index)+"($inpos,vertexColor,spectrum,"+str(params.variableA())+","+str(params.variableB())+",frame,$outpos);",
                       "vertexdeclaration":"void shadercustom"+str(index)+"(in vec3 inpos, in vec2 vertexColor, in float spectrum[512], float variableA, float variableB, float frame, out vec3 outpos);"})
        return image,vertices,shader

compositingfunctionsdropdown = [["Media 2D",Media2D],["Media 3D",Media3D],["Basic Shader",BasicShader],["Scrolling Shader",ScrollingShader],["Tiling Shader",TilingShader],["Custom Shader",CustomShader],["Custom Code",CustomCode],["Blur Shader",BlurShader],["Glitch Shader",GlitchShader],["Custom Vertex Shader",CustomVertexShader],["Custom Color Shader",CustomColorShader]]
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