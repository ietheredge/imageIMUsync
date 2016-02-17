import RTIMU
import picamera, checkbattery, checkdisk, whereisthesun
import os
import math
import logging
import datetime
import time


switchGPIO = 24
triggerGPIO = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(triggerGPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(switchGPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

stacksize = 100 #number of images to grab in each stack
lat = "27:36:20.80:N" #approximate lattitude, you could have a gps output this directly, but this project is aimed for underwater use (no GPS)
lon = "95:45:20.00:W" #approximate longitude
memthreshold = 2000 #memmory threshold, in kbs

## initialize imu data be sure to calibrate properly before using this for data collection (see: github.com/Richards-Tech/RTIMULib)
SETTINGS_FILE = "../../RTIMULib/Linux/python/tests/RTIMULib"
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

## initialize camera, battery check, disk check and sun data
camera = picamera.PiCamera()
battery = checkbattery.App()
sun = whereisthesun.App(lat, lon)
disk = checkdisk.App()


availmem, usedmem, totatl = disk.checkds(memthreshold) # check that there is enough disk space, compress data if space is low
if battery.check(): # check battery level
    pass
# use IMU data to determine orientation relative to sun and send signal to indicator LEDS
#print sunalt
#print sunaz
while True:
    try:
        GPIO.wait_for_edge(triggerGPIO, GPIO.FALLING)
        print "\nFalling edge detected. Now your program can continue with"
        print "whatever was waiting for a button press."

        if GPIO.input(switchGPIO):
            for i in range (1,stacksize): # record data
                if imu.IMURead(): # read from calibrated IMU
                    data = imu.getIMUData()
                    intosun, awayfromsun, horizontal, sunalt, sunaz = sun.checkkeyaxes(data)
                    sun.callleds(intosun, awayfromsun, horizontal)
                    (data["pressureValid"], data["pressure"], data["temperatureValid"], data["temperature"]) = temp.pressureRead()
                    fusionPose = data["fusionPose"]
                    # record image/RAW with time, imu data, sun heading, and solar angle data as name
                    camera.capture('../data/'+str(datetime.datetime.now().strftime('%H-%M-%S-%f'))+str("_%f" % data["temperature"])+str("_%f_%f_%f_%s_%f_%f" % (math.degrees(fusionPose[0]), math.degrees(fusionPose[1]),
                                                    math.degrees(fusionPose[2]), ('I' if intosun==True else 'A' if awayfromsun==True else 'P'), sunalt, sunaz))+'.jpg' , format='jpeg', bayer=True)
        else:
            if imu.IMURead(): # read from calibrated IMU
                data = imu.getIMUData()
                intosun, awayfromsun, horizontal, sunalt, sunaz = sun.checkkeyaxes(data)
                sun.callleds(intosun, awayfromsun, horizontal)
                (data["pressureValid"], data["pressure"], data["temperatureValid"], data["temperature"]) = temp.pressureRead()
                fusionPose = data["fusionPose"]
                
                # record image/RAW with time, imu data, sun heading, and solar angle data as name
                camera.start_recording('../data/'+str(datetime.datetime.now().strftime('%H-%M-%S-%f'))+str("_%f" % data["temperature"])+str("_%f_%f_%f_%s_%f_%f" % (math.degrees(fusionPose[0]), math.degrees(fusionPose[1]),
                                                math.degrees(fusionPose[2]), ('I' if intosun==True else 'A' if awayfromsun==True else 'P'), sunalt, sunaz))+'.h264')
    else:
        time.sleep(poll_interval*1.0/1000.0)
        sun.clearleds()
    except KeyboardInterrupt:
        GPIO.cleanup()       # clean up GPIO on CTRL+C exit


GPIO.cleanup()
