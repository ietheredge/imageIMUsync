'''
///////////////////////////////////////////////////////////
//  Permission is hereby granted, free of charge,
//  to any person obtaining a copy of
//  this software and associated documentation files
//  (the "Software"), to deal in the Software without
//  restriction, including without limitation the rights
//  to use, copy, modify, merge, publish, distribute,
//  sublicense, and/or sell copies of the Software, and
//  to permit persons to whom the Software is furnished
//  to do so, subject to the following conditions:
//
//  The above copyright notice and this permission notice
//  shall be included in all copies or substantial portions
//  of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
//  ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
//  TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
//  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
//  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
//  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
//  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
//  IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
//  DEALINGS IN THE SOFTWARE.
'''

__author__='Robert Ian'
__version__='0.3.1'

import RPi.GPIO as GPIO
import os
import sys
import softresetNOLEDS as softreset
import time
import camera
import threading
from threading import Thread

'''
try:
    sys.argv[1] == 'test'
    testloop = True
    print 'testing... testing...'
except:
    testloop = False
'''

def txrx(inpin, outpin):
    print "sync attempt"
    GPIO.output(outpin, False)
    while True:
        if GPIO.input(inpin):
            print 'input true'
            if GPIO.output(outpin, True):
                print 'output true too'
                print "synced"
                break
            else:
               GPIO.output(outpin, True)
        else:
            print 'input false'
            if GPIO.output(outpin, False):
                print 'output false too'
                pass
            else:
                print 'set input true'
                GPIO.output(outpin, True)

GPIO.setmode(GPIO.BCM)
triggerGPIO = 23
syncOUT = 24 ##?
syncIN =  25 ##?

# trigger interrupt
GPIO.setup(triggerGPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(syncOUT, GPIO.OUT)
GPIO.setup(syncIN, GPIO.IN)

## set directory
os.chdir('/')

## shutdown switch
down = softreset.App()

## cameras
camera = camera.App()

camera.settings('png', 'h264', '1920x1080', 'sports', 30, 1, 'output%s' %
                str(time.asctime(time.localtime(time.time()))))
camera.signal(10, 0.1)
GPIO.output(syncOUT, True)
while True:
    #print 'in out loop'
    down.main()
    GPIO.wait_for_edge(triggerGPIO, GPIO.FALLING) #wait for triger to enter loop
    time.sleep(2.0)
    GPIO.add_event_detect(triggerGPIO, GPIO.FALLING)
    while True:
        #print 'in in loop'
        if GPIO.event_detected(triggerGPIO):
            GPIO.remove_event_detect(triggerGPIO)
            break
        else:
            # sync pis
            txrx(syncIN, syncOUT)
            try:
                camera.capimage()
                camera.signal(2, 0.2)
                time.sleep(0.2)
            except KeyboardInterrupt:
                print 'keyboard interrup--exiting'
                break
            down.main()
            GPIO.remove_event_detect(syncIN) #
            GPIO.output(syncOUT, True)#



GPIO.cleanup()
exit()
