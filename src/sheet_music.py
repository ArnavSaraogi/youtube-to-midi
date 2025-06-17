import pretty_midi
import mido
import os

# puts events in format (pitch, start, end)
def hand_assignments_to_events(hand_assignments, fps):
    events_right_hand = []
    events_left_hand = []
    active_notes = {}

    sorted_keys = sorted(hand_assignments.keys())

    for (frame, pitch) in sorted_keys:
        if pitch not in active_notes:
            active_notes[pitch] = (frame, hand_assignments[(frame, pitch)])
        else:
            pass

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

    for pitch, (start_frame, hand) in active_notes.items():
        start_time = start_frame / fps
        end_time = max(f for f, _ in hand_assignments.keys()) / fps
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

    pm.instruments.append(right_hand)
    pm.instruments.append(left_hand)

    return pm

def generate_midi(events_left_hand, events_right_hand, bpm=120, velocity=80, output="output"):
    pm = generate_pretty_midi(events_left_hand, events_right_hand, velocity)
    temp_path = "./tmp/temp.mid"
    pm.write(temp_path)
    
    mid = mido.MidiFile(temp_path)
    tempo_track = mido.MidiTrack()

    tempo = mido.bpm2tempo(bpm)
    tempo_msg = mido.MetaMessage('set_tempo', tempo=tempo, time=0)
    tempo_track.append(tempo_msg)

    mid.tracks.insert(0, tempo_track)

    os.remove(temp_path)

    os.makedirs("outputs", exist_ok=True)
    mid.save("./outputs/" + output + ".mid")
    return "./outputs/" + output + ".mid"