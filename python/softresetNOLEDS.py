import RPi.GPIO as GPIO
import time, sys
from subprocess import call

class App():
    def __init__(self):
    	print 'soft reset started'
        GPIO.setmode(GPIO.BCM)
        self.pin0 = 5
        self.pin = 6
        GPIO.setup(self.pin, GPIO.IN)

        GPIO.setup(self.pin0, GPIO.OUT)
    	GPIO.output(self.pin0, GPIO.HIGH)

        GPIO.remove_event_detect(self.pin)
        GPIO.add_event_detect(self.pin, GPIO.BOTH)

    def main(self):
        print 'served'
        if GPIO.event_detected(self.pin):
            App.shutitdown(self)
        else:
            pass

    def shutitdown(self):
        print 'trigger'
        time.sleep(1.5)

        # send to halt state
        call(["sudo", "halt"])
        GPIO.cleanup()
        sys.exit()


if __name__ == '__main__':
    sudohalt = App()
    while True:
        sudohalt.main()
