import sys
import cv2 as cv
import numpy as np

def show_wait_destroy_particular(winname, img):

    cv.imshow(winname, img)   
    cv.moveWindow(winname, 300, 0)
    cv.waitKey(0)
    cv.destroyWindow(winname)
    cv.waitKey(1)
    
    
def clean_noise(img, min_thresh=200):
    img = cv.medianBlur(img,1)
    ret,th1 = cv.threshold(img,min_thresh,255,cv.THRESH_BINARY)

    #show_wait_destroy_particular('orig', img)
    #show_wait_destroy_particular('global', th1)
    return th1