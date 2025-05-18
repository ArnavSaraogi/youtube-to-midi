import cv2 as cv
import numpy as np

def play_frames(frames):
    for i in range(len(frames)):
        cv.imshow("Live", frames[i])
        key = cv.waitKey(30)
        if key == 27:
            break
    
    cv.destroyAllWindows()

def crop_to_piano(frames):
    frame = frames[0]
    height = frame.shape[0]
    bottom_half = frame[height//2:]
    edges = cv.Canny(bottom_half, 35, 100)
    
    lines = cv.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=100, minLineLength=frame.shape[1] // 2, maxLineGap=20)

    if lines is None:
        print("Cannot find piano")
        return []

    top_line_y = None
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if abs(y1 - y2) < 5:
            y = min(y1, y2)
            if top_line_y is None or y < top_line_y: 
                top_line_y = y
    
    if top_line_y is None:
        print("Cannot find piano")
        return []
    else:
        for i in range(len(frames)):
            frames[i] = frames[i][top_line_y + height//2:]
    
    return frames

