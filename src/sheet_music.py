import pretty_midi
import music21
import mido
import os
import copy

# puts events in format (note, start, duration)
def matrix_to_events(note_matrix, hand_assignments, fps):
    events_right_hand = []
    events_left_hand = []
    active_notes = {}

    for frame, keys in enumerate(note_matrix):
        for pitch, pressed in enumerate(keys):
            if pressed:
                if pitch not in active_notes:
                    active_notes[pitch] = frame
            elif pitch in active_notes:
                start_frame = active_notes.pop(pitch)
                start_time = start_frame / fps
                end_time = frame / fps
                if hand_assignments[(start_frame, pitch)] == "left":
                    events_left_hand.append((pitch + 21, start_time, end_time)) # +21 bc A0 on piano is MIDI #21
                else:
                    events_right_hand.append((pitch + 21, start_time, end_time))
    
    for pitch, start_frame in active_notes.items():
        start_time = start_frame / fps
        end_time = len(note_matrix) / fps
        if hand_assignments[(start_frame, pitch)] == "left":
            events_left_hand.append((pitch + 21, start_time, end_time))
        else:
            events_right_hand.append((pitch + 21, start_time, end_time))
    
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
    score = music21.converter.parse(midi_path)
    grand_score = music21.stream.Score()

    if len(score.parts) < 2:
        raise ValueError("MIDI file must have at least two parts (left and right hand).")

    left_notes = score.parts[0].flatten().notes
    right_notes = score.parts[1].flatten().notes

    if key_signature is None:
        key = score.analyze('key')
        key_signature = key.sharps
    
    ks = music21.key.KeySignature(key_signature)
    ts = music21.meter.TimeSignature(time_signature)

    left_hand = music21.stream.Part()
    right_hand = music21.stream.Part()

    # Insert instruments and clefs into each part at offset 0
    left_hand.insert(0, music21.instrument.Piano())
    left_hand.insert(0, music21.clef.BassClef())
    left_hand.insert(0, ks)
    left_hand.insert(0, ts)

    right_hand.insert(0, music21.instrument.Piano())
    right_hand.insert(0,music21.clef.TrebleClef())
    right_hand.insert(0, ks)
    right_hand.insert(0, ts)

    for n in left_notes:
        left_hand.append(n)
    for n in right_notes:
        right_hand.append(n)

    # Add parts to grand score
    grand_score.insert(0, right_hand)
    grand_score.insert(0, left_hand)
    
    # Add brace to group both staves
    grand_score.insert(0, music21.layout.StaffGroup(
        [left_hand, right_hand],
        name='Piano',
        abbreviation='Pno.',
        symbol='brace'
    ))

    grand_score.write('musicxml', output_path)