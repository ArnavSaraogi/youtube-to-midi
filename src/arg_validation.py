import argparse
import re

def parse_url_str(url):
    pattern = r'^https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/|m\.youtube\.com/watch\?v=)[\w\-_]{11}'
    if not re.match(pattern, url):
        raise argparse.ArgumentTypeError('Invalid URL format — must be a YouTube video link.')
    return url

def parse_time_str(s):
    """Parses mm:ss string to seconds"""
    try:
        minutes, seconds = map(int, s.strip().split(':'))
        if minutes >= 60 or minutes < 0 or seconds >= 60 or seconds < 0:
            raise Exception()
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

def check_times(start, end):
    if start >= end:
        raise ValueError("Start time must be less than end time")