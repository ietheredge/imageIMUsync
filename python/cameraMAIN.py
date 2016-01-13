import RPi.GPIO as GPIO
import os
import sys
import softresetClient as softreset
import time
import camera


if sys.argv[1] == 'test':
    testloop = True
    print 'testing... testing...'
else:
    testloop = False

def pisync(outpin, inpin):
    pass
    diff = outpin - inpin
    if diff > 0:
        return diff
    else:
        return 0

GPIO.setmode(GPIO.BCM)
triggerGPIO = 23
syncOUT = 24 ##?
syncIN =  25 ##?
GPIO.setup(triggerGPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP) # trigger interrupt
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
camera.signal(7, 0.2)

while True:
    delta = pisync(syncOUT, syncIN)
    time.sleep(delta)
    down.main()
    try:
        GPIO.wait_for_edge(triggerGPIO, GPIO.FALLING)
        if testloop:
            inloop = True
            while inloop:
                delta2 = pisync(syncOUT, syncIN)
                time.sleep(delta2)
                camera.capimage()
                camera.capvideo()
                camera.capraw()
                time.sleep(1)
                try:
                    GPIO.wait_for_edge(triggerGPIO, GPIO.FALLING)
                    inloop = False
                except KeyboardInterrupt:
                    print 'keyboard interrupt... exiting'
                    break
        else:
            camera.capimage()
    except KeyboardInterrupt:
        print 'keyboard interrupt... exiting'
        break
    else:
        pass

GPIO.cleanup()
exit()
