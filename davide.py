import random

from music import tone, play_sequence


def make_music(synth):
    TEMPO = 120
    BASE = 60 / TEMPO
    # G A C D E G
    scale = [tone(x, 440) for x in (-2, 0, 3, 5, 7, 10)]
    bass_scale = [x / 2 for x in scale]
    while True:
        sequence1 = [(random.choice(scale), BASE) for x in range(16)]
        sequence2 = [(random.choice(bass_scale), BASE * 2) for x in range(8)]
        sequence3 = [(random.choice(bass_scale) if x % 4 == 0 else 0, BASE)
                     for x in range(16)]
        synth.play_mix(
            play_sequence(seq) for seq in [sequence1, sequence2, sequence3]
        )
