import RPi.GPIO as GPIO



triggerGPIO = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(triggerGPIO, GPIO.OUT)
GPIO.output(triggerGPIO, 0)
