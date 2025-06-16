import argparse
import re
from src import video_processing, piano_analysis, sheet_music

def parse_url_str(url):
    pattern = r'^https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/|m\.youtube\.com/watch\?v=)[\w\-_]{11}'
    if not re.match(pattern, url):
        raise argparse.ArgumentTypeError('Invalid URL format — must be a YouTube video link.')
    return url

def parse_time_str(s):
    """Parses mm:ss string to seconds"""
    try:
        minutes, seconds = map(int, s.strip().split(':'))
        return minutes * 60 + seconds
    except:
        raise argparse.ArgumentTypeError(f'Invalid time format: {s}. Use mm:ss')

def parse_start_key_str(key):
    """Validates if input is valid piano key name"""
    if re.fullmatch(r"^[A-Ga-g]#?\d$", key) is None:
        raise argparse.ArgumentTypeError(f'Invalid key: {key} — use format like C4 or F#2')
    return key.upper()

def strip_mid_extension(path):
    """Strips trailing .mid from the output filename if present"""
    return path[:-4] if path.lower().endswith('.mid') else path

def parse_args():
    parser = argparse.ArgumentParser(
        description='Extract MIDI from piano YouTube videos',
        epilog='Example: %(prog)s -u "https://www.youtube.com/watch?v=D-X1CwyQLYo" -r 0:02 1:54 -s A0 -o song.mid'
    )
    parser.add_argument('-u', '--url', type=parse_url_str, required=True, help='url of youtube video to create MIDI from')
    parser.add_argument('-r', '--range', type=parse_time_str, required=True, nargs=2, help='start and end timestamps in mm:ss format')
    parser.add_argument('-s', '--start_key', type=parse_start_key_str, required=True, help='the leftmost key visible in frame (ex. B1)')
    parser.add_argument('-o', '--output', type=str, required=True, help='name of the output file (ex. midi_file or midi_file.mid)')
    return parser.parse_args()

def main(url, start, end, starting_key, output):
    # video processing
    print("processing video...")
    video_path, duration = video_processing.download_video(url, output)
    fps, total_frames = video_processing.get_frame_info(video_path, duration)
    start_frame, end_frame = video_processing.get_start_and_end_frames(fps, total_frames, start, end)
    gray_first_frame, hsv_first_frame = video_processing.get_first_frame(video_path, start_frame)

    # piano analysis
    print("analyzing piano...")
    gray_first_frame, crop_line_y = piano_analysis.crop_to_piano(gray_first_frame)
    hsv_first_frame = hsv_first_frame[crop_line_y:]
    key_rois = piano_analysis.locate_keys(gray_first_frame, hsv_first_frame, starting_key) #{roi: (x1, x2, y1, y2), key_color: "black" or "white", index: , hue: , saturation: , value: }
    pressed_colors = piano_analysis.get_pressed_colors(video_path, crop_line_y, start_frame, end_frame, key_rois)
    hand_assignments = piano_analysis.get_hands(pressed_colors)

    # sheet music engraving
    print("engraving sheet music...")
    events_left_hand, events_right_hand = sheet_music.hand_assignments_to_events(hand_assignments, fps)
    midi_path = sheet_music.generate_midi(events_left_hand=events_left_hand, events_right_hand=events_right_hand, output=output)
    print(f"output at {midi_path}")

if __name__ == '__main__':
    args = parse_args()
    output = strip_mid_extension(args.output)
    main(args.url, args.range[0], args.range[1], args.start_key, output)