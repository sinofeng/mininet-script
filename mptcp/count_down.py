#!/usr/bin/python

import sys, time

for i in range(10):
    # p = "\r%s" % i
    # print p,
    p = "\rWaiting all connection finished, remain time: %ds...." % i
    print p,
    sys.stdout.flush()
    time.sleep(1)
print 'Test complete.'