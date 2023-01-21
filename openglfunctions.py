from OpenGL.GL import *
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