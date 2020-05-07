import random
from fractions import Fraction
from itertools import cycle

from music import tone, play_sequence, play_drumbase, Scale, Melody, Rhythm, NoteF
from music import NB, N1, N2, N4, N8, N16, N32, N64, N128
from instruments import kick_hard, kick, snare, hh, bass, violin, banjo


def drill_pattern(seq, pattern):
    return ((freq*p, dur) for p, (freq,dur) in zip(cycle(pattern), seq))

def drumify(rhythm):
    beats = []
    for d in rhythm:
        beats.append(1)
        beats.extend([0]*(d-1))
    return beats

def duration(note, tempo):
    return note / (tempo / 240.)

def gen_notes(rhythm, scale, index=None):
    scale_len = len(scale)
    #index = index or scale_len // 2
    interval = 1
    direction = +1
    melody_notes = []
    while len(melody_notes) < len(rhythm):
        if random.random() < .3:
            direction *= -1
        #choices = []
        #if index > interval:
            #choices.append(-interval)
        #if index < scale_len-interval-1:
            #choices.append(+interval)
        #index += random.choice(choices)
        index += direction * interval
        if not (0 <= index < scale_len):
            index += -direction * (interval*2)
        melody_notes.append(scale[index])
    return melody_notes, index

def make_music(synth):
    TIMESIG = Fraction(4, 4)
    MEASURES = 1
    scale = Scale('C', 'major')
    H, M, L = 10, 6, 6
    #I-V-vi-iii-IV-I-IV-V
    #c g a e f c f g
    chords = [1, 5, 6, 3, 4, 1, 4, 5]
    indexes = [c-1 for c in chords]  # 0-based
    weights = [[H,L,H,L,H,L,L,H,L,H,L,H,L,L][i:i+7] for i in indexes]
    scale0 = scale.range('C6', 'C7')
    scale1 = scale.range('C5', 'C6')
    scale2 = scale.range('C4', 'C5')
    bass_scale1 = scale.range('C2', 'C3')
    bass_scale2 = scale.range('C3', 'C4')
    rest = NoteF('C', octave=0, freq=0)
    last_index = 0
    for dom, weight in zip((indexes*4), (weights*4)):
        # main melody
        rhythm = Rhythm(TIMESIG, MEASURES).generate(N4, N4)
        notes, last_index = gen_notes(rhythm, scale1, last_index)
        melody = rhythm.add_notes(notes)

        # bass line 1
        rhythm = Rhythm(TIMESIG, MEASURES).generate(N8, N2)
        notes = random.choices(scale2, weight, k=len(rhythm))*MEASURES
        bass_line1 = rhythm.add_notes(notes)

        # bass line 2 (slower)
        rhythm = Rhythm(TIMESIG, MEASURES).generate(N4, NB, prob=0.7, decay=0)
        weight2 = [w if w == H else 0 for w in weight]
        notes2 = random.choices(scale2, weight2, k=len(rhythm))
        #bass_line2 = Melody.from_list(TIMESIG, zip(notes2, rhythm4))
        bass_line2 = rhythm.add_notes(notes2)

        # fillers
        filler1 = Melody.from_pattern(TIMESIG, MEASURES, [(scale1[dom], N2)])
        filler2 = Melody.from_pattern(TIMESIG, MEASURES, [(scale2[dom], N1)])

        BPM = 130
        pattern = random.choice([[1,0,0,0], [1,0,1,0], [0,1,0,1]])
        drums = [
            #play_drumbase(drumify(rhythm), duration(N8, BPM), snare),
            play_drumbase([0,1]*4*MEASURES, duration(N8, BPM), hh),
            play_drumbase([1,0]*8*MEASURES, duration(N16, BPM), kick_hard),
            play_drumbase([0,1]*8*MEASURES, duration(N16, BPM), kick),
            play_drumbase(pattern*MEASURES, duration(N4, BPM), snare),
        ]
        synth.play_mix([
            *drums,
            play_sequence(melody.to_sequence(BPM), banjo),
            #play_sequence(drill_pattern(melody.to_sequence(BPM), [0,1]), banjo),
            #play_sequence(melody2.to_sequence(BPM), banjo),
            play_sequence(bass_line1.to_sequence(BPM), bass),
            #play_sequence(bass_line2.to_sequence(BPM), bass),
            play_sequence(filler1.to_sequence(BPM), bass),
            play_sequence(filler2.to_sequence(BPM), violin),
        ])
