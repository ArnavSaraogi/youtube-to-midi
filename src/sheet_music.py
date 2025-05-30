import pretty_midi

# puts events in format (note, start, duration)
def matrix_to_events(note_matrix, fps):
    events = []
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
                events.append((pitch, start_time, end_time))
    
    for pitch, start_frame in active_notes.items():
        start_time = start_frame / fps
        end_time = len(note_matrix) / fps
        events.append((pitch, start_time, end_time))
    
    return events

def generate_midi(events, output_path="output.mid", velocity=80):
    pm = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=0)

    for pitch, start, end in events:
        note = pretty_midi.Note(
            velocity=velocity,
            pitch=pitch,
            start=start,
            end=end
        )
        instrument.notes.append(note)
    
    pm.instruments.append(instrument)
    pm.write(output_path)
    print(f"MIDI saved to {output_path}")