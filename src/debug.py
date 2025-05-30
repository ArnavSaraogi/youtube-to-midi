import cv2 as cv

def play_frames(frames):
    for i in range(len(frames)):
        cv.imshow("Live", frames[i])
        key = cv.waitKey(30)
        if key == 27:
            break
    
    cv.destroyAllWindows()

def check_key_order(key_rois):
    passed = True
    black_key_idxs = {1, 4, 6, 9, 11}
    for key in key_rois:
        if key['index'] % 12 in black_key_idxs:
            if key['color'] != 'black':
                passed = False
        else:
            if key['color'] != 'white':
                passed = False
    print(passed)

def play_press_detection(frames, key_rois, note_matrix):
    for i, frame in enumerate(frames):
        bgr_frame = cv.cvtColor(frame, cv.COLOR_HSV2BGR)
        for j, key in enumerate(key_rois):
            if note_matrix[i, j] == 1:  # key pressed
                x1, x2, y1, y2 = key['roi']
                cv.rectangle(bgr_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # green box
        cv.imshow("Color frame with boxes", bgr_frame)
        if cv.waitKey(30) & 0xFF == ord('q'):
            break
    
    cv.destroyAllWindows()