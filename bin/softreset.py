import RPi.GPIO as GPIO
import time
from subprocess import call

class App():
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.pin = 5
        self.led1 = 17
        self.led2 = 27
        self.led3 = 22
        GPIO.setup(self.pin, GPIO.OUT, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.led1, GPIO.OUT)
        GPIO.setup(self.led1, GPIO.OUT)
        GPIO.setup(self.led1, GPIO.OUT)

    def listen(self):
        try:
            time.sleep(0.25)
            GPIO.wait_for_edge(self.pin, GPIO.FALLING)
            GPIO.output(self.led1, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(self.led1, GPIO.LOW)
            GPIO.output(self.led2, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(self.led2, GPIO.LOW)
            GPIO.output(self.led3, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(self.led3, GPIO.LOW)
            GPIO.output(self.led1, GPIO.LOW)
            GPIO.output(self.led2, GPIO.LOW)
            GPIO.output(self.led1, GPIO.HIGH)
            GPIO.output(self.led2, GPIO.HIGH)
            GPIO.output(self.led3, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(self.led3, GPIO.LOW)
            GPIO.output(self.led1, GPIO.LOW)
            GPIO.output(self.led2, GPIO.LOW)

            call(["sudo", "halt"])
        else:
            pass


if __name__ == '__main__':
    sudohalt = App()
    while True:
        App.listen()
