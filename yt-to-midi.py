import argparse
import os
import sys
from src import video_processing, piano_analysis, sheet_music, arg_validation

def main(url, start, end, starting_key, output):
    print("processing video...")
    video_path, duration = video_processing.download_video(url, output)
    fps, total_frames = video_processing.get_frame_info(video_path, duration)
    start_frame, end_frame = video_processing.get_start_and_end_frames(fps, total_frames, start, end)
    gray_first_frame, hsv_first_frame = video_processing.get_first_frame(video_path, start_frame)

    print("analyzing piano...")
    gray_first_frame, crop_line_y = piano_analysis.crop_to_piano(gray_first_frame)
    hsv_first_frame = hsv_first_frame[crop_line_y:]
    key_rois = piano_analysis.locate_keys(gray_first_frame, hsv_first_frame, starting_key) #{roi: (x1, x2, y1, y2), key_color: "black" or "white", index: , hue: , saturation: , value: }
    pressed_colors = piano_analysis.get_pressed_colors(video_path, crop_line_y, start_frame, end_frame, key_rois)
    hand_assignments = piano_analysis.get_hands(pressed_colors)
    os.remove(video_path)

    print("generating MIDI...")
    events_left_hand, events_right_hand = sheet_music.hand_assignments_to_events(hand_assignments, fps)
    midi_path = sheet_music.generate_midi(events_left_hand=events_left_hand, events_right_hand=events_right_hand, output=output)
    print(f"output at {midi_path}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        def prompt_with_validation(prompt, parser_func):
            while True:
                val = input(prompt).strip()
                try:
                    return parser_func(val)
                except argparse.ArgumentTypeError as e:
                    print(f"Error: {e}")

        url = prompt_with_validation("Enter YouTube URL: ", arg_validation.parse_url_str)
        start = prompt_with_validation("Enter start time (mm:ss): ", arg_validation.parse_time_str)
        end = prompt_with_validation("Enter end time (mm:ss): ", arg_validation.parse_time_str)
        arg_validation.check_times(start, end)
        start_key = prompt_with_validation("Enter leftmost visible key (e.g., A0): ", arg_validation.parse_start_key_str)
        output = input("Enter output filename (e.g., song.mid): ").strip()
        output = arg_validation.strip_mid_extension(output)

    else:
        args = arg_validation.parse_args()
        url = args.url
        start, end = args.range
        arg_validation.check_times(start, end)
        start_key = args.start_key
        output = arg_validation.strip_mid_extension(args.output)

    main(url, start, end, start_key, output)