import pretty_midi
import music21
import mido
import os
import copy

# puts events in format (note, start, duration)
def hand_assignments_to_events(hand_assignments, fps):
    events_right_hand = []
    events_left_hand = []
    active_notes = {}

    # Sort by frame number to ensure proper ordering
    sorted_keys = sorted(hand_assignments.keys())

    for (frame, pitch) in sorted_keys:
        if pitch not in active_notes:
            # Note starts
            active_notes[pitch] = (frame, hand_assignments[(frame, pitch)])
        else:
            # Note is already active — continue holding
            pass

        # Check if note ends at the *next* frame by peeking ahead
        next_frame = frame + 1
        if (next_frame, pitch) not in hand_assignments:
            start_frame, hand = active_notes.pop(pitch)
            start_time = start_frame / fps
            end_time = next_frame / fps
            event = (pitch + 21, start_time, end_time)
            if hand == "left":
                events_left_hand.append(event)
            else:
                events_right_hand.append(event)

    # In case any notes are still active at the end
    for pitch, (start_frame, hand) in active_notes.items():
        start_time = start_frame / fps
        end_time = max(f for f, p in hand_assignments.keys()) / fps
        event = (pitch + 21, start_time, end_time)
        if hand == "left":
            events_left_hand.append(event)
        else:
            events_right_hand.append(event)

    return (events_left_hand, events_right_hand)

def generate_pretty_midi(events_left_hand, events_right_hand, velocity):
    pm = pretty_midi.PrettyMIDI()
    
    left_hand = pretty_midi.Instrument(program=0, name="Left Hand")
    right_hand = pretty_midi.Instrument(program=0, name="Right Hand")

    for pitch, start, end in events_left_hand:
        note = pretty_midi.Note(
            velocity=velocity,
            pitch=pitch,
            start=start,
            end=end
        )
        left_hand.notes.append(note)
    
    for pitch, start, end in events_right_hand:
        note = pretty_midi.Note(
            velocity=velocity,
            pitch=pitch,
            start=start,
            end=end
        )
        right_hand.notes.append(note) 
    
    left_hand.notes.sort(key=lambda note: note.start)
    right_hand.notes.sort(key=lambda note: note.start)

    pm.instruments.append(left_hand)
    pm.instruments.append(right_hand)

    return pm

def generate_midi(events_left_hand, events_right_hand, bpm=120, velocity=80, output_path="output.mid"):
    pm = generate_pretty_midi(events_left_hand, events_right_hand, velocity)
    temp_path = "temp.mid"
    pm.write(temp_path)
    
    mid = mido.MidiFile(temp_path)
    tempo_track = mido.MidiTrack()

    tempo = mido.bpm2tempo(bpm)
    tempo_msg = mido.MetaMessage('set_tempo', tempo=tempo, time=0)
    tempo_track.append(tempo_msg)

    mid.tracks.insert(0, tempo_track)

    os.remove(temp_path)
    mid.save(output_path)
    return output_path

def midi_to_sheet(midi_path="output.mid", key_signature=None, time_signature="4/4", output_path="output.musicxml"):
    """Simple, reliable MIDI to sheet music converter"""
    score = music21.converter.parse(midi_path)
    
    if len(score.parts) < 2:
        raise ValueError("MIDI file must have at least two parts (left and right hand).")

    # Get the parts and add proper measures
    right_hand = score.parts[1].makeMeasures()  
    left_hand = score.parts[0].makeMeasures()   
    
    # Analyze key if not provided
    if key_signature is None:
        try:
            key = score.analyze('key')
            key_signature = key.sharps
        except:
            key_signature = 0  # Default to C major if analysis fails
    
    # Create key signature and time signature objects
    ks = music21.key.KeySignature(key_signature)
    ts = music21.meter.TimeSignature(time_signature)
    
    # Set up right hand part (treble clef)
    right_hand.insert(0, music21.instrument.Piano())
    right_hand.insert(0, music21.clef.TrebleClef())
    right_hand.insert(0, ks)
    right_hand.insert(0, ts)
    right_hand.partName = 'Piano Right Hand'
    
    # Set up left hand part (bass clef)
    left_hand.insert(0, music21.instrument.Piano())
    left_hand.insert(0, music21.clef.BassClef())
    left_hand.insert(0, ks)
    left_hand.insert(0, ts)
    left_hand.partName = 'Piano Left Hand'
    
    # Create new score
    piano_score = music21.stream.Score()
    
    # Add metadata
    piano_score.insert(0, music21.metadata.Metadata())
    piano_score.metadata.title = 'Piano Score'
    piano_score.metadata.composer = 'Generated from MIDI'
    
    # Add parts to score (right hand first, then left hand)
    piano_score.append(right_hand)
    piano_score.append(left_hand)
    
    # Write to MusicXML
    piano_score.write('musicxml', fp=output_path)
    print(f"Sheet music saved to {output_path}")
    return piano_score