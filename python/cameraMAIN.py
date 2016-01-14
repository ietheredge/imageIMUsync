import RPi.GPIO as GPIO
import os
import sys
import softresetNOLEDS as softreset
import time
import camera


try:
    sys.argv[1] == 'test'
    testloop = True
    loop = True
    print 'testing... testing...'
except:
    testloop = False
'''
def pisync(outpin, inpin):
    pass
    diff = outpin - inpin
    if diff > 0:
        return diff
    else:
        return 0
'''
GPIO.setmode(GPIO.BCM)
triggerGPIO = 23
#syncOUT = 24 ##?
#syncIN =  25 ##?

# trigger interrupt
GPIO.setup(triggerGPIO, GPIO.IN)
GPIO.add_event_detect(triggerGPIO, GPIO.BOTH)
#GPIO.setup(syncOUT, GPIO.OUT)
#GPIO.setup(syncIN, GPIO.IN)
## set directory
os.chdir('/')

## shutdown switch
down = softreset.App()

## cameras
camera = camera.App()

camera.settings('png', 'h264', '1920x1080', 'sports', 30, 1, 'output%s' %
                str(time.asctime(time.localtime(time.time()))))
camera.signal(5, 0.5)

while True:
    #delta = pisync(syncOUT, syncIN)
    #time.sleep(delta)
    down.main()
    try:
        GPIO.event_detected(triggerGPIO)
        if testloop:
            camera.signal(5, 0.2)
            time.sleep(1)
            while loop:
                print 'testing loop'
                #delta2 = pisync(syncOUT, syncIN)
                time.sleep(1)
                camera.capimage()
                time.sleep(1)
                camera.capvideo()
                time.sleep(1)
                camera.capraw()
                time.sleep(1)
                camera.signal(5, 0.2)
                time.sleep(1)
                if GPIO.event_detected(triggerGPIO):
                    loop = False
                    break
                else:
                    print 'continuing'
                    continue
        else:
            camera.capimage()
    except KeyboardInterrupt:
        print 'keyboard interrupt... exiting'
        break
    else:
        pass

GPIO.cleanup()
exit()
