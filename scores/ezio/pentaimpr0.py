import random

from itertools import chain
from fractions import Fraction

from music import play_sequence, play_drumbase, Scale, Melody, Rhythm, Note
from music import NB, N1, N2, N4, N8, N16, N32, N64, N128
from instruments import kick, snare, hh, bass, violin, banjo, metallic_ufo, pure_sin

def gen_notes(rhythm, scale):
    scale_len = len(scale)
    index = scale_len // 2
    direction = +1
    melody_notes = []
    while len(melody_notes) < len(rhythm):
        interval = random.choice([0,0,1,1,1,2,2,2,3])
        if random.random() < .3:
            direction *= -1
        index += direction * interval
        if not (0 <= index < scale_len):
            index += -direction * (interval*2)
        melody_notes.append(scale[index])
    return melody_notes


def duration(note, tempo):
    return note / (tempo / 240.)


def make_music(synth):
    TIMESIG = TS = Fraction(4, 4)
    MEASURES = MS = 16
    BPM = 110
    backing_scale = Scale('C', 'major').range('C3', 'C6')
    melody_scale = Scale('C', 'pentatonic major').range('C4', 'C7')

    # C F Am G
    arpeggio = ('C3 E3 G3 C4 E3 G3 C4 E4 '
                'C3 E3 A3 C4 E3 A3 C4 E4 '
                'C3 F3 A3 C4 F3 A3 C4 E4 '
                'D3 G3 B3 D4 G3 B3 D4 G4').split()
    notes = [Note(n) for n in arpeggio] * (MS//2)
    rhythm = Rhythm(TS, MS).generate(N16, N16)

    backing_melody = rhythm.add_notes(notes)

    melody_rhythm = Rhythm(TS, MS).generate([(N16, N2), (N16, N4)])
    melody = melody_rhythm.add_notes(gen_notes(melody_rhythm, melody_scale))

    pattern = random.choice([[1,0,0,0], [1,0,1,0], [0,1,0,1]])
    drums = [
        play_drumbase([0,1]*4*MEASURES, duration(N8, BPM), hh),
        play_drumbase([1,0]*4*MEASURES, duration(N8, BPM), kick),
        play_drumbase(pattern*MEASURES, duration(N4, BPM), snare),
    ]

    synth.play_mix([
        *drums,
        play_sequence(backing_melody.to_sequence(BPM), pure_sin),
        play_sequence(melody.to_sequence(BPM), pure_sin),
    ])
