import sys, getopt
import os
import spidev
import RTIMU
import os.path
import time
import math
import RPi.GPIO as GPIO
import ephem
sys.path.append('.')


#ephem functions
def converttodecimal(lat, lon):
    ltdeg, ltmin, ltsec, lthem = lat.split(":")
    lndeg, lnmin, lnsec, lnhem = lon.split(":")
    latitudeD = (1 if lthem=="N" else -1)*(float(ltdeg)+(float(ltmin)/60)+
    (float(ltsec)/3600))
    longitudeD = (1 if lnhem=="E" else -1)*(float(lndeg)+(float(lnmin)/60)+
    (float(lnsec)/3600))
    return latitudeD, longitudeD
def checkaxes(sun=ephem.Sun(rig), imuroll, imupitch, imuyawintsp, itsp, afsp, hp, precision=22.5):
    ## this function is not very pythonic, can be improved upon greatly....
    sunalt = str(sun.alt)
    sunaz = str(sun.az)
    altdeg, altmin, altsec = sunalt.split(":")
    azdeg, azmin, azsec = sunaz.split(":")
    azimuth = float(azdeg)+(float(azmin)/60)+(float(azsec)/3600)
    altitude = float(altdeg)+(float(altmin)/60)+(float(altsec)/3600)
    its = (True if (azimuth-precision)<=imuyaw<=(azimuth+precision) else False)
    afs = (True if ((azimuth-precision)+180)<=imuyaw<=((azimuth+precision)+180)
        or ((azimuth-precision)-180)<=imuyaw<=
        ((azimuth+precision)-180) else False)
    h = (True if (-1*precision)<=imuroll<=precision and (-1*precision)<=
        imupitch<=precision else False)
    if its:
        GPIO.output(itsp, GPIO.HIGH)
    if afs:
        GPIO.output(afsp, GPIO.HIGH)
    if h:
        GPIO.output(hp, GPIO.HIGH)
    if not its:
        GPIO.output(itsp, GPIO.LOW)
    if not afs:
        GPIO.output(afsp, GPIO.LOW)
    if not h:
        GPIO.output(hp, GPIO.LOW)
    return sunalt, sunaz
## SPI / depth sensor functions
def ReadChannel(channel):
    adc = spi.xfer2([1,(8+channel)<<4,0]) #<<X is 2**X
    data = ((adc[1]&3) << 8) + adc[2]
    return data
def ConvertVolts(data,places=4):
    volts = (data * 5.0) / float(1023)
    volts = round(volts,places)
    return volts
def get_depthMeters(Vout):
    return ((((Vout/5)-0.04)/0.000901)-(1.01*(10**5)))/(1029*9.8)

#ephem site location info
try:
    lat = sys.argv[1]
    lon = sys.rgv[2]
except:
    lat = "27:36:20.80:N"
    lon = "95:45:20.00:W"
if isinstance(lat, float):
    latitudeD = lat
    longitudeD = lon
else:
    latitudeD, longitudeD = converttodecimal(lat, lon)
rig = ephem.Observer()
rig.lon = str(longitudeD)
rig.lat = str(latitudeD)

#LED pin info
itsp = 17
afsp = 27
hp = 22
#pin setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(itsp, GPIO.OUT)
GPIO.setup(afsp, GPIO.OUT)
GPIO.setup(hp, GPIO.OUT)

#SPI setup
spi = spidev.SpiDev()
spi.open(0,0)

## i2c / IMU sensor
SETTINGS_FILE = "RTIMULib"
print("Using settings file " + SETTINGS_FILE + ".ini")
if not os.path.exists(SETTINGS_FILE + ".ini"):
  print("Settings file does not exist, will be created")
s = RTIMU.Settings(SETTINGS_FILE)
imu = RTIMU.RTIMU(s)
pressure = RTIMU.RTPressure(s)
print("IMU Name: " + imu.IMUName())
if (not imu.IMUInit()):
    print("IMU Init Failed")
    sys.exit(1)
else:
    print("IMU Init Succeeded");
imu.setSlerpPower(0.02)
imu.setGyroEnable(True)
imu.setAccelEnable(True)
imu.setCompassEnable(True)
poll_interval = imu.IMUGetPollInterval()
print("Recommended Poll Interval: %dmS\n" % poll_interval)

while True:
    print 'out'
    if imu.IMURead():
        print 'in'

        ## collect data

        ## i2C/ IMU&temperature
        imudata = imu.getIMUData()
        (ret1, ret2, temp1, temp2) = pressure.pressureRead()
        imuread = imudata["fusionPose"]
        imuroll, imupitch, imuyaw = (math.degrees(imuread[0])), (math.degrees(
                                        imuread[1])),(math.degrees(imuread[2]))

        ## SPI/ depth sensor
        data = ReadChannel(0) #only one device, channel 0
        spioutvolts = ConvertVolts(data)
        depth = get_depthMeters(spioutvolts)

        ## calculate solar elevation
        rig.elevation = -depth


        ## get sun locatio nand set camera position LED indicators
        alt, az = checkaxes(imuroll, imupitch, imuyaw, itsp, afsp, hp)

        ## time in milliseconds (GMT, convert for local)
        GMTms = int(round(time.time() * 1000))
        print("t: %i-%i-%i-%i r: %f p: %f y: %f d: %f c: %f sa: %s sz: %s" %
        (((int(GMTms)/(1000*60*60)%24)-6),(int(GMTms)/(1000*60)%60),
        (int(GMTms)/1000%60),(int(GMTms)/1000),imuroll,
        imupitch,imuyaw,depth, temp1,
        alt, az))
        time.sleep(poll_interval*1.0/1000.0)
        ## using print and running the python script in a shell with >> will
        ## output to a a file, you can replace the prints with writing to a
        ## file directly, if you want.

        #else:
            #continue
