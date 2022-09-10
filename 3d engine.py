import os
import time
import pip
from math import sin, cos
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
height-=1
pixelBuffer = [' ']*(width*height-width)
camPosX = 0
camPosY = 0
camPosZ = -5
camRotX = 0
camRotY = 0
last = 0
focalLengh = 1
sensitivityMov = 0.35
sensitivityRot = 0.2

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
    v=[projection(rotationx(rotationy(AddVec3(pos,(-camPosX,-camPosY,-camPosZ))))) for pos in tri]
    test=[projection(pos) for pos in tri]

    clipped = clipping(tri)

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

def LinePlaneCollision(planeNormal, planePoint, p1, p2):
    u=SubVec3(p2,p1)
    dotp = dot(planeNormal,u)
    if abs(dotp) < 1e-2:
        return '// '
    
    w = SubVec3(p1, planePoint)
    si = -dot(planeNormal,w)/dotp
    u = MultScal(si,u)
    return AddVec3(p1,u)

def inZ(planeNormal, planePoint, p):
    v = SubVec3(planePoint,p)
    sign = dot(v,planeNormal)
    if sign>0:
        return True
    return False

def clipping(tri):
    global inf
    global camPos
    normal = (-sin(camRotY)*cos(camRotX),sin(camRotX),cos(camRotY)*cos(camRotX))
    camPos = (camPosX,camPosY,camPosZ)
    inf =(inZ(normal,camPos,tri[0]),inZ(normal,camPos,tri[1]),inZ(normal,camPos,tri[2]))
    LinePlaneCollision(normal,camPos,tri[0],tri[1])



# main loop
vertex = [[(-1,-1,2),(-1,-1,10),(1,-1,2)]]
         #[(-1,-1,3),(1,-1,1),(1,-1,3)]]

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
    #(camPosX,camPosY,camPosZ),LinePlaneCollision((-sin(camRotY)*cos(camRotX),sin(camRotX),cos(camRotY)*cos(camRotX)),(camPosX,camPosY,camPosZ),(0,-1,0),(0,1,0))
    if dt>0:
        fps = 10/dt
    draw(str(inf),str(camPos)," fps : ",str(fps))
    