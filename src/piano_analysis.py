import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

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

def locate_keys(frames):
    frame = frames[0]
    boundaries = find_key_boundaries(frame)
    
    height = frame.shape[0]
    white_top = (height//4) * 3
    white_bottom = (height - 10)
    
    key_width_3rd = int(boundaries[0] * 1/3)
    
    key_rois = [(0 + key_width_3rd, boundaries[0] - key_width_3rd)] # x1, x2
    for i in range(1, len(boundaries)):
        key_width_3rd = int((boundaries[i] - boundaries[i - 1]) * 1/3)
        key_rois.append((boundaries[i - 1] + key_width_3rd, boundaries[i] - key_width_3rd))
    key_rois.append((boundaries[len(boundaries) - 1] + key_width_3rd, frame.shape[1] - key_width_3rd))

    debug_frame = frames[0]
    for roi in key_rois:
        cv.line(debug_frame, (roi[0], white_top), (roi[0], white_bottom), (0, 0, 255), 1)
        cv.line(debug_frame, (roi[1], white_top), (roi[1], white_bottom), (0, 0, 255), 1)
    cv.imshow("Key Boundaries", debug_frame)
    cv.waitKey(0)
    cv.destroyAllWindows()

def find_key_boundaries(frame):
    height = frame.shape[0]
    frame_cropped = frame[(height//4)* 3:]

    inv = 255 - frame_cropped

    vertical_projection = np.sum(inv, axis = 0)
    projection_smoothed = cv.GaussianBlur(
        vertical_projection.astype(np.float32).reshape(1, -1), 
        (21,1), 
        0
        ).flatten()
    threshold = np.max(projection_smoothed) * 0.5
    boundaries = []
    for i in range(1, len(projection_smoothed) - 1):
        if (
            projection_smoothed[i] > threshold and
            projection_smoothed[i] > projection_smoothed[i - 1] and
            projection_smoothed[i] > projection_smoothed[i + 1]
        ):
            boundaries.append(i)

    return boundaries