import os
import yt_dlp
import cv2 as cv

def download_video(url): 
    with yt_dlp.YoutubeDL({}) as ydl:
        info = ydl.extract_info(url, download=False)

    title = (info.get('title', 'no_title')).replace(" ", "_")[:20]
    os.makedirs("./downloads", exist_ok=True)
    output_path = "./downloads/" + title + ".mp4"

    if os.path.exists(output_path):
        return output_path

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return output_path



def extract_frames(file_path):
    frames = []
    cap = cv.VideoCapture(file_path)

    if not cap.isOpened():
        print(f"Error: Cannot open video file {file_path}")
        return frames 

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frames.append(gray)

    cap.release()
    return frames