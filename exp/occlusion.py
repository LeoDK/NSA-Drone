#!/home/leo/.virtualenvs/default/bin/python                                                                                                                                     
# -*- coding:utf-8 -*-                                                                                                                                                          

"""
Tester la robustesse d'un algorithme face à l'occlusion d'objectif.
À lancer avec occlusion.sh
"""

import cv2
from datetime import datetime
import numpy as np

def testOcclusion(cam, tracker, occlusion_t):
    width = int(cam.get(3))
    height = int(cam.get(4))
    cont, frame = cam.read()
    count = 1
    t1 = datetime.now()
    while cont and cv2.waitKey(1) & 0xFF != ord('q'):
        cont, frame = cam.read() 
        t2 = datetime.now()
        if (t2-t1).total_seconds() >= occlusion_t:
            t1 = t2
            frame = np.zeros((height, width, 3), np.uint8)
        _, roi = tracker.update(frame)
        cv2.rectangle(frame, (int(roi[0]), int(roi[1])), (int(roi[2]+roi[0]), int(roi[3]+roi[1])), (0,0,255), thickness=7)
        cv2.imshow("Webcam", frame)
        cv2.imwrite("tmp/Frame {}.jpg".format(str(count)), frame)
        count += 1

def showCam(cam):
    cont, frame = cam.read()
    while cont and cv2.waitKey(1) & 0xFF != ord(' '):
        cont, frame = cam.read()
        cv2.imshow("Webcam", frame)

def chooseROI(cam):
    roi = None
    showCam(cam)
    cont, frame = cam.read()
    if cont:
        roi = cv2.selectROI("Selection", frame, True, True)
        cv2.destroyWindow("Selection")
    return frame, roi


tracker = cv2.TrackerMedianFlow_create()
#tracker = cv2.TrackerMIL_create()
#tracker = cv2.TrackerKCF_create()
#tracker = cv2.TrackerTLD_create()

cam = cv2.VideoCapture(0)

frame, roi = chooseROI(cam)
tracker.init(frame, roi)
testOcclusion(cam, tracker, 1.0)
#testOcclusion(cam, tracker, 0.5)
#testOcclusion(cam, tracker, 0.2)

cam.release()
