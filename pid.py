# -*- coding:utf-8 -*-

class PID (object):

    """
    Contrôleur Proportionnel - Intégral - Dérivée.
    """

    DEF_KP = 3
    DEF_KI = 0.05
    DEF_KD = 1

    def __init__(self, kp=DEF_KP, ki=DEF_KI, kd=DEF_KD):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral.last_error = 0
        self.derivative.last_error = 0
        self.error_area = 0

    def proportionnal(self, error):
        return error

    def integral(self, error, delta_t):
        # Méthode d'approximation des trapèzes
        self.area_error += (error - self.integral.last_error) * delta_t + self.integral.last_error * delta_t
        self.integral.last_error = error
        return self.area_error

    def derivative(self, error, delta_t):
        ret = (error - self.derivative.last_error) / delta_t
        self.derivative.last_error = error
        return ret

    def getOrder(self, error, delta_t):
        """
        Retourne la consigne calculée.
        """
        return self.proportionnal(error)*self.kp + self.integral(error, delta_t)*self.ki + self.derivative(error, delta_t)*self.kd
