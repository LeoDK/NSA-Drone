#!/home/leo/.virtualenvs/default/bin/python
# -*- coding:utf-8 -*-

"""
Sélectionner des points sur le rendu vidéo du drone.
"""

import sys
sys.path.append("../")
from autodrone import AutoDrone
import cv2

d = AutoDrone(True, verbosity=AutoDrone.QUIET)
d.connect()
d.enableCam()

cam = d.cam

ix, iy = -1, -1

cont,img = cam.read()

def captMouse(event, x, y, flags, param):
	global ix, iy
	if event == cv2.EVENT_LBUTTONDBLCLK:
		ix, iy = x,y
		print x,y

cv2.namedWindow('image')
cv2.setMouseCallback('image',captMouse)

while cont:
	cont,img = cam.read()
	cv2.circle(img, (ix,iy),5,(0,0,255),-1)
	cv2.imshow('image', img)
	key = cv2.waitKey(1)
	if key & 0xFF == ord('q'):
		cont = False
	elif key & 0xFF == ord('a'):
		print ix, iy

d.inactivate()
