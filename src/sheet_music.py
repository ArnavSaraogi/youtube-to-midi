import pretty_midi

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

def generate_midi(events_left_hand, events_right_hand, output_path="output.mid", velocity=80):
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

    pm.write(output_path)