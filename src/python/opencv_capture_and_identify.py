import cv2 as cv
import numpy as np
import os
from time import time
from mss import mss
from PIL import Image

loop_time = time()
sct = mss()
while(True):
    
    monitor = {"top": 100, "left": 0 , "width": 450, "height":650}                          ### window upper left corner    --> sct.monitors[1] for whole monitor 1
    screenshot = sct.grab(monitor)
    screenshot = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "RGBX")
    #return Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')         ### conversion on linux not necessary, maybe on windows?
    screenshot = np.array(screenshot)
    #screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)                                 ### conversion on linux not necessary, maybe on windows?

    needle_img = cv.imread('/home/edvard/Documents/ML/OpenCVtest/files/flappybcut.png')

    result = cv.matchTemplate(screenshot, needle_img, cv.TM_CCOEFF)                         ### cv.TM_CCOEFF        --> always has to find exactly 1 match
                                                                                            ### cv.TM_CCOEFF_NORMED --> few pipes matched as flappybird. Other methods are worse
 
    cv.imshow('Result', result)
 
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    threshold = 0.99
    if max_val >= threshold:
        print('Found needle.')
        needle_w = needle_img.shape[1]
        needle_h = needle_img.shape[0]

        top_left = max_loc
        bottom_right = (top_left[0] + needle_w, top_left[1] + needle_h)
        cv.rectangle(screenshot, top_left, bottom_right,
                     color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)
        cv.imshow('Result', screenshot)

        #cv.waitKey()
    
    else:
        print('No needle found.')


    print('FPS {}'.format(1 / (time() - loop_time)))
    loop_time = time()

    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done.')
