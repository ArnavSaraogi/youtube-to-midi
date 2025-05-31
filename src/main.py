import video_processing
import piano_analysis
import debug
import sheet_music
import cv2 as cv
import numpy as np

song = 'la la'
url = ''
start = 0
end = 0

if song == 'la la':
    url = "https://www.youtube.com/watch?v=D-X1CwyQLYo"
    start = 2
    end = 114
if song == 'howl':
    url = "https://www.youtube.com/watch?v=QCNVEsk3pcw"
    start = 3
    end = 170

# video processing
video_path, duration = video_processing.download_video(url)
fps, total_frames = video_processing.get_frame_info(video_path, duration)
start_frame, end_frame = video_processing.get_start_and_end_frames(fps, total_frames, start, end)
gray_first_frame, hsv_first_frame = video_processing.get_first_frame(video_path, start_frame)

gray_first_frame, crop_line_y = piano_analysis.crop_to_piano(gray_first_frame)
hsv_first_frame = hsv_first_frame[crop_line_y:]
key_rois = piano_analysis.locate_keys(gray_first_frame, hsv_first_frame)

note_matrix, pressed_colors = piano_analysis.make_note_matrix(video_path, crop_line_y, start_frame, end_frame, key_rois)
print("machine: learning...")
hand_assignments = piano_analysis.get_hands(pressed_colors)

debug.visualize_note_matrix(
    video_path=video_path,
    crop_line_y=crop_line_y,
    start_frame=start_frame,
    end_frame=end_frame,
    note_matrix=note_matrix,
    key_rois=key_rois,
    hand_assignments=hand_assignments
)

"""
# sheet music engraving
events = sheet_music.matrix_to_events(note_matrix, fps)
sheet_music.generate_midi(events)
"""