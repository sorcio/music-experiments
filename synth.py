import wave
import threading

from pathlib import Path
from importlib import import_module
from functools import lru_cache, partial
from contextlib import contextmanager

import numpy as np
# import soundcard as sc
import sounddevice as sd


SAMPLERATE = 44100  # default sample rate


def sine_wave(duration, frequency, ampl=1.0, samplerate=SAMPLERATE):
    frames = int(duration * samplerate)
    x = np.linspace(0, duration, frames)
    assert len(x) == frames
    return (0.5 * ampl) * np.sin(x * frequency * np.pi * 2)


def release_time(atk, dcy, samplelen, samplerate=SAMPLERATE):
    return samplelen / samplerate * 1000 - (atk + dcy)


def envelope(attack_time, decay_time, sustain_level, release_time, frames):
    assert isinstance(frames, int)

    attack_frames = int(frames * attack_time)
    decay_frames = int(frames * decay_time)
    release_frames = int(frames * release_time)
    sustain_frames = frames - attack_frames - decay_frames - release_frames
    return np.concatenate([
        np.linspace(0, 1, attack_frames),
        np.linspace(1, sustain_level, decay_frames),
        np.linspace(sustain_level, sustain_level, sustain_frames),
        np.linspace(sustain_level, 0, release_frames),
    ])


def envelope_ms(attack_time, decay_time, sustain_level, release_time, frames, samplerate=SAMPLERATE):
    assert isinstance(frames, int)

    attack_frames = int(attack_time / 1000 * samplerate)
    decay_frames = int(decay_time / 1000 * samplerate)
    release_frames = int(release_time / 1000 * samplerate)
    padding_frames = frames - attack_frames - decay_frames - release_frames

    attack_frames = np.clip(attack_frames, 0, None)
    decay_frames = np.clip(decay_frames, 0, None)
    release_frames = np.clip(release_frames, 0, None)
    padding_frames = np.clip(padding_frames, 0, None)
    return np.concatenate([
        np.linspace(0, 1, attack_frames),
        np.linspace(1, sustain_level, decay_frames),
        np.linspace(sustain_level, 0, release_frames),
        np.linspace(0, 0, padding_frames)
    ])[:frames]


@lru_cache()
def lowpass_noise(cutoff, duration, samplerate=SAMPLERATE):
    frames = int(duration*samplerate)

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
    fd_noise = np.fft.rfft(noise)
    freq = np.fft.rfftfreq(noise.size, d=1/samplerate)
    print(len(freq[freq < cutoff]))
    fd_noise[freq > cutoff] = 0
    noise = np.fft.irfft(fd_noise)
    # noise = np.convolve(noise, kernel)
    return noise


@lru_cache()
def bandpass_noise(cutoffl, cutoffh, duration, samplerate=SAMPLERATE):
    frames = int(duration*samplerate)
    noise = np.random.normal(0, 0.2, frames)
    fd_noise = np.fft.rfft(noise)
    freq = np.fft.rfftfreq(noise.size, d=1/samplerate)
    fd_noise[freq < cutoffl] = 0
    fd_noise[freq > cutoffh] = 0
    noise = np.fft.irfft(fd_noise)
    return noise


class Synth:
    def __init__(self, output):
        self.output = output

    def play(self, *args):
        self.play_mix(args)

    def play_mix(self, mix):
        concatenated = [np.concatenate(list(map(list, waves))) for waves in mix]
        longest = len(max(concatenated, key=lambda x: len(x)))
        for idx, ary in enumerate(concatenated):
            zeros = np.zeros([longest-len(ary)])
            concatenated[idx] = np.block([ary, zeros])

        self.output.play_wave(sum(concatenated))

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


class OutputDevice:
    def __init__(self):
        self.thread = None
        self.__terminated = False

    def __enter__(self):
        if self.thread:
            raise RuntimeError("already running")
        self.queue = Queue0()
        self.thread = threading.Thread(target=self._feed_thread, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.__terminated = True

    @property
    def terminated(self):
        return self.__terminated


class SoundcardOutput(OutputDevice):
    def __init__(self, speaker):
        super().__init__()
        self.speaker = speaker

    def play_wave(self, wave):
        self.queue.put(wave, interrupt_delay=0.1)

    def _feed_thread(self):
        for item in self.queue:
            self.speaker.play(item)


class SounddeviceOutput(OutputDevice):
    def __init__(self, device=None, *, blocksize=8192, channels=2):
        super().__init__()
        self.device = device
        self.channels = channels
        self.buffer = np.empty(0)
        self.blocksize = blocksize

    def play_wave(self, wave):
        bs = self.blocksize
        wave = np.concatenate((self.buffer, wave))
        for x in range(0, len(wave), bs):
            chunk = wave[x:x+bs]
            if len(chunk) >= bs:
                self.queue.put(chunk, interrupt_delay=0.1)
            else:
                self.buffer = chunk

    def _feed(self, outdata, frames, time, status):
        outdata[:, 0] = self.queue.get()

    def _feed_thread(self):
        with sd.OutputStream(device=self.device, blocksize=self.blocksize,
            samplerate=SAMPLERATE, channels=self.channels,
            callback=self._feed, latency="low"):
            while not self.terminated:
                sd.sleep(1)


@contextmanager
def open_sc_stream(samplerate=SAMPLERATE, buffer_duration=1.0):
    speaker = sc.default_speaker()
    print(speaker)
    blocksize = int(samplerate * buffer_duration)
    with speaker.player(samplerate=samplerate, blocksize=blocksize) as player:
        # player.channels = [-1]
        with SoundcardOutput(player) as output:
            yield output


@contextmanager
def open_sd_stream(samplerate=SAMPLERATE, buffer_duration=0.4):
    blocksize = int(samplerate * buffer_duration)
    with SounddeviceOutput(channels=1, blocksize=blocksize) as output:
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
    # with open_sc_stream() as stream:
    with open_sd_stream() as stream:
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
    # TODO: use argparse
    import sys
    outfile = None
    if len(sys.argv) >= 2:
        scorename = sys.argv[1]
    if len(sys.argv) == 3:
        outfile = sys.argv[2]
    # TODO: handle multiple scores with the same name
    scorefile = next(f for f in Path('.').glob('**/*.py') if f.stem == scorename)
    # scores/ezio/ezio0.py -> scores.ezio.ezio0
    module = '.'.join([*scorefile.parent.parts, scorefile.stem])
    run_synth(import_module(module).make_music, output=outfile)
