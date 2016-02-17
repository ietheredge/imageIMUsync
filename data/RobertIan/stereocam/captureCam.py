
#simple camera capture for getting calibration images from raspberry pi camera module
import time
import picamera

with picamera.PiCamera() as camera:
    camera.resolution = (1920,1080)
    camera.exposure_mode = 'sports' #need a fast shutter speed
    start = time.time()
    camera.capture_sequence((
        'img%04d.jpg' % i #format
        for i in range(10) #number of sample images
    ), use_video_port=False) #capture frames from stream or images (False==images,True==frames)
