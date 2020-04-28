from contextlib import contextmanager
from functools import lru_cache, partial
import threading
import wave

import numpy as np
import soundcard as sc


SAMPLERATE = 44100  # default sample rate


def sine_wave(duration, frequency, ampl=1.0, samplerate=SAMPLERATE):
    frames = int(duration * samplerate)
    x = np.linspace(0, duration, frames)
    assert len(x) == frames
    return (0.5 * ampl) * np.sin(x * frequency * np.pi * 2)


def envelope(attack_time, decay_time, sustain_level, release_time, frames, samplerate=SAMPLERATE, msecs=False):
    assert isinstance(frames, int)

    if msecs is True:
        attack_frames = np.clip(int(attack_time / 1000 * samplerate), 0, None)
        decay_frames = np.clip(int(decay_time / 1000 * samplerate), 0, None)
        release_frames = np.clip(int(release_time / 1000 * samplerate), 0, None)
        sustain_frames = 0
        padding_frames = np.clip(frames - attack_frames - decay_frames - release_frames, 0, None)
    else:
        attack_frames = int(frames * attack_time)
        decay_frames = int(frames * decay_time)
        release_frames = int(frames * release_time)
        sustain_frames = frames - attack_frames - decay_frames - release_frames
        padding_frames = 0

    return np.concatenate([
        np.linspace(0, 1, attack_frames),
        np.linspace(1, sustain_level, decay_frames),
        np.linspace(sustain_level, sustain_level, sustain_frames),
        np.linspace(sustain_level, 0, release_frames),
        np.linspace(0, 0, padding_frames)
    ])[:frames]


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
    wave = sine_wave(duration, 0, 0)
    for fm, am in harmonics:
        wave += sine_wave(duration, freq * fm, ampl * am, samplerate)
    env = envelope(0.1, 0.2, 0.6, 0.2, len(wave))
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
def bandpass_noise(cutoffl, cutoffh, duration, samplerate=SAMPLERATE):
    frames = int(duration*samplerate)
    print('generating some noise frames', frames)
    noise = np.random.normal(0, 0.2, frames)
    print('fft...')
    fd_noise = np.fft.rfft(noise)
    freq = np.fft.rfftfreq(noise.size, d=1/samplerate)
    fd_noise[freq < cutoffl] = 0
    fd_noise[freq > cutoffh] = 0
    noise = np.fft.irfft(fd_noise)
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
def play_kick(duration, samplerate=SAMPLERATE):
    frames = int(duration*samplerate)
    wave = 0.6 * sine_wave(duration, 60, 1, samplerate)
    wave += 0.6 * sine_wave(duration, 90, 1, samplerate)

    bp_noise = [
        (0.35, [300, 750]),
        (0.45, [1700, 8000]),
        (0.15, [8000, 11500])
    ]
    for ampl, (freql, freqh) in bp_noise:
        some_noise = ampl * bandpass_noise(freql, freqh, duration+.1, samplerate)
        noise = some_noise[:frames]
        wave += noise

    env = envelope(0.08, 0.1, 0.15, 0.7, frames)
    wave *= env
    return wave


@lru_cache()
def silence(duration, samplerate=SAMPLERATE):
    return np.zeros(int(duration*samplerate))


class Synth:
    def __init__(self, output):
        self.output = output

    def play(self, *args):
        self.play_mix(args)

    def play_mix(self, mix):
        wave = sum(np.concatenate(list(map(list, waves))) for waves in mix)
        self.output.play_wave(wave)

    def play_wave(self, wave):
        self.output.play_wave(wave)


class Queue0:
    """Bufferless Queue"""

    def __init__(self):
        self.mutex = threading.Lock()
        self.not_empty = threading.Condition(self.mutex)
        self.not_full = threading.Condition(self.mutex)
        self.waiters = 0
        self.data = []

    def put(self, item, interrupt_delay=None):
        with self.not_full:
            while not self.waiters:
                self.not_full.wait(timeout=interrupt_delay)
            self.waiters -= 1
            self.data.append(item)
            self.not_empty.notify()

    def get(self, interrupt_delay=None):
        with self.not_empty:
            self.waiters += 1
            self.not_full.notify()
            while not self.data:
                self.not_empty.wait(timeout=interrupt_delay)
            item = self.data.pop()
            return item

    def __iter__(self):
        return self

    def __next__(self):
        return self.get()


class SoundcardOutput:
    def __init__(self, speaker):
        self.speaker = speaker
        self.thread = None

    def play_wave(self, wave):
        self.queue.put(wave, interrupt_delay=0.1)

    def __enter__(self):
        if self.thread:
            raise RuntimeError("already running")
        self.queue = Queue0()
        self.thread = threading.Thread(target=self._feed_thread, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *args):
        pass

    def _feed_thread(self):
        for item in self.queue:
            self.speaker.play(item)


@contextmanager
def open_sc_stream(samplerate=SAMPLERATE, buffer_duration=1.0):
    speaker = sc.default_speaker()
    print(speaker)
    blocksize = int(samplerate * buffer_duration)
    with speaker.player(samplerate=samplerate, blocksize=blocksize) as player:
        # player.channels = [-1]
        with SoundcardOutput(player) as output:
            yield output


class MyBuffer(bytearray):
    def play_wave(self, data):
        self.extend(np.int16(np.clip(data, -1, 1) * 32767))


def _write_wav_file(filename, sample_rate, stream):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.setnframes(len(stream))
        wf.writeframes(stream)


@contextmanager
def create_wav_file(filename, sample_rate=SAMPLERATE):
    stream = MyBuffer()
    try:
        yield Synth(stream)
    finally:
        _write_wav_file(filename, sample_rate, stream)


@contextmanager
def open_soundcard_synth(sample_rate=SAMPLERATE):
    with open_sc_stream() as stream:
        yield Synth(stream)


def run_synth(callable, output=None, **kwargs):
    if output is None:
        context_function = open_soundcard_synth
    elif isinstance(output, str):
        context_function = partial(create_wav_file, output)
    try:
        with context_function(**kwargs) as synth:
            callable(synth)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        module = sys.argv[1]
        run_synth(__import__(module).make_music)
    if len(sys.argv) == 3:
        module = sys.argv[1]
        filename = sys.argv[2]
        run_synth(__import__(module).make_music, output=filename)
