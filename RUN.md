## Prerequisites
Just one! You need at least Python 3.6. Use the command `python3 --version` in terminal to check your version.

## Download and Setup
Paste the commands line by line into terminal:

1. Clone the repository
```bash
git clone https://github.com/ArnavSaraogi/youtube-to-midi
cd youtube-to-midi 
```

2. Set up virtual environment and install requirements
```bash
python3 -m venv venv
source venv/bin/activate # on Windows, the command is venv\Scripts\activate
```

3. Install requirements
```bash
pip install -r requirements.txt
```

## Running the Program
Make sure you are in the youtube-to-midi folder in your terminal and that your virtual environment is activated.

### Without flags
You can run the program with
```bash
python yt-to-midi.py
```
You'll then be prompted to enter:
1. The youtube URL
2. Starting and ending times where the piano is in frame (in mm:ss format)
3. The leftmost key visible in frame (like A0, C#1, G2)
4. The name the output MIDI should have

### With flags
You can also add flags to the command to run the program immediately:
* -u or --url: the url of the video
* -r or --range: the time range when the piano is in frame (the first argument is the starting time, second is the ending time)
* -s or --start_key: the leftmost key visible in frame
* -o or --output: The name the output MIDI should have

For example:
```bash
python yt-to-midi.py -u "https://www.youtube.com/watch?v=D-X1CwyQLYo" -r 0:02 1:54 -s A0 -o la_la_land
```

### Important Notes
1. The program may take some time to run the first time you use it, but after the .py files are stored in `__pycache__` it will be faster
2. When running the program with flags, make sure that the url is in double quotes
3. Either all or none of the flags have to be included for the program to run
4. Use this image as a reference for what key label to enter for the starting key:
[![piano-key-labels.png](https://i.postimg.cc/529CtthR/piano-key-labels.png)](https://postimg.cc/RN8FsvV7)