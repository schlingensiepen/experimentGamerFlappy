import cv2 as cv
import numpy as np
import os
from time import time
from windowCapture import WindowCapture
from vision import Vision



# initialize the WindowCapture class
wincap = WindowCapture('Flappy Bird')
# initialize the Vision class
vision_flappy = Vision('c:/work/flappy/player.jpg')

'''
# https://www.crazygames.com/game/guns-and-bottle
wincap = WindowCapture()
vision_gunsnbottle = Vision('C:/Users/atwer/PycharmProjects/pythonProject/assets/sprites/')
'''

loop_time = time()
while(True):

    # get an updated image of the game
    screenshot = wincap.get_screenshot()

    surf = cv.SURF(400)
    kp, des = surf.detectAndCompute(screenshot,None)
    len(kp)

    # debug the loop rate
    print('FPS {}'.format(1 / (time() - loop_time)))
    loop_time = time()

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done.')