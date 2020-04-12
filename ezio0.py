import random
import itertools

from music import tone, play_sequence


def gen_rythm(beats):
    while True:
        res = random.choices([1,2,4,8], (32,8,2,1),
                             k=random.choice([4,8,16,32]))
        if sum(res) == beats:
            return res


def gen_rythm2(beats):
    if beats == 1:
        return [1]
    if random.random() < 0.9:
        return [*gen_rythm2(int(beats/2)), *gen_rythm2(int(beats/2))]
    else:
        return [beats]


def make_music(synth):
    MUL = 4
    I = (0, 3, 5, 7, 10)  # A C D E G
    IV = (9, 12, 14, 16, 19)  # F# A B C# E
    V = (16, 19, 21, 23, 26)  # C# E F# G# B
    scale_I = [tone(x, 440) for x in I]
    scale_IV = [tone(x, 440) for x in IV]
    scale_V = [tone(x, 440) for x in V]
    for scale in itertools.cycle([scale_I, scale_IV, scale_V, scale_V]):
        TEMPO = random.choice([300, 400, 600])
        BASE = 60 / TEMPO
        bass_scale = [x / 4 for x in scale]
        beat_duration = random.choice([4,8,16,32])
        durations = [BASE*d for d in gen_rythm2(beat_duration)]
        hdlen = len(durations)
        notes = [*random.choices(scale, (5,5,3,1,1), k=hdlen)*2,
                 *random.choices(scale, (1,1,3,5,5), k=hdlen)*2]
        durations *= MUL
        print(len(durations), len(notes))
        sequence = list(zip(notes, durations))
        #print(*[f'{round(freq,1):5}/{d:2}' for (freq, d) in sequence])

        sequence2 = [(random.choice(scale) if x % 2 == 0 else 0, BASE*int(MUL/2))
                     for x in range(beat_duration*int(MUL/2))]
        sequence3 = [(bass_scale[0], BASE*MUL) for x in range(beat_duration)]
        synth.play_mix(
            play_sequence(seq) for seq in [sequence, sequence2, sequence3]
        )
