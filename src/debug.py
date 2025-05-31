import cv2 as cv

def play_frames(frame_gen):
    for frame in frame_gen:
        #bgr = cv.cvtColor(frame, cv.COLOR_HSV2BGR)  

        cv.imshow("HSV Frame", frame)
        key = cv.waitKey(10) 

        if key == ord('q'): 
            break

    cv.destroyAllWindows()

def show_frame(frame, window_name="Frame"):
    if frame is None:
        print("No frame to show.")
        return
    cv.imshow(window_name, frame)
    cv.waitKey(0)
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


def visualize_note_matrix(video_path, crop_line_y, start_frame, end_frame, note_matrix, key_rois, downscale_factor=0.5):
    cap = cv.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video {video_path}")
        return

    cap.set(cv.CAP_PROP_POS_FRAMES, start_frame)
    frame_index = 0
    total_frames = end_frame - start_frame + 1

    while frame_index < total_frames:
        ret, frame = cap.read()
        if not ret:
            break

        # Preprocess
        width = int(frame.shape[1] * downscale_factor)
        height = int(frame.shape[0] * downscale_factor)
        resized = cv.resize(frame, (width, height), interpolation=cv.INTER_AREA)
        resized = resized[crop_line_y:]

        # Overlay note matrix data
        for j, key in enumerate(key_rois):
            x1, x2, y1, y2 = key["roi"]
            pressed = note_matrix[frame_index, j]
            if pressed:
                cv.rectangle(resized, (x1, y1), (x2, y2), (0, 255, 0), 1)

        cv.putText(resized, f"Frame {frame_index + start_frame}", (10, 20),
                   cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        cv.imshow("Note Matrix Visualization", resized)
        key = cv.waitKey(30)
        if key == ord('q'):
            break

        frame_index += 1

    cap.release()
    cv.destroyAllWindows()