# -*- coding:utf-8 -*-

from math import sqrt, cos, sin, asin, atan, pi

class Vector (object):

        '''
	Classe modélisant un vecteur du plan.
        '''

        #Précision : 10 décimales après le 0
        DEC_PRECISION = 10

        def __init__(self, *args):
                self.refresh(*args)
                #L'unité S.I.
                self.unit = "(no unit)"

	def refresh(self, *args):
		''' Actualise un vecteur. args contient soit les composantes en x, y et z, soit la norme, la dir. et le sens '''

		try:
			#Composantes
			self.x = float(args[0])
			self.y = float(args[1])
			self.z = float(args[2])

			#Norme
			self.val = sqrt(self.x**2 + self.y**2 + self.z**2)

			#Direction (angles de Y et Z par rapport à l'axe X)
			self.dir_rad = [ abs(atan(self.z/self.x)), abs(asin(self.z/self.val)) ]
			self.dir_deg = map(Vector.radToDeg, self.dir_rad)

			#Sens
			sign = lambda b : False if b<0 else True
			self.sense = ( sign(self.x), sign(self.y), sign(self.z) )

			#Arrondi
			values = (self.x, self.y, self.val, self.dir_deg[0], self.dir_deg[1], self.dir_rad[0], self.dir_rad[1])
			values = tuple( round(value, Vector.DEC_PRECISION) for value in values )
			self.x, self.y, self.val, self.dir_deg[0], self.dir_deg[1], self.dir_rad[0], self.dir_rad[1] = values 

                except (ZeroDivisionError, TypeError):
                        self.x = 0
                        self.y = 0
			self.z = 0
                        self.val = 0
                        self.dir_deg = None
                        self.dir_rad = None
                        self.sense = None

	#---------------------------------------------------------------------------------------------------------------------------------------#
	#							Surcharge d'opérateur								#
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

	#---------------------------------------------------------------------------------------------------------------------------------------#
	#							Calculs "généraux"								#
	#---------------------------------------------------------------------------------------------------------------------------------------#
 
        @staticmethod
        def degToRad(deg):
                return deg*pi/180

        @staticmethod
        def radToDeg(rad):
                return 180*rad/pi
