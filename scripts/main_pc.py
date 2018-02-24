#!/home/leo/.virtualenvs/default/bin/python
# -*- coding:utf-8 -*-

import sys
sys.path.append("../")
from autodrone import PCAutoDrone
from time import sleep

d = PCAutoDrone(False, min_speed=0.5, max_speed=2, verbosity=PCAutoDrone.QUIET)
d.connect()

try:
    print "starting auto detection"
    d.start()
    sleep(5)
    if len(sys.argv) == 2 and sys.argv[1] == '--dbg':
        print "Debug mode"
    else:
        print "Taking off!!!"
        d.takeOff()
        sleep(4)
        d.up()
        sleep(0.5)
        d.stop()
    while d.is_alive():
        sleep(0.5)
    d.land()

except KeyboardInterrupt:
    d.land()
    d.inactivate()
    print "DONE"

except Exception as e:
    d.land()
    d.inactivate()
    print "Error while launching autonomous drone"
    print e
