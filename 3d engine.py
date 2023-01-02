import os
from random import randint
import time
import pip
from math import sin, cos,sqrt
try:
    import keyboard
except:
    print('Installing keybord module...')
    pip.main(['install', "keyboard"])
    try:
        import keyboard
    except:
        print('Failed to install "keyboard" module,\ncheck your internet connection, make sure you have admin privilege\nor try : pip install keybord')
        input()
        exit()



def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)

import sys
sys.excepthook = show_exception_and_exit



# init variables
width,height = os.get_terminal_size()
height-=1
pixelBuffer = [' ']*(width*height-width)
camPosX = 0
camPosY = 0
camPosZ = -5
camRotX = 0
camRotY = 0
last = 0
focalLengh = 1.5
sensitivityMov = 0.35
sensitivityRot = 0.2
color = ".-;=0&@"
# screen
def clear(char):
    for i in range(width*height-width):
        pixelBuffer[i] = char
def draw(*info):
    info = ''.join(info)
    info += ' '*(width - len(info))
    print(info+''.join(pixelBuffer),end='')
def putPixel(x,y,char):
    if 0<=x<width and 0<=y<height-1:
        pixelBuffer[round(y)*width+round(x)] = char

# math
def AddVec3(v1,v2):
    return v1[0]+v2[0],v1[1]+v2[1],v1[2]+v2[2]

def SubVec3(v1,v2):
    return v1[0]-v2[0],v1[1]-v2[1],v1[2]-v2[2]

def dot(v1,v2):
    return v1[0]*v2[0]+v1[1]*v2[1]+v1[2]*v2[2]

def MultScal(l,v):
    return l*v[0],l*v[1],l*v[2]

def crossProd(v1,v2):
    v = []
    v.append(v1[1]*v2[2]-v1[2]*v2[1])
    v.append(v1[2]*v2[0]-v1[0]*v2[2])
    v.append(v1[0]*v2[1]-v1[1]*v2[0])
    return v

def dist(v):
    return sqrt(v[0]**2+v[1]**2+v[2]**2)

def normalize(v):
    l = dist(v)
    return [v[0]/l,v[1]/l,v[2]/l] if l!=0 else 0.0

# transform
def projection(pos):
    nz = focalLengh*2*pos[2]/2
    px = (2*height/width)*pos[0]/nz
    py = -pos[1]/nz
    return round((px+1)*width/2),round((py+1)*height/2)

def rotationx(pos):
    y1=cos(camRotX)*pos[1]-sin(camRotX)*pos[2]
    z1=sin(camRotX)*pos[1]+cos(camRotX)*pos[2]
    return pos[0],y1,z1

def rotationy(pos):
    x1=cos(camRotY)*pos[0]+sin(camRotY)*pos[2]
    z1=-sin(camRotY)*pos[0]+cos(camRotY)*pos[2]
    return x1,pos[1],z1

def transform(tri):
    clipped = clipping(tri)
    if clipped is None:
        return
    for tri2 in clipped:
        v=[]
        translated = [AddVec3(i,(-camPosX,-camPosY,-camPosZ)) for i in tri2]
        line1 = SubVec3(tri2[1],tri2[0])
        line2 = SubVec3(tri2[2],tri2[0])
        norm = normalize(crossProd(line1,line2))
        if dot(norm,SubVec3(translated[0],[camPosX,camPosY,camPosZ])) < 0:
            v = [projection(rotationx(rotationy(i))) for i in translated]
            lum = getChar(dot(norm,[0,0,-1]))
            #v = [projection(rotationx(rotationy(AddVec3(i,(-camPosX,-camPosY,-camPosZ))))) for i in tri2]
            triangle(v,lum)

# rasterization
def getChar(value):
    return color[round(value*6)] if value>=0 else "."

def eq(p,a,b):
    return (a[0]-p[0])*(b[1]-p[1])-(a[1]-p[1])*(b[0]-p[0])

def triangle(pos,char):    
    xmin = min(pos[0][0],pos[1][0],pos[2][0])
    xmax = max(pos[0][0],pos[1][0],pos[2][0])+1
    ymin = min(pos[0][1],pos[1][1],pos[2][1])
    ymax = max(pos[0][1],pos[1][1],pos[2][1])+1
    for y in range(ymin,ymax):
        if 0<=y<height-1:
            pass
        else:
            continue
        for x in range(xmin,xmax):
            if 0<=x<width:
                pass
            else:
                continue
            w0=eq((x,y),pos[2],pos[0])
            w1=eq((x,y),pos[0],pos[1])
            w2=eq((x,y),pos[1],pos[2])
            if (w0 >= 0 and w1 >= 0 and w2 >= 0) or (-w0 >= 0 and -w1 >= 0 and -w2 >= 0):
                putPixel(x,y,char)

def mesh(m):
    for tri in m:
        transform(tri)

def LinePlaneCollision(planeNormal, planePoint, p1, p2):
    u=SubVec3(p2,p1)
    dotp = dot(planeNormal,u)
    if abs(dotp) < 1e-2:
        return (0,0,0)
    
    w = SubVec3(p1, planePoint)
    si = -dot(planeNormal,w)/dotp
    u = MultScal(si,u)
    return AddVec3(p1,u)

def inZ(planeNormal, planePoint,tri):
    L = []
    for vert in tri:
        v = SubVec3(planePoint,vert)
        sign = dot(v,planeNormal)
        if sign>0:
            L.append(vert)
    return L

def clipping(tri):
    global camPos
    v = tri.copy()
    clip = []
    normal = (-sin(camRotY)*cos(camRotX),sin(camRotX),cos(camRotY)*cos(camRotX))
    camPos = (camPosX,camPosY,camPosZ)
    zNear = AddVec3(camPos,MultScal(0.1,normal))
    L = inZ(normal,zNear,v)

    if len(L) == 0:
        return [v]
    elif len(L) == 3:
        return None
    elif len(L) == 1:
        v.remove(L[0])
        vi0 = LinePlaneCollision(normal,zNear,v[0],L[0])
        vi1 = LinePlaneCollision(normal,zNear,v[1],L[0])
        clip.append([vi0,v[0],v[1]])
        clip.append([vi0,v[1],vi1])
    elif len(L) == 2:
        v.remove(L[0])
        v.remove(L[1])
        vi0 = LinePlaneCollision(normal,zNear,L[0],v[0])
        vi1 = LinePlaneCollision(normal,zNear,L[1],v[0])
        clip.append([vi0,vi1,v[0]])
    return clip

# obj
def loadObj(name):
    f = open(name, "r")
    lines = [line.rstrip('\n').split(' ') for line in f.readlines() if line.rstrip('\n')]
    f.close()
    vert = [list(map(float,line[1:])) for line in lines if line[0] == 'v']
    order = [line[1:] for line in lines if line[0] == 'f']

    vertex = []
    for tri in order:
        if len(tri) == 4:
            vertex.append([vert[int(tri[0])-1],vert[int(tri[1])-1],vert[int(tri[2])-1]])
            vertex.append([vert[int(tri[2])-1],vert[int(tri[3])-1],vert[int(tri[0])-1]])
        if len(tri) == 3:
            vertex.append([vert[int(tri[0])-1],vert[int(tri[1])-1],vert[int(tri[2])-1]])
    return vertex

# main loop
vertex = loadObj("test.obj")

while True:
    clear(' ')

    current = time.time()
    dt = (current-last)*10
    last=current

    if keyboard.is_pressed("down arrow"):
        if camRotX>-1.57:
            camRotX-=dt*sensitivityRot
    if keyboard.is_pressed("up arrow"):
        if camRotX<1.57:
            camRotX+=dt*sensitivityRot
    if keyboard.is_pressed("left arrow"):
        camRotY+=dt*sensitivityRot
    if keyboard.is_pressed("right arrow"):
        camRotY-=dt*sensitivityRot
    if keyboard.is_pressed("s"):
        camPosX-=-sin(camRotY)*dt*sensitivityMov
        camPosZ-=cos(camRotY)*dt*sensitivityMov
    if keyboard.is_pressed("z"):
        camPosX+=-sin(camRotY)*dt*sensitivityMov
        camPosZ+=cos(camRotY)*dt*sensitivityMov
    if keyboard.is_pressed("d"):
        camPosX+=cos(camRotY)*dt*sensitivityMov
        camPosZ+=sin(camRotY)*dt*sensitivityMov
    if keyboard.is_pressed("q"):
        camPosX-=cos(camRotY)*dt*sensitivityMov
        camPosZ-=sin(camRotY)*dt*sensitivityMov
    if keyboard.is_pressed("shift"):
        camPosY-=dt*sensitivityMov
    if keyboard.is_pressed("space"):
        camPosY+=dt*sensitivityMov
    mesh(vertex)
    if dt>0:
        fps = 10/dt
    draw(" fps : ",str(round(fps)))