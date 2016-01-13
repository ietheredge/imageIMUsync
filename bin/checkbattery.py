import RPi.GPIO as GPIO
import argparse

__version__ = "P16.1.0"


class App:
    def __init__(self):
        # setup GPIO pin for battery gate input
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(16, GPIO.IN)
        print 'pin 16: ', str(GPIO.input(16))

    def check(self):
        # check GPIO pin for voltage drop
        if GPIO.input(16):
            #print True
            return True
        else:
            #print False
            return False

    def loglowbat(self):
        # log results from battery queries
        if not GPIO.input(16):
            print 'battery voltage drop detected, starting log.'
            batlog.info("battery voltage drop detected")

            while True:
                batlog.info("they say I got a low battery but I ain't dead yet!")
                time.sleep(120)
        else:
            print 'battery must be low (have a significant drop in voltage) to start log.\n' \
                  '\trun $:python checkbattery.py --calib to check every 5 minutes and create log on detection' \


    def retlowbatcal(self):
        # print the first and last lines of log file
        f = open('log/lowbatlog.log')
        lines = f.read().splitlines()
        print lines[0]
        print lines[1]
        print lines[-1]
        return lines[0], lines[1], lines[-1]


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--calib", help="run batcheck with calibration on", action='store_true')
    ap.add_argument("-r", "--readcal", help="returns the average battery reserve calibration", action='store_true')
    args = vars(ap.parse_args())
    batapp = App()
    batapp.check()

    if args["calib"]:
        import time
        import logging
        batlog = logging.getLogger('lowbatlog')
        hdlr = logging.FileHandler('log/lowbatlog.log')
        formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s', "%m/%d/%Y:%H:%M:%S")
        hdlr.setFormatter(formatter)
        batlog.addHandler(hdlr)
        batlog.setLevel(logging.INFO)
        batlog.info("starting calibration schedule, will check for voltage drop every 5 minutes")
        print 'monitoring battery for voltage drop.'
        while True:
            time.sleep(300)
            if batapp.check():
                print 'battery voltage OK!'
                continue
            else:
                batapp.loglowbat()

    if args["readcal"]:
        batapp.retlowbatcal()
