from OpenGL.GL import *
from customShaderCompilation import compileProgram,compileShader
from ctypes import c_void_p
import numpy as np
from scipy.spatial.transform import Rotation
# Copy a pointer to a bound opengl GL_PIXEL_UNPACK_BUFFER
def CopyToBuffer(pointer:int,maxlen:int):
    glBufferData(GL_PIXEL_UNPACK_BUFFER, maxlen,None, GL_STREAM_DRAW)
    data = glMapBuffer(GL_PIXEL_UNPACK_BUFFER,GL_WRITE_ONLY)
    array = (GLubyte*maxlen).from_address(data)
    ctypes.memmove(array,pointer,maxlen)
    glUnmapBuffer(GL_PIXEL_UNPACK_BUFFER)


# Create a bound RGBA texture with glTexImage2D and a pointer to image data
def CreateTexture(pointer:int,size:tuple):
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_BORDER)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_BORDER)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_BASE_LEVEL,0)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAX_LEVEL,0)
    
    glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,size[0],size[1],0,GL_RGBA,GL_UNSIGNED_BYTE,c_void_p(pointer))

# CopyToBuffer but with a glTexSubImage2D appended.
def UpdateTextureWithBuffer(pointer:int,maxlen:int,size:tuple):
    glBufferData(GL_PIXEL_UNPACK_BUFFER, maxlen, None, GL_STREAM_DRAW)
    data = glMapBuffer(GL_PIXEL_UNPACK_BUFFER,GL_WRITE_ONLY)
    array = (GLubyte*maxlen).from_address(data)
    ctypes.memmove(array,pointer,maxlen)
    glUnmapBuffer(GL_PIXEL_UNPACK_BUFFER)
    glTexSubImage2D(GL_TEXTURE_2D,0,0,0,size[0],size[1],GL_RGBA,GL_UNSIGNED_BYTE,c_void_p(0))

def RotatePoints(points, X, Y, Z):
    return np.hstack(
                (
                    Rotation.from_euler("xyz",(
                            X,
                            Y,
                            Z),True).apply(
                        points[:,:3]
                    ),
                    points[:,3:]
                )
            )


def GenerateShader(shader,isframebuffer=False):
    vertexshaderlist = []
    if(not isframebuffer):
        vertexDeclarations = "\n"
        for snippet in shader:
            if("vertexshader" in snippet):
                vertexDeclarations += snippet["vertexdeclaration"]+"\n"
                if("ismultisample" in snippet):
                    break
        addedVertexFunctions = ""
        curInPosName = "pos1"
        curOutPosName = "pos2"
        for snippet in shader:
            if("vertexshader" in snippet):
                vertexshaderlist.append(snippet["vertexshader"])
                addedVertexFunctions += snippet["vertexlinetoadd"].replace("$inpos",curInPosName).replace("$outpos",curOutPosName)+"\n    "
                curInPosName,curOutPosName = curOutPosName,curInPosName #Swap them
        addedVertexFunctions += f"gl_Position = matrix*vec4({curInPosName},1.0);"
        mainvertexcode = """#version 450 core
layout (location=0) in vec3 vertexPos;
layout (location=1) in vec2 vertexColor;
uniform highp mat4 matrix;
uniform float frame;
uniform float spectrum[512];
out vec2 fragmentColor;
out vec3 worldPos;"""+vertexDeclarations+"""void main()
{
    vec3 pos1, pos2;
    pos1 = vertexPos;
    pos2 = vec3(0,0,0);
    """+addedVertexFunctions+"""
    fragmentColor = vertexColor;
    worldPos = """+curInPosName+""";
}"""
    else:
        mainvertexcode = """#version 450 core
layout (location=0) in vec3 vertexPos;
layout (location=1) in vec2 vertexColor;
uniform float frame;
uniform float spectrum[512];
out vec2 fragmentColor;
out vec3 worldPos;
void main()
{
    gl_Position = vec4(vertexColor.x*2-1, vertexColor.y*2-1, 0.0,1.0);
    fragmentColor = vertexColor;
    worldPos = vertexPos;
}"""

    mainfragmentcode = """#version 450 core
in vec2 fragmentColor;
in vec3 worldPos;
uniform sampler2D image;
uniform float frame;
uniform int width;
uniform int height;
uniform float spectrum[512];
layout(location = 0) out vec4 color;
""" if isframebuffer else """#version 450 core
in vec2 fragmentColor;
in vec3 worldPos;
uniform sampler2D image;
uniform float frame;
uniform int width;
uniform int height;
uniform float spectrum[512];
out vec4 color;
"""
    addedDeclarations = []
    for snippet in shader:
        if("fragmentshader" in snippet and snippet["fragmentdeclaration"] not in addedDeclarations):
            mainfragmentcode += snippet["fragmentdeclaration"]+"\n"
            addedDeclarations.append(snippet["fragmentdeclaration"])
            if("ismultisample" in snippet):
                break

    mainfragmentcode+= """void main()
{
    vec2 pos1,pos2;
    pos1 = fragmentColor;
    pos2 = vec2(0,0);
    """

    curInPosName = "pos1"
    curOutPosName = "pos2"
    fragmentshaderlist = []
    for snippet in shader:
        if("fragmentshader" in snippet):
            fragmentshaderlist.append(snippet["fragmentshader"])
            if("ismultisample" in snippet):
                mainfragmentcode += f"color = {snippet['fragmentlinetoadd'].replace('$inpos',curInPosName).replace('$outpos',curOutPosName)}\n}}"
                break
            else:
                mainfragmentcode += snippet["fragmentlinetoadd"].replace("$inpos",curInPosName).replace("$outpos",curOutPosName)+"\n    "
            curInPosName,curOutPosName = curOutPosName,curInPosName #Swap them
    else: #for DOES have an else, it executes if the loop DIDN'T break.
        mainfragmentcode += f"color = texture(image,{curInPosName});\n}}"
    
    mainvertexshader = compileShader(mainvertexcode,GL_VERTEX_SHADER)
    mainfragmentshader = compileShader(mainfragmentcode,GL_FRAGMENT_SHADER)
    shaders=vertexshaderlist+\
    [
        mainvertexshader
    ]+\
    fragmentshaderlist+\
    [mainfragmentshader]

    return shaders,(mainvertexshader,mainfragmentshader)