import os
import yt_dlp
import cv2 as cv

def download_video(url, output): 
    with yt_dlp.YoutubeDL({}) as ydl:
        info = ydl.extract_info(url, download=False)

    duration = info.get('duration', 0)

    os.makedirs("tmp", exist_ok=True)
    video_path = "./tmp/" + output + ".mp4"
    
    if os.path.exists(video_path):
        return (video_path, duration)

    ydl_opts = {
        'quiet': True,
        'format': 'bestvideo[ext=mp4]',
        'outtmpl': video_path,
        'merge_output_format': 'mp4',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return (video_path, duration)

def stream_HSV_frames(video_path, crop_line_y, start_frame=0, end_frame=None, downscale_factor = 0.5):
    cap = cv.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video file {video_path}")
        return
    cap.set(cv.CAP_PROP_POS_FRAMES, start_frame)

    frame_index = start_frame

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if end_frame is not None and frame_index > end_frame:
            break

        # downscale, convert to HSV, blur, crop
        width = int(frame.shape[1] * downscale_factor)
        height = int(frame.shape[0] * downscale_factor)
        resized = cv.resize(frame, (width, height), interpolation=cv.INTER_AREA)
        hsv_blurred = cv.GaussianBlur(cv.cvtColor(resized, cv.COLOR_BGR2HSV), (5, 5), 0)
        hsv_blurred = hsv_blurred[crop_line_y:]

        yield hsv_blurred
        frame_index += 1
    
    cap.release()

def get_frame_info(video_path, duration):
    cap = cv.VideoCapture(video_path)
    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    cap.release()
    return ((total_frames / duration), total_frames)

def get_start_and_end_frames(fps, total_frames, start, end):
    start_frame = max(int(round(fps * start)), 0)
    end_frame = min(int(round(fps * end)), total_frames)
    return (start_frame, end_frame)

def get_first_frame(video_path, start_frame, downscale_factor = 0.5):
    cap = cv.VideoCapture(video_path)
    cap.set(cv.CAP_PROP_POS_FRAMES, start_frame)
    
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print(f"Error: Couldn't read frame {start_frame} from {video_path}")
        return None

    width = int(frame.shape[1] * downscale_factor)
    height = int(frame.shape[0] * downscale_factor)
    resized = cv.resize(frame, (width, height), interpolation=cv.INTER_AREA)

    gray_blurred = cv.GaussianBlur(cv.cvtColor(resized, cv.COLOR_BGR2GRAY), (5,5), 0)
    hsv_blurred = cv.GaussianBlur(cv.cvtColor(resized, cv.COLOR_BGR2HSV), (5,5), 0)

    return (gray_blurred, hsv_blurred)