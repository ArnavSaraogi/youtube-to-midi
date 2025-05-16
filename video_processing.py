import yt_dlp
import cv2 as cv
import numpy as np

def download_video(url, output_path = "./downloads/piano_tutorial.%(ext)s"): 
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]',  
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def extract_frames(file_path):
    frames = []
    cap = cv.VideoCapture(file_path)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    return frames