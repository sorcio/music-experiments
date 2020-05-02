from functools import lru_cache

import numpy as np

from synth import (SAMPLERATE, sine_wave, envelope_ms, release_time,
                   lowpass_noise, bandpass_noise)


@lru_cache()
def default_tone(freq, duration, samplerate=SAMPLERATE):
    # # high freq att:
    # # 0.0 : 0.99 = 110 : 880
    # attenuation = min(max((freq - 110) / 770 * 0.99, 0.0), 0.99)
    # ampl = 1 - attenuation
    ampl = 0.5
    harmonics = [
        # (freqmult, amplmult)
        (1.0, 0.5),
        # (2.0, 0.2),
        # (4.0, 0.1),
        (1.01, 0.3),
        (0.2, 0.3),
        (0.5, 0.2),
        (0.25, 0.1),
    ]
    wave = sine_wave(duration, 0, 0)
    for fm, am in harmonics:
        wave += sine_wave(duration, freq * fm, ampl * am, samplerate)
    atk = 15
    dcy = 20
    sus = 0.6
    rel = release_time(atk, dcy, len(wave))
    #return wave * envelope(0.1, 0.2, 0.6, 0.2, len(wave))
    return wave * envelope_ms(atk, dcy, sus, rel, len(wave))


@lru_cache()
def banjo(freq, duration, samplerate=SAMPLERATE):
    ampl = 0.38
    harmonics = [
        # (freqmult, amplmult)
        (1.0, 0.5),
        (1.25, 0.2),  # major third
        (1.5, 0.3),   # perfect fifth
        (0.75, 0.2),  # perfect fifth
        (0.25, 0.3),  # octave
    ]
    wave = sine_wave(duration, 0, 0)
    for fm, am in harmonics:
        wave += sine_wave(duration, freq * fm, ampl * am, samplerate)
    atk = 0
    dcy = 1
    sus = 0.9
    rel = release_time(atk, dcy, len(wave))
    return wave * envelope_ms(atk, dcy, sus, rel, len(wave))


@lru_cache()
def metallic_ufo(freq, duration, samplerate=SAMPLERATE):
    ampl = 0.5
    harmonics = [
        # (freqmult, amplmult)
        (1.0, 0.7),
        # minor sevenths
        (1.8, 0.2),
        (0.9, 0.3),
        # thirds
        (2.5, 0.1),
        (1.25, 0.4),
        (0.625, 0.5),
        # perfect fifths
        (1.5, 0.1),
        (0.75, 0.2),
        # octaves
        (0.5, 0.15),
        (0.25, 0.15),
        (0.125, 0.15),
    ]
    wave = sine_wave(duration, 0, 0)
    for fm, am in harmonics:
        wave += sine_wave(duration, freq * fm, ampl * am, samplerate)
    atk = 1
    dcy = 1
    sus = 0.8
    rel = release_time(atk, dcy, len(wave))
    return wave * envelope_ms(atk, dcy, sus, rel, len(wave))


@lru_cache()
def violin(freq, duration, samplerate=SAMPLERATE):
    ampl = 0.3
    harmonics = [
        # (freqmult, amplmult)
        (4, 0.05),    # octave
        (2, 0.4),     # octave
        (1.5, 0.3),   # perfect fifth
        (1.0, 0.6),
        (0.75, 0.3),  # perfect fifth
        (0.5, 0.3),   # octave
        (1.25, 0.1),  # octave
    ]
    wave = sine_wave(duration, 0, 0)
    for fm, am in harmonics:
        wave += sine_wave(duration, freq * fm, ampl * am, samplerate)
    atk = 120
    dcy = 30
    sus = 0.8
    rel = release_time(atk, dcy, len(wave))
    return wave * envelope_ms(atk, dcy, sus, rel, len(wave))


@lru_cache()
def drum1(duration, samplerate=SAMPLERATE):
    frames = int(duration*samplerate)
    some_noise = 48 * lowpass_noise(1000, 10.0, samplerate)
    noise = some_noise[:frames]
    return noise * envelope(0.01, 0.1, 0.1, 0.4, frames)


@lru_cache()
def kick_hard(duration, samplerate=SAMPLERATE):
    frames = int(duration*samplerate)
    wave = 0.6 * sine_wave(duration, 60, 1, samplerate)
    wave += 0.6 * sine_wave(duration, 90, 1, samplerate)

    bp_noise = [
        (0.4, [300, 750]),
        (0.45, [1700, 8000]),
        (0.15, [8000, 11500])
    ]
    for ampl, (freql, freqh) in bp_noise:
        some_noise = ampl * bandpass_noise(freql, freqh, duration+.1, samplerate)
        wave += some_noise[:frames]

    # envelope(0.08, 0.1, 0.05, 0.7, frames)
    return wave * envelope_ms(10, 20, 0.05, 175, frames) * 1.4


@lru_cache()
def kick(duration, samplerate=SAMPLERATE):
    frames = int(duration*samplerate)
    wave = 0.6 * sine_wave(duration, 60, 1, samplerate)
    wave += 0.6 * sine_wave(duration, 90, 1, samplerate)

    bp_noise = [
        (0.5, [300, 750]),
        (0.20, [1700, 8000]),
        (0.05, [8000, 11500])
    ]
    for ampl, (freql, freqh) in bp_noise:
        some_noise = ampl * bandpass_noise(freql, freqh, duration+.1, samplerate)
        wave += some_noise[:frames]

    # envelope(0.08, 0.1, 0.05, 0.7, frames)
    return wave * envelope_ms(10, 20, 0.05, 175, frames) * 1.6


@lru_cache()
def snare(duration, samplerate=SAMPLERATE):
    frames = int(duration*samplerate)
    top_wave = 0.15 * sine_wave(duration, 120, 1, samplerate)
    top_wave += 0.35 * sine_wave(duration, 160, 1, samplerate)
    atk = 3
    dcy = 25
    sus = 0.2
    top_wave *= envelope_ms(atk, dcy, sus, 100, frames)

    btm_wave = sine_wave(duration, 0, 1, samplerate)
    bp_noise = [
        (0.25, [300, 800]),
        (0.15, [1200, 2400]),
        (0.20, [4000, 8000]),
        (0.15, [8000, 12000]),
    ]
    for ampl, (freql, freqh) in bp_noise:
        some_noise = ampl * bandpass_noise(freql, freqh, duration+.1, samplerate)
        btm_wave += some_noise[:frames]

    sus = 0.45
    rel = release_time(atk, dcy, len(btm_wave))
    btm_wave *= envelope_ms(atk, dcy, sus, min(200, rel), frames)

    return (top_wave + btm_wave) * 2.3


@lru_cache()
def hh(duration, samplerate=SAMPLERATE):
    frames = int(duration*samplerate)
    wave = sine_wave(duration, 0, 1, samplerate)

    bp_noise = [
        (0.3, [200, 500]),
        (0.4, [2000, 4500]),
        (0.5, [6000, 16000])
    ]
    for ampl, (freql, freqh) in bp_noise:
        some_noise = ampl * bandpass_noise(freql, freqh, duration+.1, samplerate)
        wave += some_noise[:frames]

    return wave * envelope_ms(10, 30, 0.05, 50, frames) * 0.5


@lru_cache()
def bass(freq, duration, samplerate=SAMPLERATE):
    ampl = 0.5
    bass_wave = sine_wave(duration, 0, 1)
    harmonics = [
        (0.125, 0.5),
        (0.25, 0.3),
        (0.5, 0.03),
        (1.0, 0.01)
    ]
    for fm, am in harmonics:
        bass_wave += sine_wave(duration, freq * fm, ampl * am)

    atk = 10
    dcy = 0
    sus = 1
    rel = release_time(atk, dcy, len(bass_wave))
    bass_wave *= envelope_ms(atk, dcy, sus, rel, len(bass_wave))

    # pick_wave = sine_wave(duration, freq, ampl * 0.01)
    # pick_wave += sine_wave(duration, freq * 2, ampl * 0.005)

    # atk = 10
    # dcy = 15
    # sus = 0.1
    # rel = release_time(atk, dcy, len(pick_wave))
    # pick_wave *= envelope_ms(atk, dcy, sus, rel, len(pick_wave))

    return bass_wave # + pick_wave


@lru_cache()
def silence(duration, samplerate=SAMPLERATE):
    return np.zeros(int(duration*samplerate))
