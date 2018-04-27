#!/home/leo/.virtualenvs/default/bin/python
# -*- coding:utf-8 -*-

"""
Test du calcul de distance en Z.
"""

import cv2

def calcZDist(ideal_roi, detected_roi):
    if detected_roi:
        d = ideal_roi[2] / detected_roi[3]
        return d
    return "NONE"

def followTarget(cam, tracker, ideal_roi):
    cont, frame = cam.read()
    while cont and cv2.waitKey(1) & 0xFF != ord('q'):
        cont, frame = cam.read()
        _, roi = tracker.update(frame)
        cv2.rectangle(frame, (int(roi[0]), int(roi[1])), (int(roi[2]+roi[0]), int(roi[3]+roi[1])), (0,0,255), thickness=7)
        cv2.imshow("Drone camera", frame)
        print "d = {} m".format( calcZDist(ideal_roi, roi) )

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


tracker = cv2.TrackerMedianFlow_create()
cam = cv2.VideoCapture(0)

frame, roi = chooseROI(cam)
if roi == None:
    raise Exception("Mince...")
if not tracker.init(frame, roi):
    raise Exception("Mince2...")

followTarget(cam, tracker, roi)
