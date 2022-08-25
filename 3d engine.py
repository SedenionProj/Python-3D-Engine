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
width,height = os.get_terminal_size()
pixelBuffer = [' ']*(width*height-width)
focalLengh = 1
c=0

def clear(char):
    for i in range(width*height-width):
        pixelBuffer[i] = char
def draw():
    print(''.join(pixelBuffer),end='')
def putPixel(x,y,char):
    if 1<x<width-3 and 1<y<height-2:
        pixelBuffer[round(y)*width+round(x)] = char

def projection(x,y,z):
    nx = 2*x/width
    ny = 2*y/height
    nz = (2*z/100)
    px = nx*focalLengh/nz
    py = ny*focalLengh/nz
    return (px+1)*width/2,(py+1)*height/2

while True:
    clear(' ')
    c+=0.01
    
    draw()