import random
from fractions import Fraction
from itertools import cycle

from music import tone, play_sequence, play_drumbase, Scale, Phrase, Rhythm, NoteF
from music import NB, N1, N2, N4, N8, N16, N32, N64, N128
from instruments import kick, snare, hh, bass, violin, banjo


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


def make_music(synth):
    TIMESIG = Fraction(4, 4)
    MEASURES = 4
    scale = Scale('C', 'melodic minor')
    H, M, L = 10, 3, 1
    weights = [
        [H,L,H,L,H,L,M,H], # Cm
        [H,L,M,H,L,H,L,H], # Fmaj
        [L,H,L,M,H,L,H,L], # Gmaj
        [H,L,H,L,H,L,M,H], # Cm
        [H,L,H,L,H,L,H,H], # Cm7
        [M,H,L,H,L,H,L,H], # Dm7
        [L,H,L,H,H,L,H,L], # Gmaj
        [H,L,H,L,H,L,M,H], # Cm
    ]
    scale1 = [note.get_freq(5) for note in scale]
    scale2 = [note.get_freq(4) for note in scale]
    bass_scale1 = [note.get_freq(2) for note in scale]
    bass_scale2 = [note.get_freq(3) for note in scale]
    scale1 = scale.range('C5', 'D6')
    scale2 = scale.range('C4', 'D5')
    bass_scale1 = scale.range('C2', 'D3')
    bass_scale2 = scale.range('C3', 'D4')
    rest = NoteF('C', 0, 0)
    dominants = [0, 3, 4, 0, 0, 1, 4, 0]
    for dom, weight in zip((dominants), (weights)):
        # main melody
        r1 = Rhythm(TIMESIG, MEASURES//2).generate()
        r2 = Rhythm(TIMESIG, MEASURES//2).generate()
        rhythm = r1 + r2
        notes = [*random.choices(scale1, weight, k=len(r1)),
                 *random.choices(scale1, weight, k=len(r2))]
        melody = rhythm.add_melody(notes)

        # melody
        rhythm = Rhythm(TIMESIG, MEASURES).generate(N16, N16)
        notes = random.choices(scale1, weight, k=len(rhythm))
        melody = rhythm.add_melody(notes)

        # melody2
        rhythm = Rhythm(TIMESIG, MEASURES).generate(N16, N16)
        notes = [scale1[dom], rest, scale1[dom+3], rest] * MEASURES * 4
        melody2 = rhythm.add_melody(notes)

        # bass line 1
        rhythm = Rhythm(TIMESIG, MEASURES).generate(N8, N2)
        notes2a = random.choices(scale1, weight, k=len(rhythm))*(MEASURES//2)
        notes2b = random.choices(scale1, weight, k=len(rhythm))*(MEASURES//2)
        bass_line1 = rhythm.add_melody(notes2a + notes2b)

        # bass line 2 (slower)
        rhythm = Rhythm(TIMESIG, MEASURES).generate(N4, NB, prob=0.7, decay=0)
        weight2 = [w if w == H else 0 for w in weight]
        notes2 = random.choices(scale2, weight2, k=len(rhythm))
        #bass_line2 = Phrase.from_list(TIMESIG, zip(notes2, rhythm4))
        bass_line2 = rhythm.add_melody(notes2)

        # fillers
        filler1 = Phrase.from_pattern(TIMESIG, MEASURES, [(bass_scale1[dom], N2)])
        filler2 = Phrase.from_pattern(TIMESIG, MEASURES, [(bass_scale2[dom], N1)])

        BPM = random.choice([140, 150])
        pattern = random.choice([[1,0,0,0], [1,0,1,0], [0,1,0,1]])
        drums = [
            #play_drumbase(drumify(rhythm), duration(N8, BPM), snare),
            play_drumbase([0,1]*4*MEASURES, duration(N8, BPM), hh),
            play_drumbase([1,0]*4*MEASURES, duration(N8, BPM), kick),
            play_drumbase(pattern*MEASURES, duration(N4, BPM), snare),
        ]
        synth.play_mix([
            *drums,
            #play_sequence(melody.to_sequence(BPM), banjo),
            play_sequence(drill_pattern(melody.to_sequence(BPM), [0,1]), banjo),
            play_sequence(melody2.to_sequence(BPM), banjo),
            play_sequence(bass_line1.to_sequence(BPM), bass),
            play_sequence(bass_line2.to_sequence(BPM), bass),
            play_sequence(filler1.to_sequence(BPM), bass),
            play_sequence(filler2.to_sequence(BPM), bass),
        ])
