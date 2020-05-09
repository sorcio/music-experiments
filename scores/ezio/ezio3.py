import random
from itertools import cycle

from music import tone, play_sequence, play_drumbase, Scale
from instruments import kick, snare, hh

def gen_rhythm2(beats, prob=0.9):
    if beats == 1:
        return [1]
    if random.random() < prob:
        prob = max(prob-.2, .1)
        return [*gen_rhythm2(int(beats/2), prob), *gen_rhythm2(int(beats/2), prob)]
    else:
        return [beats]

def drill(notes):
    return [note if (random.random()>.2) else 0 for note in notes]

def drill_pattern(notes, pattern):
    return [note*p for p, note in zip(cycle(pattern), notes)]

def drumify(rhythm):
    beats = []
    for d in rhythm:
        beats.append(1)
        beats.extend([0]*(d-1))
    return beats

def make_music(synth):
    MUL = 2
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
    dominants = [0, 3, 4, 0, 0, 1, 4, 0]
    for dom, weight in zip((dominants), (weights)):
        TEMPO = random.choice([600, 700])
        #TEMPO = 600
        BASE = 60 / TEMPO
        beat_duration = random.choice([8,16])
        rhythm = gen_rhythm2(beat_duration)
        durations = [BASE*d for d in rhythm]
        hdlen = len(durations)
        notes = [*random.choices(scale1, weight, k=hdlen),
                 *random.choices(scale1, weight, k=hdlen)] * (MUL//2)
        durations *= MUL
        print(TEMPO, beat_duration, rhythm*MUL)
        assert len(durations) == len(notes), (len(durations), len(notes))
        #drums = [play_drum2(d) for d in durations]
        sequence = list(zip(drill(notes), durations))
        #print(*[f'{round(freq,1):5}/{d:2}' for (freq, d) in sequence])

        notes2 = drill_pattern(random.choices(scale2, weight, k=len(durations)), [1,0])
        sequence2 = list(zip(notes2, durations))
        sequence3 = [(bass_scale1[dom], BASE*beat_duration)]*MUL
        sequence4 = [(bass_scale2[dom], BASE*beat_duration)]*MUL

        pattern = random.choice([[1,0,0,0], [1,0,1,0], [0,1,0,1]])
        drums = [
            play_drumbase(drumify(rhythm*MUL), BASE, kick),
            play_drumbase([1]*beat_duration*2, BASE, hh),
            #play_drumbase([0,1]*(beat_duration//1), BASE, drum3),
            play_drumbase(pattern*(beat_duration//2), BASE, snare),
        ]
        sequences = [sequence, sequence2, sequence3, sequence4]
        synth.play_mix([*drums, *map(play_sequence, sequences)])

