import cv2 as cv
import numpy as np
import os
from time import time
from windowCapture import WindowCapture
from vision import Vision
from hsvfilter import HsvFilter

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# initialize the WindowCapture class
wincap = WindowCapture('Flappy Bird')
# initialize the Vision class
vision_flappy2 = Vision('c:/work/flappy/playerrot.JPG')
vision_flappy3 = Vision('c:/work/flappy/playerrot1.jpg')
vision_flappy = Vision('c:/work/flappy/player.JPG')
vision_pipeDown = Vision('c:/work/flappy/pipe_down.jpg')
vision_pipeUp = Vision('c:/work/flappy/pipe_up.jpg')
vision_pipeTest = Vision('c:/work/flappy/pipe_test.jpg')
# initialize the trackbar window
vision_flappy.init_control_gui()

# limestone HSV filter
hsv_filter = HsvFilter(0, 0, 0, 255, 255, 255, 0, 0, 0, 0)

loop_time = time()
while(True):

    # get an updated image of the game
    screenshot = wincap.get_screenshot()

    # do object detection
    rectangles = vision_flappy.find(screenshot, 0.4)
    pipeDown = vision_pipeDown.find(screenshot, 0.7)
    pipeUp = vision_pipeUp.find(screenshot, 0.7)

#    rectangles2 = vision_flappy3.find(screenshot, 0.4)
#    rectangles3 = vision_flappy2.find(screenshot, 0.4)

    # draw the detection results onto the original image
    output_image = vision_flappy.draw_rectangles(screenshot, rectangles)
    output_image = vision_flappy.draw_rectangles(output_image, pipeDown)
    output_image = vision_flappy.draw_rectangles(output_image, pipeUp)
#    output_image = vision_flappy.draw_rectangles(output_image, rectangles2)
#    output_image = vision_flappy.draw_rectangles(output_image, rectangles3)

    #display matches
    cv.imshow('Matches', output_image)

    # debug the loop rate
    print('FPS {}'.format(1 / (time() - loop_time)))
    loop_time = time()

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done.')