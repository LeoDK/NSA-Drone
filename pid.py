# -*- coding:utf-8 -*-

class PID (object):

    """
    Contrôleur Proportionnel - Intégral - Dérivée.
    """

    DEF_KP = 3
    DEF_KI = 0.8
    DEF_KD = 0.1

    def __init__(self, kp=DEF_KP, ki=DEF_KI, kd=DEF_KD):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.last_integral_error = 0
        self.integral_error = 0
        self.last_derivative_error = 0

    def proportionnal(self, error):
        return error

    def integral(self, error, delta_t):
        # Méthode d'approximation des trapèzes
        self.integral_error += (error - self.last_integral_error) * delta_t * 0.5 + self.last_integral_error * delta_t
        self.last_integral_error = error
        return self.integral_error

    def derivative(self, error, delta_t):
        ret = (error - self.last_derivative_error) / delta_t
        self.last_derivative_error = error
        return ret

    def getOrder(self, error, delta_t):
        """
        Retourne la consigne calculée.
        """
        return self.proportionnal(error)*self.kp + self.integral(error, delta_t)*self.ki + self.derivative(error, delta_t)*self.kd
