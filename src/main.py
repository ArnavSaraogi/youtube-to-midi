import video_processing as vp
import piano_analysis as pa
import debug as db
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

output_path, duration = vp.download_video(url)
frames = vp.extract_frames(output_path)
frames = vp.keep_section_frames(frames, start, end, duration)
frames = pa.crop_to_piano(frames)
key_rois = pa.locate_keys(frames[0])

note_matrix = pa.make_note_matrix(frames, key_rois)

db.play_press_detection(frames, key_rois, note_matrix)