import video_processing
import piano_analysis
import debug
import sheet_music
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
output_path, duration = video_processing.download_video(url)
frames = video_processing.extract_frames(output_path)
fps = video_processing.get_fps(frames, duration)
frames = video_processing.keep_section_frames(frames, start, end, fps)

# piano analysis
frames = piano_analysis.crop_to_piano(frames)
key_rois = piano_analysis.locate_keys(frames[0])
note_matrix = piano_analysis.make_note_matrix(frames, key_rois)

# sheet music engraving
events = sheet_music.matrix_to_events(note_matrix, fps)
sheet_music.generate_midi(events)

debug.play_press_detection(frames, key_rois, note_matrix)