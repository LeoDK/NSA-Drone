# -*- coding:utf-8 -*-

from math import sqrt

class Vector (object):

    '''
    Classe modélisant un vecteur du plan.
    '''

    #Précision : 10 décimales après le 0
    DEC_PRECISION = 10

    def __init__(self, x, y, z):
        self.refresh(x, y, z)
        #L'unité S.I.
        self.unit = "(no unit)"

    def refresh(self, x, y, z):
        '''
        Actualiser un vecteur à partir de ses composantes.
        '''

        try:
            #Composantes
            self.x = x
            self.y = y
            self.z = z

            #Norme
            self.val = sqrt(self.x**2 + self.y**2 + self.z**2)

            #Arrondi
            values = (self.x, self.y, self.z, self.val)
            values = tuple( round(value, Vector.DEC_PRECISION) for value in values )
            self.x, self.y, self.z, self.val = values

        #Vecteur nul
        except (ZeroDivisionError, TypeError):
            self.x = 0
            self.y = 0
            self.z = 0
            self.val = 0

    #---------------------------------------------------------------------------------------------------------------------------------------#
    #                                                      Surcharge d'opérateur                                                            #
    #---------------------------------------------------------------------------------------------------------------------------------------#

    def __add__(self, vect):
        x = self.x + vect.x
        y = self.y + vect.y
        z = self.z + vect.z
        return Vector(x,y,z)

    def __sub__(self, vect):
        ''' Soustraction de deux vecteurs '''
        return self.__add__(-1*vect)

    def __mul__(self, num):
        ''' Produit d'un vecteur avec un nombre '''
        x = self.x*num
        y = self.y*num
        z = self.z*num
        return Vector(x,y,z)

    def __rmul__(self, num):
        ''' Pareil que __mul__ '''
        return self.__mul__(num)

    def __div__(self, num):
        ''' Division d'un vecteur par un nombre '''
        return self.__mul__(1.0/num)

    def __rdiv__(self, num):
        return self.__div__(num)
