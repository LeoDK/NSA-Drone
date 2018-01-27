#!/home/leo/.virtualenvs/default/bin/python
# -*- coding:utf-8 -*-

"""
Script à lancer en cas d'urgence.
"""

import sys
sys.path.append("../")
from drone import Drone
Drone.spoofedLand('192.168.1.3')
