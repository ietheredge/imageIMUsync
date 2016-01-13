import RPi.GPIO as GPIO
import time, sys
from subprocess import call

class App():
    def __init__(self):
	print 'soft reset started'
    GPIO.setmode(GPIO.BCM)
	self.pin0 = 5
    self.pin = 6
    self.led1 = 17
    self.led2 = 27
    self.led3 = 22
	GPIO.setup(self.pin0, GPIO.OUT)
	GPIO.output(self.pin0, GPIO.HIGH)
    GPIO.setup(self.pin, GPIO.IN)
    GPIO.setup(self.led1, GPIO.OUT)
    GPIO.setup(self.led2, GPIO.OUT)
    GPIO.setup(self.led3, GPIO.OUT)
    GPIO.remove_event_detect(self.pin)
	GPIO.add_event_detect(self.pin, GPIO.BOTH)

	#print 'OK'
    def main(self):
        print 'served'
	if GPIO.event_detected(self.pin):
            App.shutitdown(self)

    def shutitdown(self):
        # flash leds to alert user
	print 'trigger'
        for pins in [self.led1, self.led2, self.led3]:
            GPIO.output(pins, GPIO.HIGH)
            GPIO.output(pins, GPIO.LOW)
            time.sleep(0.5)
        for pins in [self.led1, self.led2, self.led3]:
            GPIO.output(pins, GPIO.HIGH)
            GPIO.output(pins, GPIO.LOW)
            time.sleep(0.5)
        for pins in [self.led1, self.led2, self.led3]:
            GPIO.output(pins, GPIO.HIGH)
            GPIO.output(pins, GPIO.LOW)
            time.sleep(0.5)
        GPIO.output(self.led1, GPIO.HIGH)
        GPIO.output(self.led2, GPIO.HIGH)
        GPIO.output(self.led3, GPIO.HIGH)
        time.sleep(.5)
        # send to halt state
        call(["sudo", "halt"])
        GPIO.cleanup()
        sys.exit()


if __name__ == '__main__':
    sudohalt = App()
    while True:
        sudohalt.main()
