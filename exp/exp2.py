#!/home/leo/.virtualenvs/default/bin/python
# -*- coding:utf-8 -*-

"""
Comparaison de différents algorithmes de traçage intégrés de base dans OpenCV.
"""

import sys
sys.path.append("../")
import cv2
from autodrone import AutoDrone

def followTarget(cam, tracker):
	cont, frame = cam.read()
	while cont and cv2.waitKey(1) & 0xFF != ord('q'):
		cont, frame = cam.read()
		_, roi = tracker.update(frame)
		cv2.rectangle(frame, (int(roi[0]), int(roi[1])), (int(roi[2]+roi[0]), int(roi[3]+roi[1])), (0,0,255), thickness=7)
		cv2.imshow("Drone camera", frame)

def showCam(cam):
	cont, frame = cam.read()
	while cont and cv2.waitKey(1) & 0xFF != ord(' '):
		cont, frame = cam.read()
		cv2.imshow("Drone camera", frame)

def chooseROI(cam):
	roi = None
	showCam(cam)
	cont, frame = cam.read()
	if cont:
		roi = cv2.selectROI("Selection", frame, True, True)
		cv2.destroyWindow("Selection")
	return frame, roi

#cam = cv2.VideoCapture(0)
d = AutoDrone(True, verbosity=AutoDrone.QUIET)
d.connect()
d.enableCam()
cam = d.cam

trackers = {"MedianFlow":cv2.TrackerMedianFlow_create(), "KCF":cv2.TrackerKCF_create(), "MIL":cv2.TrackerMIL_create(), "TLD":cv2.TrackerTLD_create()}

for t in trackers:
	print "Test pour {}".format(t)
	frame, roi = chooseROI(cam)
	if roi == None:
		raise Exception("Mince...")
	if not trackers[t].init(frame, roi):
		raise Exception("Mince2...")
	followTarget(cam, trackers[t])

cam.release()
