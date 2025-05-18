from video_processing import download_video, extract_frames, keep_section_frames
from piano_analysis import play_frames, crop_to_piano
import numpy as np

url = "https://www.youtube.com/watch?v=D-X1CwyQLYo"
start = 1
end = 114

output_path, duration = download_video(url)
frames = extract_frames(output_path)
frames = keep_section_frames(frames, start, end, duration)

frames = crop_to_piano(frames)

play_frames(frames)