import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

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

def locate_keys(frame):
    boundaries = find_key_boundaries(frame)
    white_key_rois = find_white_keys(frame, boundaries)
    black_key_rois = find_black_keys(frame)

    key_rois = [
        {"roi": roi, "color": "white"} for roi in white_key_rois
    ] + [
        {"roi": roi, "color": "black"} for roi in black_key_rois
    ]

    key_rois.sort(key=lambda k: (k["roi"][0] + k["roi"][1]) // 2)

    for idx, key in enumerate(key_rois):
        key["index"] = idx
        x1, x2, y1, y2 = key["roi"]
        key["intensity"] = cv.mean(frame[y1:y2, x1:x2])[0]

    return key_rois # {roi: , color: , index: , intensity: }

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

def find_white_keys(frame, boundaries):    
    height = frame.shape[0]
    white_top = (height//4) * 3
    white_bottom = (height - 10)
    
    key_width_3rd = int(boundaries[0] * 1/3)
    
    white_key_rois = [(0 + key_width_3rd, boundaries[0] - key_width_3rd, white_top, white_bottom)] # x1, x2, y1, y2
    for i in range(1, len(boundaries)):
        key_width_3rd = int((boundaries[i] - boundaries[i - 1]) * 1/3)
        white_key_rois.append((boundaries[i - 1] + key_width_3rd, boundaries[i] - key_width_3rd, white_top, white_bottom))
    white_key_rois.append((boundaries[len(boundaries) - 1] + key_width_3rd, frame.shape[1] - key_width_3rd, white_top, white_bottom))

    return white_key_rois

def find_black_keys(frame):
    height = frame.shape[0]
    upper_half = frame[height // 10 : height // 2] # upper portion cropped to avoid black bar in some videos
    inv = 255 - upper_half
    _, thresh = cv.threshold(inv, 200, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    black_key_rois = []

    for cnt in contours:
        x, y, w, h = cv.boundingRect(cnt)
        if 5 < w < 100:
            black_key_rois.append((x + int(w // 4), x + (int(w // 4) * 3), (height // 10) + y + int(h // 4), (height // 10) + y + h)) # x1, x2, y1, y2

    return black_key_rois

def make_note_matrix(frames, key_rois):
    note_matrix = np.zeros((len(frames), len(key_rois)), dtype=np.uint8)

    for i, frame in enumerate(frames):
        for j, key in enumerate(key_rois):
            x1, x2, y1, y2 = key['roi']
            new_intensity = cv.mean(frame[y1:y2, x1:x2])[0]
            if abs(new_intensity - key['intensity']) > 40:
                note_matrix[i, j] = 1

    return note_matrix