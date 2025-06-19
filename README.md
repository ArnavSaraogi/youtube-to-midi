# youtube-to-midi
Generate MIDI files from [Synesthesia-style](https://www.youtube.com/watch?v=QCNVEsk3pcw) Youtube videos. 

## Overview
This project uses OpenCV to identify pressed keys in Youtube piano tutorials and stores the note data in a MIDI file. Follow the instructions in [RUN.md](RUN.md) to download and run the code.

## Demo (click thumbnail to view in youtube)
[![Demo Video](https://img.youtube.com/vi/-JE1TyBCnUU/0.jpg)](https://www.youtube.com/watch?v=-JE1TyBCnUU)

## Motivation and MIDI Usage
Sheet music and MIDI files for piano tutorials on Youtube are often not free, and transcribing by hand takes time. Furthermore, methods for converting audio to MIDI can be unreliable. By relying on video rather than audio, this project enables fast, free, and accurate MIDI generation.

MIDI files can be used for creating sheet music -- just import the MIDI into MuseScore (or similar software). It can also be uploaded to Synesthesia for learning and practicing songs.

## Technical Details
1. OpenCV's Canny edge detection and thesholding methods are used to identify the piano's white and black keys in the video
2. The video is processed in the HSV colorspace
    * White key presses are determined by comparing a key's saturation to its baseline (its value in the first frame)
    * Black key presses are determined by comparing a key's value to its baseline
3. K-means clustering on hue is used to determine which hand played a note
4. The event information about notes is turned into a MIDI file with Pretty Midi

## To-Do
- [ ] Support tutorials only using one hand (ie, one color)
- [ ] Deal with "fadeaway" effect on Sheet Music Boss tutorials
- [ ] Identify when piano appears in frame so start and end times not required
- [ ] Move to processing the video without downloading it
- [ ] Optimize key press detection loop

## Limitations
Many of the tutorials on Youtube don't use exact timings when playing notes, so sheet music created using the generated MIDI may appear messy. However, with some manual adjustment in software like MuseScore, quality sheet music can be created.