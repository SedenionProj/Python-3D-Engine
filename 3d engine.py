import os
import time
import pip
from math import sin, cos, sqrt
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

# init variables
width,height = os.get_terminal_size()
pixelBuffer = [' ']*(width*height-width)
camPosX = 0
camPosY = 0
camPosZ = 0
camRotX = 0
camRotY = 0
last = 0
focalLengh = 1
sensitivityMov = 0.5
sensitivityRot = 0.25

# screen
def clear(char):
    for i in range(width*height-width):
        pixelBuffer[i] = char
def draw():
    print(''.join(pixelBuffer),end='')
def putPixel(x,y,char):
    if 0<=x<width and 0<=y<height-1:
        pixelBuffer[round(y)*width+round(x)] = char

# math
def AddVec3(v1,v2):
    return v1[0]+v2[0],v1[1]+v2[1],v1[2]+v2[2]

# transform
def projection(pos):
    nz = (2*pos[2]/2)
    px = (2*height/width)*pos[0]*focalLengh/nz
    py = -pos[1]*focalLengh/nz
    return round((px+1)*width/2),round((py+1)*height/2)

def rotationx(pos):
    y1=cos(camRotX)*pos[1]-sin(camRotX)*pos[2]
    z1=sin(camRotX)*pos[1]+cos(camRotX)*pos[2]
    return pos[0],y1,z1

def rotationy(pos):
    x1=cos(camRotY)*pos[0]+sin(camRotY)*pos[2]
    z1=-sin(camRotY)*pos[0]+cos(camRotY)*pos[2]
    return x1,pos[1],z1

def transform(vertex):
    v=[]
    for pos in vertex:
        v.append(projection(rotationx(rotationy(AddVec3(pos,(camPosX,camPosY,camPosZ))))))
    triangle(v)


# rasterization
def eq(p,a,b):
    return (a[0]-p[0])*(b[1]-p[1])-(a[1]-p[1])*(b[0]-p[0])

def triangle(pos):    
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
                putPixel(x,y,'#')

def mesh(m):
    for tri in m:
        transform(tri)

# main loop
vertex = [[(-1,-1,1),(-1,-1,3),(1,-1,1)],
         [(-1,-1,3),(1,-1,1),(1,-1,3)]]

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
    if keyboard.is_pressed("z"):
        camPosX-=-sin(camRotY)*dt*sensitivityMov
        camPosZ-=cos(camRotY)*dt*sensitivityMov
    if keyboard.is_pressed("s"):
        camPosX+=-sin(camRotY)*dt*sensitivityMov
        camPosZ+=cos(camRotY)*dt*sensitivityMov
    if keyboard.is_pressed("q"):
        camPosX+=cos(camRotY)*dt*sensitivityMov
        camPosZ+=sin(camRotY)*dt*sensitivityMov
    if keyboard.is_pressed("d"):
        camPosX-=cos(camRotY)*dt*sensitivityMov
        camPosZ-=sin(camRotY)*dt*sensitivityMov
    if keyboard.is_pressed("space"):
        camPosY-=dt*sensitivityMov
    if keyboard.is_pressed("shift"):
        camPosY+=dt*sensitivityMov
    mesh(vertex)
    draw()