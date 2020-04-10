import wave
import random

from contextlib import contextmanager
from functools import lru_cache

import numpy as np
import soundcard as sc


SAMPLERATE = 44100


def sine_wave(duration, frequency, ampl=1.0, samplerate=SAMPLERATE):
    frames = int(duration * samplerate)
    x = np.linspace(0, duration, frames)
    assert len(x) == frames
    return (0.5 * ampl) * np.sin(x * frequency * np.pi * 2)


def envelope(attack_time, decay_time, sustain_level, release_time, frames):
    attack_frames = int(frames * attack_time)
    decay_frames = int(frames * decay_time)
    release_frames = int(frames * release_time)
    sustain_frames = int(frames - attack_frames - decay_frames - release_frames)
    assert frames == attack_frames + decay_frames + sustain_frames + release_frames
    return np.concatenate([
        np.linspace(0, 1, attack_frames),
        np.linspace(1, sustain_level, decay_frames),
        np.linspace(sustain_level, sustain_level, sustain_frames),
        np.linspace(sustain_level, 0, release_frames),
    ])


@lru_cache()
def play_tone(freq, duration, samplerate=SAMPLERATE):
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
    env = envelope(0.1, 0.2, 0.6, 0.2, duration*samplerate)
    wave = sine_wave(duration, 0, 0)
    for fm, am in harmonics:
        wave += sine_wave(duration, freq * fm, ampl * am, samplerate)
    wave *= env
    return wave


@lru_cache()
def lowpass_noise(cutoff, duration, samplerate=SAMPLERATE):
    frames = int(duration*samplerate)

    print('generating some noise frames', frames)
    # # low pass filter implementation without fft
    # # len(convolution) = len(signal) + len(kernel) - 1
    # kernel_half_duration = 1
    # t = np.linspace(
    #     -kernel_half_duration,
    #     kernel_half_duration,
    #     2 * kernel_half_duration * samplerate
    # )
    # kernel = 2 * cutoff * np.sinc(2 * cutoff * t)

    noise = np.random.normal(0, 0.2, frames)
    print('fft...')
    fd_noise = np.fft.rfft(noise)
    freq = np.fft.rfftfreq(noise.size, d=1/samplerate)
    print(len(freq[freq < cutoff]))
    fd_noise[freq > cutoff] = 0
    noise = np.fft.irfft(fd_noise)
    # noise = np.convolve(noise, kernel)
    print('got some noise')
    return noise


@lru_cache()
def play_drum(duration, samplerate=SAMPLERATE):
    frames = int(duration*samplerate)
    some_noise = 48 * lowpass_noise(1000, 10.0, samplerate)
    noise = some_noise[:frames]
    env = envelope(0.01, 0.1, 0.1, 0.4, frames)
    wave = env * noise
    return wave


@lru_cache()
def play_drum2(duration, samplerate=SAMPLERATE):
    frames = int(duration*samplerate)
    wave = 0.2 * np.sign(sine_wave(duration, 20, 1, samplerate))

    some_noise = lowpass_noise(4000, 10.0, samplerate)
    noise = some_noise[:frames]
    wave += noise

    env = envelope(0.1, 0.1, 1, 0.7, frames)
    wave *= env
    return wave


@lru_cache()
def silence(duration, samplerate=SAMPLERATE):
    return np.zeros(int(duration*samplerate))


def play_sequence(sequence):
    for freq, duration in sequence:
        yield play_tone(freq, duration)


def play_drumbase(beats, duration):
    for x in beats:
        if x:
            yield play_drum2(duration)
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


def make_music(stream):
    TEMPO = 120
    BASE = 60 / TEMPO
    # G A C D E G
    scale = [tone(x, 440) for x in (-2, 0, 3, 5, 7, 10)]
    bass_scale = [x / 2 for x in scale]
    while True:
        sequence = [(random.choice(scale), BASE) for x in range(16)]
        wave = np.concatenate(list(play_sequence(sequence)))

        sequence = [(random.choice(bass_scale) if x % 2 == 0 else 0, BASE)
                    for x in range(16)]
        wave += np.concatenate(list(play_sequence(sequence)))

        sequence = [(random.choice(bass_scale) if x % 4 == 0 else 0, BASE)
                    for x in range(16)]
        wave += np.concatenate(list(play_sequence(sequence)))

        # wave += np.concatenate(list(play_drumbase([1, 0, 0, 0] * 4, BASE)))

        stream.play_wave(wave)


class SoundcardOutput:
    def __init__(self, speaker):
        self.speaker = speaker

    def play_wave(self, wave):
        self.speaker.play(wave)


@contextmanager
def open_sc_stream(samplerate=SAMPLERATE):
    speaker = sc.default_speaker()
    print(speaker)
    with speaker.player(samplerate=samplerate) as player:
        # player.channels = [-1]
        yield SoundcardOutput(player)


def create_wav_file(filename):
    class MyBuffer(bytearray):
        def write(self, data):
            return self.extend(data)


    @contextmanager
    def produce_audio_for_file():
        stream = MyBuffer()
        yield stream

    def write_file(stream):
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLERATE)
            wf.setnframes(len(stream))
            wf.writeframes(stream)

    try:
        with produce_audio_for_file() as stream:
            make_music(stream)
    except KeyboardInterrupt:
        pass

    write_file(stream)


def play_music():
    try:
        with open_sc_stream() as stream:
            make_music(stream)
    except KeyboardInterrupt:
        print('interrupted.')


play_music()
# create_wav_file('davide2.wav')
