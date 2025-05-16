import cv2 as cv
import numpy as np

def find_start(frames):
    for i in range(len(frames)):
        cv.imshow("Live", frames[i])
        key = cv.waitKey(30)
        if key == 27:
            break
    
    cv.destroyAllWindows()
