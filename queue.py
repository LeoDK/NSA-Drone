# -*- coding:utf-8 -*-

"""
Pour éviter de surcharger de commandes le drone.
"""

from vector import Vector

class Queue (object):
	"""
	Permet de moduler le flux de commandes à donner au drone, en moyennant les vecteurs déplacement successifs sur plusieurs frames.
	"""

	def __init__(self, drone, cmd_max):
		self.queue = []
		self.processed = []
		self.drone = drone

		self.opposed = {self.drone.forward : self.drone.backward,
				self.drone.backward : self.drone.forward,
				self.drone.left : self.drone.right,
				self.drone.right : self.drone.left,
				self.drone.down : self.drone.up,
				self.drone.up : self.drone.down,
				self.drone.rLeft : self.drone.rRight,
				self.drone.rRight : self.drone.rLeft}
		self.count = 0
		self.cmd_max = cmd_max

	def flush(self):
		"""
		Envoie les commandes intelligemment : somme les vecteurs déplacement pour améliorer la précision des déplacements.
		"""
		#Vecteur représentant le pointage moyen sur plusieurs frames
		sum_vector = Vector(0,0,0)
		for vector in self.queue:
			sum_vector += vector

		sum_vector /= self.count
		self.drone.processVector(sum_vector)
		self.empty()

	def empty(self):
		self.queue = []
		self.count = 0

	def add(self, offset):
		self.queue.append(Vector(offset[0], offset[1], offset[2]))
		self.count+=1

	def check(self):
		if self.count >= self.cmd_max:
			self.flush()
