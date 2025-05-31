import video_processing
import debug
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

def crop_to_piano(gray_first_frame):
    height = gray_first_frame.shape[0]
    bottom_half = gray_first_frame[height//2:]
    edges = cv.Canny(bottom_half, 35, 100)
    
    lines = cv.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=100, minLineLength=gray_first_frame.shape[1] // 2, maxLineGap=20)

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
    
    gray_first_frame = gray_first_frame[top_line_y + height//2:]

    return (gray_first_frame, top_line_y + height//2)

def locate_keys(gray_frame, hsv_frame):  
    boundaries = find_key_boundaries(gray_frame)
    white_key_rois = find_white_keys(gray_frame, boundaries)
    black_key_rois = find_black_keys(gray_frame)

    key_rois = [
        {"roi": roi, "color": "white"} for roi in white_key_rois
    ] + [
        {"roi": roi, "color": "black"} for roi in black_key_rois
    ]

    key_rois.sort(key=lambda k: (k["roi"][0] + k["roi"][1]) // 2)

    for idx, key in enumerate(key_rois):
        key["index"] = idx
        x1, x2, y1, y2 = key["roi"]
        roi = hsv_frame[y1:y2, x1:x2]
        h, s, v, _ = cv.mean(roi)
        key["hue"] = h
        key["saturation"] = s
        key["value"] = v

    return key_rois # {roi: , color: , index: , hue: , saturation: , value: }

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

def make_note_matrix(video_path, crop_line_y, start_frame, end_frame, key_rois, sat_thresh=30, val_thresh=30):
    num_frames = end_frame - start_frame + 1
    note_matrix = np.zeros((num_frames, len(key_rois)), dtype=np.uint8)
    frame_gen = video_processing.stream_HSV_frames(video_path, crop_line_y, start_frame, end_frame)

    for i, frame in enumerate(frame_gen):
        for j, key in enumerate(key_rois):
            x1, x2, y1, y2 = key["roi"]
            roi = frame[y1:y2, x1:x2]
            h, s, v, _ = cv.mean(roi)

            if key["color"] == "white":
                if abs(s - key["saturation"]) > sat_thresh:
                    note_matrix[i, j] = 1
            else:
                if abs(v - key["value"]) > val_thresh:
                    note_matrix[i, j] = 1

    return note_matrix