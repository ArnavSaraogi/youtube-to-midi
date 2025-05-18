import os
import yt_dlp
import cv2 as cv

def download_video(url): 
    with yt_dlp.YoutubeDL({}) as ydl:
        info = ydl.extract_info(url, download=False)

    title = (info.get('title', 'no_title')).replace(" ", "_")[:20]
    duration = info.get('duration', 0)

    os.makedirs("./downloads", exist_ok=True)
    output_path = "./downloads/" + title + ".mp4"

    if os.path.exists(output_path):
        return (output_path, duration)

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return (output_path, duration)

def extract_frames(file_path):
    downscale_factor = 0.5
    frames = []
    cap = cv.VideoCapture(file_path)

    if not cap.isOpened():
        print(f"Error: Cannot open video file {file_path}")
        return frames 

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        width = int(frame.shape[1] * downscale_factor)
        height = int(frame.shape[0] * downscale_factor)
        
        resized = cv.resize(frame, (width, height), interpolation=cv.INTER_AREA)
        gray = cv.cvtColor(resized, cv.COLOR_BGR2GRAY)

        print(frame.shape)
        print(gray.shape)

        frames.append(gray)

    cap.release()
    return frames

def keep_section_frames(frames, start, end, duration):
    if duration == 0:
        raise ValueError("Duration cannot be zero.")
    
    fps = len(frames) / duration
    start_frame = int(max(0, fps * start))
    end_frame = int(min(len(frames), fps * end))
    return frames[start_frame:end_frame]