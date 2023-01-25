from PIL import Image,ImageFilter,ImageChops
import numpy as np
from generate import put
from scipy.spatial.transform import Rotation as R
from math import pi
from util import *



def find_coeffs(pa, pb):  #get coefficients for Image Transform
    matrix = [] 
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])

    A = np.matrix(matrix, dtype=np.float)
    B = np.array(pb).reshape(8)

    res = np.dot(np.linalg.inv(A.T * A) * A.T, B)
    return np.array(res).reshape(8)

def rotate(vec,angles): #rotate vector by an angle
    
    angle = np.array(angles/180*pi)
    #print(angles)
    rot = R.from_rotvec(angle)
    #print(vec)
    return rot.apply(vec)


def translaterotateproject(width,height,position,rotation,origin,corner,perspective=250): #combined translation, rotation, and projection
    vec = np.array((width*corner[0]-(width*origin[0])/2,height*corner[1]-(height*origin[1])/2,0))
    rotated = rotate(vec,rotation)
    z = 1+rotated[2]/perspective+position[2]
    projected = [(rotated[0]-width*(0.5-origin[0]/2))/z+width/2+position[0],(rotated[1]-height*(0.5-origin[1]/2))/z+height/2+position[1]]
    return projected



def CreateCustomWindowAnimation(image,time=1,startpos=(0,0,0),startrotation=(0,0,0),origin=(0.5,0.5,0)):  #coefficients for animation
    #print("theimage,",image)
    t = min(1,max(0,time))
    startrotation = np.array(startrotation)
    startpos = np.array(startpos)
    NW = translaterotateproject(w(image),h(image),startpos*(1-t),startrotation*(1-t),origin,(0,0,0))
    NE = translaterotateproject(w(image),h(image),startpos*(1-t),startrotation*(1-t),origin,(1,0,0))
    SW = translaterotateproject(w(image),h(image),startpos*(1-t),startrotation*(1-t),origin,(0,1,0))
    SE = translaterotateproject(w(image),h(image),startpos*(1-t),startrotation*(1-t),origin,(1,1,0))
    coeffs = find_coeffs([NW,NE,SE,SW],[[0,0],[w(image),0],[w(image),h(image)],[0,h(image)]])
    return coeffs
def ExecuteCustomWindowAnimation(image,coeffs,time,wallpaper=None,pos=None,align=None): #warp image by coefficients and composite
    t = min(1,max(0,time))
    image = image.transform(image.size, Image.PERSPECTIVE, coeffs,Image.LINEAR);
    no = image.copy()
    no.putalpha(0)
    image = ImageChops.blend(no,image,t)
    if wallpaper:
        image = put(wallpaper.copy(),image.copy(),pos[0],pos[1],align)
    return image

def Composite7(img,GlassMask,time,startpos,startrotation,origin,wallpaper,pos,align): #warp image by coefficients and composite with Windows 7 method
    wallpaper = wallpaper.copy()
    GlassImg = openimage("7/Glass.png")
    WithBorder = put(Image.new("RGBA",(800,602),(0,0,0,0)),GlassImg.resize(wallpaper.size,0),int(-pos[0]+w(img)/16-wallpaper.size[0]/16+pos[0]/8),-pos[1])
    GlassMask = put(Image.new("RGBA",img.size,(255,255,255,0)),GlassMask,14,14)
    WithBorder = ImageChops.multiply(WithBorder,GlassMask)
    IMAGE = put(WithBorder,img,0,0)
    coeffs = CreateCustomWindowAnimation(IMAGE,time,startpos,startrotation,origin)
    IMAGE = ExecuteCustomWindowAnimation(IMAGE,coeffs,time)
    GlassMask = ExecuteCustomWindowAnimation(GlassMask,coeffs,time)
    Blur = wallpaper.filter(ImageFilter.GaussianBlur(radius=6))
    masked = ImageChops.multiply(put(Image.new("RGBA",wallpaper.size,(0,0,0,0)),GlassMask,pos[0]-14, pos[1]-14,align),Blur)
    masked = put(masked,IMAGE,pos[0]-14,pos[1]-14,align)
    wallpaper.alpha_composite(masked)
    return wallpaper
    
composites = {"xp": (lambda img,mask,time,startpos,startrotation,origin,wallpaper,pos,align: ExecuteCustomWindowAnimation(img,CreateCustomWindowAnimation(img,time,startpos,startrotation,origin),time,wallpaper,pos,align)),
              "7": (lambda img,mask,time,startpos,startrotation,origin,wallpaper,pos,align: Composite7(img,mask,time,startpos,startrotation,origin,wallpaper,pos,align)),
              "custom": (lambda img,mask,time,startpos,startrotation,origin,wallpaper,pos,align: ExecuteCustomWindowAnimation(img,CreateCustomWindowAnimation(img,time,startpos,startrotation,origin),time,wallpaper,pos,align))}

def CompositeWindow(img,mask,os,time,startpos,startrotation,origin,wallpaper,pos,align,close,closetime,endpos,endrotation,endorigin,closetimingfunction,timingfunction): #Generic composition function
    global composites
    if close:
        time = 1-closetimingfunction(closetime)
        return composites[os](img,mask,time,endpos,endrotation,endorigin,wallpaper,pos,align)
    else:
        time = timingfunction(time)
        return composites[os](img,mask,time,startpos,startrotation,origin,wallpaper,pos,align)