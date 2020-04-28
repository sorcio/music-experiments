from synth import (
    play_tone,
    play_drum2,
    play_kick,
    silence,
)


def play_sequence(sequence):
    for freq, duration in sequence:
        yield play_tone(freq, duration)


def play_drumbase(beats, duration):
    for x in beats:
        if x:
            yield play_kick(duration)
        else:
            yield silence(duration)


def tone(n, base_freq=440.0):
    #  0 A
    #  1 A#
    #  2 B
    #  3 C
    #  4 C#
    #  5 D
    #  6 D#
    #  7 E
    #  8 F
    #  9 F#
    # 10 G
    # 11 G#
    return base_freq * 2 ** (n/12)
