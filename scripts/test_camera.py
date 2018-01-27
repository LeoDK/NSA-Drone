#!/home/leo/.virtualenvs/default/bin/python
# -*- coding:utf-8 -*-

"""
Tester la caméra du drone
"""

import sys
sys.path.append("../")
from autodrone import AutoDrone

d = AutoDrone(False, verbosity=AutoDrone.QUIET)
d.connect()
d.enableCam()

try:
	d.viewCam()
	d.bottomCam()
	d.viewCam()
	d.inactivate()

except KeyboardInterrupt:
	d.inactivate()

except:
	print "error"
