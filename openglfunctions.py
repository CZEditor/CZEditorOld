from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
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
    main = """#version 450 core
in vec2 fragmentColor;
uniform sampler2D image;
uniform float frame;
layout(location = 0) out vec4 color;
""" if isframebuffer else """#version 450 core
in vec2 fragmentColor;
uniform sampler2D image;
uniform float frame;
out vec4 color;
"""
    for snippet in shader:
        main += snippet[3]+"\n"
        if(snippet[4]):
            break

    main+= """void main()
{
    vec2 pos1,pos2;
    pos1 = fragmentColor;
    pos2 = vec2(0,0);
    """

    curInPosName = "pos1"
    curOutPosName = "pos2"
    shaderlist = []
    for snippet in shader:
        shaderlist.append(snippet[1])
        if(snippet[4]):
            main += f"color = {snippet[2].replace('$inpos',curInPosName).replace('$outpos',curOutPosName)}\n}}"
            break
        else:
            main += snippet[2].replace("$inpos",curInPosName).replace("$outpos",curOutPosName)+"\n    "
        curInPosName,curOutPosName = curOutPosName,curInPosName #Swap them
    else: #for has an else, it executes if the loop DIDN'T break.
        main += f"color = texture(image,{curInPosName});\n}}"
    #print(main)
    shaders=[
        compileShader("""#version 450 core
layout (location=0) in vec3 vertexPos;
layout (location=1) in vec2 vertexColor;
uniform highp mat4 matrix;
out vec2 fragmentColor;
void main()
{
    gl_Position = matrix*vec4(vertexPos, 1.0);
    fragmentColor = vertexColor;
}""" if not isframebuffer else """#version 450 core
layout (location=0) in vec3 vertexPos;
layout (location=1) in vec2 vertexColor;
out vec2 fragmentColor;
void main()
{
    gl_Position = vec4(vertexPos.x, vertexPos.y, 0.0,1.0);
    fragmentColor = vertexColor;
}""",GL_VERTEX_SHADER)
    ]+\
    shaderlist+\
    [compileShader(main,GL_FRAGMENT_SHADER)]
    return shaders