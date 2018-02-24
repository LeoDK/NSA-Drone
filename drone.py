# -*- coding:utf-8 -*- 

"""
Contrôler un AR Drone 2.0 par wifi.
"""

import socket
from threading import Thread
import struct
import sys
from time import sleep
from vector import Vector

class DroneTimer (Thread):
    """
    Utilisé par l'objet Drone pour garder la connexion.
    """
    
    def __init__(self, func, t):
        super(DroneTimer, self).__init__()

        self.func = func
        self.t = t
        self.cont = True

    def setTime(self, t):
        self.t = t

    def run(self):
        while self.cont:
            self.func()
            sleep(self.t)

    def stop(self):
        self.cont = False

class Drone (object):
    """ 
    Objet qui permet de contrôler l'ar drone 2.0.
    Effectue seulement les opérations de bas niveau (déplacement basique).
    """

    # Réseaux
    IP = '192.168.1.1'
    CMD_PORT = 5556

    # Verbosité
    QUIET=0
    VERBOSE=1

    # Intervalle de temps entre chaque paquet "watchdog", pour garder la connexion établie
    WD_TIME = 0.15

    # Vitesses relatives selon chaque mouvement, à adapter selon son drone (entre 0 et 1)
    SPEEDS = {"LEFT":1, "RIGHT":1, "RLEFT":1, "RRIGHT":0.75,
        "UP":0.5, "DOWN":0.5, "BACKWARD":0.25, "FORWARD":0.25}

    DEF_SPEED=2

    def __init__(self, stopped, speed=DEF_SPEED, verbosity=VERBOSE):
        """
        [stopped] -> Si le drone est en l'air ou au sol quand on s'y connecte.
        [speed] -> Sans unité, entre 0 (minimum) et 10 (maximum)
        [verbosity] -> VERBOSE : précise chaque paquet envoyé. QUIET : ne précise que les étapes principales de connexion.
        """
        # Numéro de séquence envoyé dans chaque paquet
        self.seq_nbr = 1
        self.stopped = stopped
        self.speed = speed
        self.wd = DroneTimer(self.keepAlive, Drone.WD_TIME)
        self.wd.daemon = True
        self.verbosity = verbosity
        self.cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    @staticmethod
    def i3e724(f):
        """
        Convertit un float en notation IEEE-724
        """
        string_rep = struct.pack('f', f)
        int_rep = struct.unpack('i', string_rep)[0]
        return int_rep

    ################################################################################################################
    #######################################        Commandes générales     #########################################
    ################################################################################################################

    def command(self, cmd_type, *args):
        """
        Cette fonction s'occupe de former des commandes généralistes et de les envoyer au drone.
        En ascii, une commande parrot AR se décompose de la manière suivante: AT*(operation)=(num de seq),(arguments pour l'opération)\r. (point non inclus)
        """
        cmd_args = ''
        for a in args:
            cmd_args += ','
            cmd_args += str(a)

        cmd = "AT*" + cmd_type + "=" + str(self.seq_nbr) + cmd_args + "\r"

        self.cmd_sock.sendto(cmd, (Drone.IP, Drone.CMD_PORT))

        if self.verbosity == Drone.VERBOSE:
            print "Sent : {}".format(cmd)

        self.seq_nbr += 1

    def move(self, stand, lr, fb, ud, ar):
        """
        Commandes pour bouger :
        lr : left/right(-/+) 
        fb : forward/backward(-/+)
        ud : up/down(+/-)
        ar : rotate_left/rotate_right(-/+) 
        """
        move = 0 if stand else 1
        lr, fb, ud, ar = map( Drone.i3e724, (float(lr), float(fb), float(ud), float(ar)) )
        self.command("PCMD", move, lr, fb, ud, ar)
        self.stopped = False

    def sysSignal(self, cmd):
        """
        Commandes pour : décoller, atterir, urgence (arrêt des moteurs)
        """
        self.command("REF", cmd)

    def config(self, arg, value):
        """
        Commandes pour configurer le drone (type de naviguation, caméra utilisée, etc...)
        """
        self.command("CONFIG", "\"{}\"".format(arg), "\"{}\"".format(value))

    def calib(self, arg):
        self.command("CALIB", arg)

    ################################################################################################################
    #######################################        Opés précises     ###############################################
    ################################################################################################################

    def land(self):
        self.sysSignal("290717696")
        self.stopped = True

    @staticmethod
    def spoofedLand(src_ip, ip=IP):
        """
        Si le but est simplement de faire aterrir le drone, alors au lieu de couper la connexion et d'en prendre le contrôle,
        on peut juste utiliser cette fonction (beaucoup plus rapide)
        """
        #On envoie un numéro de séq suuuuper grand... et c'est tout!!!
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto('AT*REF=1000000,290717696\r', (ip, Drone.CMD_PORT))

    def takeOff(self):
        self.seq_nbr = 1
        self.sysSignal("290718208")

    def emergencyStop(self):
        self.seq_nbr = 1
        self.sysSignal("290717952")
        self.sysSignal("290717696")

    def resetMagnetometer(self):
        self.calib("0")

    def connect(self):
        self.config("general:navdata_demo", "TRUE")
        self.wd.start()

    def keepAlive(self):
        self.command("COMWDG")

    def left(self, coef=SPEEDS["LEFT"]):
        self.move(False, -self.speed*coef, 0, 0, 0)

    def right(self, coef=SPEEDS["RIGHT"]):
        self.move(False, self.speed*coef, 0, 0, 0)

    def forward(self, coef=SPEEDS["FORWARD"]):
        self.move(False, 0, -self.speed*coef, 0, 0)

    def backward(self, coef=SPEEDS["BACKWARD"]):
        self.move(False, 0, self.speed*coef, 0, 0)

    def up(self, coef=SPEEDS["UP"]):
        self.move(False, 0, 0, self.speed*coef, 0)

    def down(self, coef=SPEEDS["DOWN"]):
        self.move(False, 0, 0, -self.speed*coef, 0)

    def rLeft(self, coef=SPEEDS["RLEFT"]):
        self.move(False, 0, 0, 0, -self.speed*coef)

    def rRight(self, coef=SPEEDS["RRIGHT"]):
        self.move(False, 0, 0, 0, self.speed*coef)

    def stop(self):
        self.move(True, 0, 0, 0, 0) 
        self.stopped = True

    def inactivate(self):
        """
        Toujours appeler cette fonction à la fin
        """
        #self.cmd_sock.close()
        self.stop()
        self.wd.stop()

    ################################################################################################################
    ################################  Commandes à l'aide d'un vecteur déplacement ##################################
    ################################################################################################################

    def processVector(self, vector):
        """
        Déplace le drone à l'aide d'un vecteur 3D t.q. :
            - gauche/droite -> axe X
            - haut/bas -> axe Y
            - devant/derrière -> axe Z
        La norme de ces vecteurs est entre 0 et 1 inclus (1 étant le max et 0 le min)
        """
        self.move(False, vector.x, vector.z, vector.y, 0)
