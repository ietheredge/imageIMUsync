import RTIMU
import picamera, checkbattery, checkdisk, whereisthesun
import os
import math
import logging
import datetime
import time
import RPi.GPIO as GPIO
import io
import sys
from compoundpi.client import CompoundPiClient

# waitfor pi function
def waitforpisignal(GPIOPINNo, wait):
    while wait:
        print 'waiting'
        if GPIO.input(GPIOPINNo):
            print' waiting'
	    pass
        else:
            wait = False
            print 'message recieved'

## variables defined
wait = True
triggerGPIO = 23
pi2piGPIO = 24
network = '128.83.0.0/16' #IP range for pis connected to network
stacksize = 10 #number of images to grab in each stack
lat = "27:36:20.80:N" #approximate lattitude, you could have a gps output this directly, but this project is aimed for underwater use (no GPS)
lon = "95:45:20.00:W" #approximate longitude
memthreshold = 2000 #memmory threshold, in kbs

##trigger and switch inputs
GPIO.setmode(GPIO.BCM)
GPIO.setup(triggerGPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP) # interrupt
GPIO.setup(pi2piGPIO, GPIO.IN) # switch

## set environment and wait for pi2 to come online
os.chdir('/')
waitforpisignal(pi2piGPIO, wait)

## data log
datlog = logging.getLogger('IMUlog')
hdlr = logging.FileHandler('home/pi/imageIMUSync/log/IMUlog.log')
formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s', "%H-%M-%S-%f")
hdlr.setFormatter(formatter)
datlog.addHandler(hdlr)
datlog.setLevel(logging.INFO)
print 'log'
'''
## imu set up, be sure to calibrate properly before using this for data collection (see: github.com/Richards-Tech/RTIMULib)
SETTINGS_FILE = "home/pi/RTIMULib/Linux/python/tests/RTIMULib"
s = RTIMU.Settings(SETTINGS_FILE)
if not os.path.exists(SETTINGS_FILE + ".ini"):
    print('Settings file does not exist, will be created')
imu = RTIMU.RTIMU(s)
temp = RTIMU.RTPressure(s)
if (not imu.IMUInit()):
    exit()
else:
    pass
imu.setSlerpPower(0.02) # set weighting of predicted vs. measured states
imu.setGyroEnable(True)
imu.setAccelEnable(True)
imu.setCompassEnable(True)
poll_interval = imu.IMUGetPollInterval()
'''
print 'imu'
## cameras
print 'cameras'
cameraclient = CompoundPiClient()
cameraclient.servers.network = network
cameraclient.servers.find() #should return 2 cameras
cameraclient.resolution(1920, 1080)
cameraclient.agc('auto')
cameraclient.awb('off', 1.5, 1.3)
cameraclient.iso(100)
cameraclient.metering('spot')
cameraclient.brightness(50)
cameraclient.contrast(0)
cameraclient.saturation(0)
cameraclient.denoise(False)
cameraclient.identify() #simultaneous blinking camera lights = ready to go
responses = cameraclient.status()
min_time = min(status.timestamp for status in responses.values())
for address, status in responses.items():
        if (status.timestamp - min_time).total_seconds() > 0.3:
            print('Warning: time on %s deviates from minimum '
                'by >0.1 seconds' % address)



## disk check and sun data
print 'extras'
sun = whereisthesun.App(lat, lon)
disk = checkdisk.App()
# check that there is enough disk space, compress data if space is low
# use IMU data to determine orientation relative to sun and send signal to indicator LEDS
#print sunalt
#print sunaz


while True:
    print 'loop'
    #availmem, usedmem, totatl = disk.checkds(memthreshold)
    try:
        GPIO.wait_for_edge(triggerGPIO, GPIO.FALLING)
        cameraclient.capture(5, delay=0.25) #record synchronized image stack
        #cameraclient.record(10, format=u'h264', delay=0.5) #record synchronized video
        data = imu.getIMUData()
        intosun, awayfromsun, horizontal, sunalt, sunaz = sun.checkkeyaxes(data)
        sun.callleds(intosun, awayfromsun, horizontal)
        (data["pressureValid"], data["pressure"], data["temperatureValid"], data["temperature"]) = temp.pressureRead()
        fusionPose = data["fusionPose"]
        datlog.info("r: %f p: %f y: %f quadrant: %s solarangle: %f, %f" % (math.degrees(fusionPose[0]), math.degrees(fusionPose[1]),
                                        math.degrees(fusionPose[2]), ('into sun' if intosun==True else 'away from sun' if awayfromsun==True else 'perpendicular to sun'), sunalt, sunaz))
        print cameraclient.status().items()
        time.sleep(poll_interval*1.0/1000.0)


        try:
            for addr, files in cameraclient.list().items():
                for f in files:
                    assert f.filetype == 'IMAGE'
                    print f
                    print addr
                    print f.timestamp
                    with io.open('%s_%s.jpg' % (addr,f.timestamp), 'wb') as output: #need to change timestamp format (currently includes spaces/not scp-usable)
                        cameraclient.download(addr, f.index, output)
        finally:
            cameraclient.clear()
    except KeyboardInterrupt:
        cameraclient.clear()
        cameraclient.close()
        GPIO.cleanup()       # clean up GPIO on CTRL+C exit
        break

cameraclient.close()
GPIO.cleanup()
exit()
