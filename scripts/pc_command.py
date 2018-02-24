#!/home/leo/.virtualenvs/default/bin/python
# -*- coding:utf-8 -*-
"""
Contrôler à l'aide du clavier un AR Drone 2.0
"""

import sys
sys.path.append("../")
import pygame
from drone import Drone
from time import sleep

if len(sys.argv) != 2:
    print "Usage : ./pc_command.py [speed]\n[speed] is between 0 and 10, but for a basic test, don't go over 4."
    sys.exit()

d = Drone(False, speed=float(sys.argv[1]))
d.connect()

commands = {pygame.K_z:d.forward, pygame.K_s:d.backward, pygame.K_d:d.right, pygame.K_q:d.left, 
            pygame.K_UP:d.up, pygame.K_DOWN:d.down, pygame.K_LEFT:d.rLeft, pygame.K_RIGHT:d.rRight,
            pygame.K_SPACE:d.takeOff, pygame.K_RETURN:d.land,
            pygame.K_r:d.resetMagnetometer }

print "Commands : \n\
Forward, backward, right, left : zqsd.\n\
Up, down : Directionnal keys up/down.\n\
Rotate right / left : Directionnal keys left, right\n\
Take off : space\n\
Land : enter\n\
Reset magnetometer : r\n\
To quit : escape key."

pygame.init()

window = pygame.display.set_mode((400,400))

cont = True

while cont:

    for event in pygame.event.get():

        if event.type == pygame.KEYDOWN and event.key in commands:
            commands[event.key]()

        elif event.type == pygame.KEYUP and event.key in commands:
            d.stop()

        elif event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            cont = False


    sleep(0.02)

d.inactivate()
pygame.quit()
