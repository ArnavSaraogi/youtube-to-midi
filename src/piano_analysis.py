from . import video_processing
import cv2 as cv
import numpy as np
from sklearn.cluster import KMeans
from tqdm import tqdm

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

def locate_keys(gray_frame, hsv_frame, starting_key="A0"):  
    boundaries = find_key_boundaries(gray_frame)
    white_key_rois = find_white_keys(gray_frame, boundaries)
    black_key_rois = find_black_keys(gray_frame)

    key_rois = [
        {"roi": roi, "key_color": "white"} for roi in white_key_rois
    ] + [
        {"roi": roi, "key_color": "black"} for roi in black_key_rois
    ]

    key_rois.sort(key=lambda k: (k["roi"][0] + k["roi"][1]) // 2)

    starting_key_pos = get_starting_key_pos(starting_key)

    for idx, key in enumerate(key_rois):
        key["key_pos"] = idx + starting_key_pos
        x1, x2, y1, y2 = key["roi"]
        roi = hsv_frame[y1:y2, x1:x2]
        h, s, v, _ = cv.mean(roi)
        key["hue"] = h
        key["saturation"] = s
        key["value"] = v

    return key_rois # {roi: (x1, x2, y1, y2), key_color: "black" or "white", key_pos: , hue: , saturation: , value: }

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

def get_starting_key_pos(starting_key):
    key_to_key_pos = {
        "A0": 0, "A#0": 1, "B0": 2,
        "C1": 3, "C#1": 4, "D1": 5, "D#1": 6, "E1": 7, "F1": 8, "F#1": 9, "G1": 10, "G#1": 11,
        "A1": 12, "A#1": 13, "B1": 14,
        "C2": 15, "C#2": 16, "D2": 17, "D#2": 18, "E2": 19, "F2": 20, "F#2": 21, "G2": 22, "G#2": 23,
        "A2": 24, "A#2": 25, "B2": 26,
        "C3": 27, "C#3": 28, "D3": 29, "D#3": 30, "E3": 31, "F3": 32, "F#3": 33, "G3": 34, "G#3": 35,
        "A3": 36, "A#3": 37, "B3": 38,
        "C4": 39, "C#4": 40, "D4": 41, "D#4": 42, "E4": 43, "F4": 44, "F#4": 45, "G4": 46, "G#4": 47,
        "A4": 48, "A#4": 49, "B4": 50,
        "C5": 51, "C#5": 52, "D5": 53, "D#5": 54, "E5": 55, "F5": 56, "F#5": 57, "G5": 58, "G#5": 59,
        "A5": 60, "A#5": 61, "B5": 62,
        "C6": 63, "C#6": 64, "D6": 65, "D#6": 66, "E6": 67, "F6": 68, "F#6": 69, "G6": 70, "G#6": 71,
        "A6": 72, "A#6": 73, "B6": 74,
        "C7": 75, "C#7": 76, "D7": 77, "D#7": 78, "E7": 79, "F7": 80, "F#7": 81, "G7": 82, "G#7": 83,
        "A7": 84, "A#7": 85, "B7": 86,
        "C8": 87
    }

    return key_to_key_pos[starting_key]

def get_pressed_colors(video_path, crop_line_y, start_frame, end_frame, key_rois, sat_thresh=50, val_thresh=100):    
    frame_gen = video_processing.stream_HSV_frames(video_path, crop_line_y, start_frame, end_frame)

    pressed_colors = {}
    for i, frame in enumerate(tqdm(frame_gen, total=end_frame-start_frame+1)):
        for key in key_rois:
            x1, x2, y1, y2 = key["roi"]
            roi = frame[y1:y2, x1:x2]
            h, s, v, _ = cv.mean(roi)

            if key["key_color"] == "white":
                if abs(s - key["saturation"]) > sat_thresh:
                    pressed_colors[(i, key["key_pos"])] = {"hue": int(round(h)), "x": (x1 + x2) // 2}
            else:
                if abs(v - key["value"]) > val_thresh:
                    pressed_colors[(i, key["key_pos"])] = {"hue": int(round(h)), "x": (x1 + x2) // 2}

    return (pressed_colors)

def get_hands(pressed_colors):
    hues = []
    xs = []
    frame_key_tuples = []

    for frame_key_tuple, data in pressed_colors.items():
        hues.append(data["hue"])
        xs.append(data["x"])
        frame_key_tuples.append(frame_key_tuple)
    
    theta = 2 * np.pi * np.array(hues) / 180
    hue_cartesian = np.column_stack((np.cos(theta), np.sin(theta)))

    labels = KMeans(n_clusters=2, random_state=42).fit_predict(hue_cartesian)

    cluster_x_avgs = []
    for cluster_id in range(2):
        cluster_xs = [xs[i] for i, label in enumerate(labels) if label == cluster_id]
        cluster_x_avgs.append(np.mean(cluster_xs))
    
    left_cluster = np.argmin(cluster_x_avgs)

    hand_assignments = {}
    for i, label in enumerate(labels):
        if label == left_cluster:
            hand_assignments[frame_key_tuples[i]] = "left"
        else:
            hand_assignments[frame_key_tuples[i]] = "right"

    return hand_assignments