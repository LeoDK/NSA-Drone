# -*- coding:utf-8 -*-

from abc import ABCMeta, abstractmethod
from datetime import datetime
import cv2
from threading import Thread
from queue import Queue
import numpy as np
from drone import Drone
from copy import deepcopy
from vector import Vector
from pid import PID

################################################################################################################
###################################        Objet drone qui bouge tout seul     #################################
################################################################################################################

class AutoDrone (Drone, Thread):
    """
    AR Drone 2.0 qui suit une cible à l'aide de la caméra avant.
    Classe abstraite.
    """

    __metaclass__ = ABCMeta

    CAM_RES = (640,360)
    VID_PORT = 5555

    # Frames per cmd -> combien de frames on attend pour envoyer une commande
    DEF_FPC = 3

    DEF_MIN_SPEED = 0.2
    DEF_MAX_SPEED = 2

    # La distance initiale de la caméra du drone à la cible, en m
    DEF_INITIAL_D = 1

    # Contrôleur proportionnel
    KP_X = 1
    KP_Y = 1
    KP_Z = 0.5

    # Contrôleur intégral
    KI_X = 0.1
    KI_Y = 0.1
    KI_Z = 0.2

    # Contrôleur dérivée
    KD_X = 0.2
    KD_Y = 0.2
    KD_Z = 0.3

    def __init__(self, stopped, min_speed=DEF_MIN_SPEED, max_speed=DEF_MAX_SPEED, verbosity=Drone.QUIET, fpc=DEF_FPC, initial_d=DEF_INITIAL_D):
        """
        [stopped] -> cf Drone.
        [min_speed] et [max_speed] -> Les vitesses min et max que l'on peut avoir en donnant des ordres au drone (selon le drone).
        [verbosity] -> cf Drone.
        [fpc] -> Le nombre d'images que l'on attend avant d'envoyer une commande (règle la précision et la réactivité).
        [initial_d] -> La distance initiale entre la cible et le drone lors de sa sélection (pour se déplacer en avant et en arrière).
        [mode] -> Selon si l'on choisit nous-même la zone d'image à suivre ou si le drone le fait automatiquement.
        """
        Drone.__init__(self, stopped, max_speed, verbosity)
        Thread.__init__(self)
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.tracking = False
        self.queue = Queue(self, fpc)
        self.frontCam()
        self.initial_d = initial_d
        self._autoMove_last_t = datetime.now()
        # Contrôleur PID
        self.pid_x = PID(kp=AutoDrone.KP_X, ki=AutoDrone.KI_X, kd=AutoDrone.KD_X)
        self.pid_y = PID(kp=AutoDrone.KP_Y, ki=AutoDrone.KI_Y, kd=AutoDrone.KD_Y)
        self.pid_z = PID(kp=AutoDrone.KP_Z, ki=AutoDrone.KI_Z, kd=AutoDrone.KD_Z)

    ################################################################################################################
    ################################################        Vidéo         ##########################################
    ################################################################################################################

    def bottomCam(self):
        """
        Demande au drone de laisser sur le port vidéo le flux de la caméra du bas.
        """
        self.config("video:video_channel", "1")
        print "Choice : bottom camera"

    def frontCam(self):
        """
        Demande au drone de laisser sur le port vidéo le flux de la caméra du haut.
        """
        self.config("video:video_channel", "0")
        print "Choice : front camera"

    def enableCam(self):
        """
        Tenter de récupérer le flux sur le port vidéo.
        """
        self.cam = cv2.VideoCapture( 'tcp://{0}:{1}'.format(Drone.IP, AutoDrone.VID_PORT) )
        if not self.cam.isOpened():
            print "Drone camera not reachable"
            return False
        print "Drone camera OK"
        return True

    def releaseCam(self):
        self.cam.release()

    def viewCam(self):
        """
        Regarder le stream video en temps réel.
        """
        cont, frame = self.cam.read()

        while cont:
            cv2.imshow('cam', frame)
            cont, frame = self.cam.read()
            if (cv2.waitKey(1) & 0xFF) == ord('q'):
                cont = False
        cv2.destroyAllWindows()

    ################################################################################################################
    ##########################################        Déplacement autonome        ##################################
    ################################################################################################################

    def autoMove(self, roi):
        """
        [roi] est la zone de l'image où se situe l'objet à suivre.
        Extrapôle le décalage en x,y,z par rapport à la position idéale, et la fournit à la file d'attente.
        Les vitesses en x,y,z sont régulées grâce à un contrôleur PID.
        """
        mid_x = roi[0] + 0.5*roi[2]
        mid_y = roi[1] + 0.5*roi[3]

        # Prélèvement du temps
        t = datetime.now()
        delta_t = (t - self._autoMove_last_t).total_seconds()
        self._autoMove_last_t = t

        error_x = mid_x - self.ideal_center[0]
        error_y = self.ideal_center[1] - mid_y

        # Pour x et y, c'est simple : on regarde l'éloignement par rapport au centre de la frame et on y applique un correcteur PID
        x_speed = self.pid_x.getOrder(error_x, delta_t) / AutoDrone.CAM_RES[0]
        y_speed = self.pid_y.getOrder(error_y, delta_t) / AutoDrone.CAM_RES[1]

        # Pour z, -> cf doc. (formule de trigo). On fait la moyenne des quotients sur x et sur y.
        z_speed = 0
        if roi[2] != 0 and roi[3] != 0:
            d = self.initial_d * ( self.ideal_target[2] / roi[2] + self.ideal_target[3] / roi[3] )/2
            error_z = d - self.initial_d
            z_speed = -1*self.pid_z.getOrder(error_z, delta_t)

        verif = lambda x : x if -1 < x < 1 else (1.0 if x>0 else -1.0)
        x_speed,y_speed,z_speed = map(verif, (x_speed, y_speed, z_speed))

        self.queue.add((x_speed,y_speed,z_speed))
        self.queue.check()

    def processVector(self, vector):
        print "{} {} {}".format(vector.x, vector.y, vector.z)
        self.move(False, 0, vector.z, vector.y, vector.x)
        # DBG
        #self.move(False, 0, vector.z, 0, vector.x)

    @abstractmethod
    def initROI(self):
        pass

    def showGUI(self, frame, roi):
        """
        Par défaut, on affiche la zone détectée.
        """
        frame_copy = deepcopy(frame)
        cv2.rectangle(frame_copy, (int(roi[0]), int(roi[1])), (int(roi[2]+roi[0]), int(roi[3]+roi[1])), (0,0,255), thickness=7)
        cv2.rectangle(    frame_copy,
                (self.ideal_target[0], self.ideal_target[1]),
                (self.ideal_target[0]+self.ideal_target[2], self.ideal_target[1]+self.ideal_target[3]),
                (0,255,0), thickness=7    )
        cv2.imshow("Drone camera", frame_copy)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.tracking= False

    def run(self):
        """
        Globalement, ce que fait la fonction:
        /////// Initialisation ///////
         + on choisit la zone d'image (ROI en anglais) manuellement ou automatiquement, qui sera la zone à suivre pendant la suite. (1)
         + on définit à partir de la ROI choisie la cible parfaite (dimensions initialies et située au centre de l'écran). (2)
         + on suit la cible à l'aide d'un algorithme de traçage, appelé MedianFlow. (3)
        /////// En boucle ///////
         + on récupère la position de l'objet à traçer, puis on la compare à la position idéale et on bouge en fonction. (4)
         + on vérifie qu'il n'y ait pas trop de latence, sinon on supprime les commandes trop anciennes.(5)
        """
        if hasattr(self, 'cam'):
            self.releaseCam()
        self.tracking = self.enableCam()

        #1
        roi = self.initROI()
        cont, frame = self.cam.read()

        #2
        self.ideal_target = (int( (AutoDrone.CAM_RES[0]-roi[2])/2 ), int( (AutoDrone.CAM_RES[1]-roi[3])/2 ), int(roi[2]), int(roi[3]))
        self.ideal_center = (self.ideal_target[0] + self.ideal_target[2]/2, self.ideal_target[1] + self.ideal_target[3]/2)
        self.ideal_area = self.ideal_target[2]*self.ideal_target[3]

        #3
        tracker = cv2.TrackerMedianFlow_create()
        if self.tracking:
            self.tracking = tracker.init(frame, roi)

        while self.tracking:
            check_time = datetime.now()
            #4
            self.autoMove(roi)

            self.showGUI(frame, roi)

            _, roi = tracker.update(frame)
            if self.tracking:
                self.tracking, frame = self.cam.read()

            #5
            latency = (datetime.now() - check_time).total_seconds()
            if latency >= 1.0:
                self.queue.empty()
                print "WARNING : REALLY TOO SLOW!!!"
            if latency >= 0.2:
                print "WARNING : high latency : {} s.".format(latency)


    def inactivate(self):
        self.tracking = False
        Drone.inactivate(self)
        self.releaseCam()

class EmbeddedAutoDrone (AutoDrone):
    """
    Contrôler automatiquement un AR Drone 2.0 à l'aide sur un système embarqué (raspberry pi).
    """

    D_TARGET_SIZE = (260,100)

    def showGUI(self, frame, roi):
        pass

    def initROI(self):
        return( AutoDrone.CAM_RES[0]-EmbeddedAutoDrone.D_TARGET_SIZE[0],
            AutoDrone.CAM_RES[1]-EmbeddedAutoDrone.D_TARGET_SIZE[1],
            EmbeddedAutoDrone.D_TARGET_SIZE[0],
            EmbeddedAutoDrone.D_TARGET_SIZE[1] )


class PCAutoDrone (AutoDrone):
    """
    Contrôler automatiquement un AR Drone 2.0 depuis un PC sous Linux.
    """

    def initROI(self):
        cont, frame = self.cam.read()
        while cont and cv2.waitKey(1) & 0xFF != ord(' '):
            cv2.imshow("Drone camera", frame)
            cont, frame = self.cam.read()

        roi = cv2.selectROI("Selection", frame, True, True)
        cv2.destroyWindow("Selection")
        return roi

    def run(self):
        AutoDrone.run(self)
        cv2.destroyAllWindows()
