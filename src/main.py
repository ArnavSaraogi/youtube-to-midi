import video_processing
import piano_analysis
import debug
import sheet_music
import time

song = 'la la'
url = ''
start = 0
end = 0
starting_key = 'A0'

if song == 'la la':
    url = "https://www.youtube.com/watch?v=D-X1CwyQLYo"
    start = 2
    end = 114
if song == 'howl':
    url = "https://www.youtube.com/watch?v=QCNVEsk3pcw"
    start = 3
    end = 170
if song == 'crazy':
    url = "https://www.youtube.com/watch?v=YIvGxvZBR80"
    start = 3
    end = 183
if song == 'halo':
    url = 'https://www.youtube.com/watch?v=xuXoLWssFCY'
    start = 4
    end = 175
    starting_key = 'C1'

# video processing
video_path, duration = video_processing.download_video(url)
fps, total_frames = video_processing.get_frame_info(video_path, duration)
start_frame, end_frame = video_processing.get_start_and_end_frames(fps, total_frames, start, end)
gray_first_frame, hsv_first_frame = video_processing.get_first_frame(video_path, start_frame)

# piano analysis
gray_first_frame, crop_line_y = piano_analysis.crop_to_piano(gray_first_frame)
hsv_first_frame = hsv_first_frame[crop_line_y:]
key_rois = piano_analysis.locate_keys(gray_first_frame, hsv_first_frame, starting_key) #{roi: (x1, x2, y1, y2), key_color: "black" or "white", index: , hue: , saturation: , value: }


start = time.time()

pressed_colors = piano_analysis.get_pressed_colors(video_path, crop_line_y, start_frame, end_frame, key_rois)

end = time.time()
print(f"Loop time: {end - start:.2f} sec")

print("machine: learning...")
hand_assignments = piano_analysis.get_hands(pressed_colors)

# sheet music engraving
events_left_hand, events_right_hand = sheet_music.hand_assignments_to_events(hand_assignments, fps)
midi_path = sheet_music.generate_midi(events_left_hand=events_left_hand, events_right_hand=events_right_hand)

#sheet_music.midi_to_sheet(midi_path=midi_path)