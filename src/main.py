from video_processing import download_video, extract_frames
from piano_analysis import find_start

url = "https://www.youtube.com/watch?v=uxhvq1O1jK4"

output_path = download_video(url)
frames = extract_frames(output_path)

