import cv2 as cv
import numpy as np
from time import time
from mss import mss
from PIL import Image
import pyautogui



loop_time = time()
sct = mss()
while(True):

    monitor = {"top": 194, "left": 130, "width": 309, "height": 530}                          # window upper left corner    --> sct.monitors[1] for whole monitor 1

    screenshot = sct.grab(monitor)
    screenshot = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "RGBX")
    screenshot = np.array(screenshot)
   
    needle_img = cv.imread('/home/edvard/Documents/ML/OpenCVtest/files/flappybcut.png')
    upper = cv.imread('/home/edvard/Documents/ML/OpenCVtest/files/upper_pipe.png')
    lower = cv.imread('/home/edvard/Documents/ML/OpenCVtest/files/lower_pipe.png')

    needle_w = needle_img.shape[1]
    needle_h = needle_img.shape[0]

    upper_w = upper.shape[1]
    upper_h = upper.shape[0]

    lower_w = lower.shape[1]
    lower_h = lower.shape[0]

    result = cv.matchTemplate(screenshot, needle_img, cv.TM_CCOEFF)
    res_u = cv.matchTemplate(screenshot, upper, cv.TM_CCOEFF_NORMED)
    res_l = cv.matchTemplate(screenshot, lower, cv.TM_CCOEFF_NORMED)

    cv.imshow('Result', result)
 
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

    threshold = 1
    thr_u = 0.9
    thr_l = 0.8

    loc_u = np.where(res_u >= thr_u)
    loc_l = np.where(res_l >= thr_l)

    if max_val >= threshold:
        print('Found needle.')


        top_left = max_loc
        height = max_loc[1]
        bottom_right = (top_left[0] + needle_w, top_left[1] + needle_h)
        cv.rectangle(screenshot, top_left, bottom_right,
                     color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)
        #print("position of bird:", max_loc)
        
        v_bird_upper = 0
        w_bird_upper = 0
        
        v_bird_lower = 0
        w_bird_lower = 0
        pt_u = (0,0)

        for pt in zip(*loc_u[::-1]):
            cv.rectangle(screenshot, pt, (pt[0] + upper_w, pt[1] + upper_h), 
                         color=(0,0,255), thickness=2, lineType=cv.LINE_4)
            pt_u = pt
            #v_bird_upper = (pt_u[1] + upper_h) - (height + needle_h*0.5)
            #w_bird_upper = (pt_u[0] + upper_w*0.5) - (max_loc[0] + needle_w*0.5)
        #print ("postion of upper pipe:", pt_u)

        pt_l = (0,0)
        for pt in zip(*loc_l[::-1]):
            cv.rectangle(screenshot, pt, (pt[0] + lower_w, pt[1] + lower_h),
                         color=(0, 0, 255), thickness=2, lineType=cv.LINE_4)
            pt_l = pt
            #v_bird_lower = pt_l[1] - (height + needle_h*0.5)
            #w_bird_lower = (pt_l[0] + lower_w*0.5) - (max_loc[0] + needle_w*0.5)
        #print("postion of lower pipe:", pt_l) 
        #print("bird to upper:", w_bird_upper, ",", v_bird_upper)
        #print("bird to lower:", w_bird_lower, ",", v_bird_lower)

        v_bird_mid = -1* ((height + needle_h*0.5) - (pt_u[1] + (pt_l[1] - pt_u[1])*0.5))
        w_bird_mid = (pt_l[0] + lower_w*0.5) - (max_loc[0] + needle_w*0.5)
        print("vertical distance from middle point between pipes", v_bird_mid)
        print("horizontal distance from middle point between pipes", w_bird_mid)

        birdx = int(max_loc[0]+needle_w*0.5)
        birdy = int(max_loc[1]+needle_h*0.5)
        birdpos = ((birdx), (birdy))
        pipesx = int(pt_l[0] + lower_w*0.5)
        pipesy = int(pt_u[1] + upper_h*0.5 + (pt_l[1] - pt_u[1])*0.5)
        pipespos = (pipesx, pipesy)

        cv.line(screenshot, birdpos, pipespos, color=(255, 0, 0), thickness=2, lineType=cv.LINE_4)

        cv.imshow('Result', screenshot)      

    else:
        print('No needle found.')


    print('FPS {}'.format(1 / (time() - loop_time)))
    loop_time = time()

    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done.')
