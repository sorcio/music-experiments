from itertools import zip_longest
from math import sin, tau
import threading
from time import sleep, perf_counter_ns
from types import coroutine


def tone(n, base_freq=440.0):
    return base_freq * 2 ** (n/12)


async def sine_wave(frequency, max_amp, phase=0.0):
    time = phase
    on = True
    attack_samples = 400
    for i in range(attack_samples):
        amp = max_amp * 1.0 * i / attack_samples
        dt, events = await emit(amp * sin(time * frequency * tau))
        time += dt
    decay_samples = 500
    for i in range(decay_samples):
        amp = max_amp * (0.5 + 0.5 * (decay_samples - i) / decay_samples)
        dt, events = await emit(amp * sin(time * frequency * tau))
        time += dt
    while on:  # sustain
        dt, events = await emit(max_amp * 0.5 * sin(time * frequency * tau))
        time += dt
        for event, args in events:
            if event == "note_off":
                # print("note_off")
                on = False
    release_samples = 4000
    for i in range(release_samples):
        amp = max_amp * 0.5 * (release_samples - i) / release_samples
        dt, events = await emit(amp * sin(time * frequency * tau))
        time += dt


async def play_note(frequency, duration):
    bg_waves = [
        start_in_background(sine_wave(frequency * n, 0.06))
        for n in range(1, 6)
    ]
    await wait(duration)
    for bg_wave in bg_waves:
        bg_wave.note_off()


# async def play_melody():
#     from music import tone
#     TEMPO = 300
#     BASE = 60 / TEMPO
#     async with (
#       my_instrument("organ") as organ,
#       my_instrument("violin") as violin
#     ):
#         for i in range(2):
#             await organ.play_note(tone(0), BASE)
#             await organ.play_note(tone(1), BASE)
#             await organ.play_note(tone(2), BASE)
#         for i in range(2):
#             await violin.play_note(tone(0), BASE)
#             await violin.play_note(tone(1), BASE)
#             await violin.play_note(tone(2), BASE)


async def play_melody():
    TEMPO = 300
    BASE = 60 / TEMPO
    # organ = my_instrument("organ")
    # violin = my_instrument("violin")
    while True:
        # print("note 0")
        await play_note(tone(-10), BASE)
        # print("note 1")
        await play_note(tone(-6), BASE)
        # print("note 2")
        await play_note(tone(-3), BASE)
    # for i in range(2):
    #     await violin.play_note(tone(0), BASE)
    #     await violin.play_note(tone(1), BASE)
    #     await violin.play_note(tone(2), BASE)


@coroutine
def wait(duration):
    yield "wait", duration


@coroutine
def emit(frame):
    return (yield "emit", frame)


loop_state = threading.local()


class Task:
    def __init__(self, coro):
        self.coro = coro
        self.events = []
        self.started = False

    def execute_step(self, dt):
        if not self.started:
            self.started = True
            return self.coro.send(None)
        else:
            events = self.collect_events()
            return self.coro.send((dt, events))

    def send_event(self, event_name, args):
        self.events.append((event_name, args))

    def collect_events(self):
        events = self.events
        self.events = []
        return events

    def __getattr__(self, name):
        def _method(**kwargs):
            self.send_event(name, kwargs)
        return _method

    def __repr__(self):
        return f"<Task {self.coro}>"


def start_in_background(coro):
    task = Task(coro)
    # print("starting task", task)
    loop_state.ready.append(task)
    return task


def run(afn):
    dt = 1 / 44_100
    ready = []
    loop_state.ready = ready
    waiting = []
    start_in_background(afn())
    sample_number = 0
    # timings = []
    while ready or waiting:
        # timing_start = time.perf_counter_ns()
        while waiting and waiting[0][0] <= sample_number:
            deadline, task = waiting.pop(0)
            # print(f"awakening task {task} at {sample_number} (dl: {deadline})")
            ready.append(task)
        mix = 0.0
        next_frame = []
        while ready:
            task = ready.pop()
            try:
                command, data = task.execute_step(dt)
            except StopIteration:
                # print(f"task ended {task} at {sample_number}")
                pass
            else:
                if command == "wait":
                    wait_duration = data
                    wait_samples = int(wait_duration / dt)
                    wait_deadline = sample_number + wait_samples
                    waiting.append((wait_deadline, task))
                    waiting.sort()
                elif command == "emit":
                    mix += data
                    next_frame.append(task)
                else:
                    raise RuntimeError(f"what is {command!r} what do you want")
        ready.extend(next_frame)
        # timing_end = time.perf_counter_ns()
        # sample_time = timing_end - timing_start
        # timings.append(sample_time)
        # if sample_number and sample_number % 88200 == 0:
        #     _print_timing_stats(timings)
        #     timings = []
        yield mix
        sample_number += 1


def _print_timing_stats(timings):
    from statistics import mean, stdev
    timing_mean = mean(timings)
    timing_stdev = stdev(timings)
    timing_max = max(timings)
    timing_min = min(timings)
    print(
        f"{timing_mean=:.0f} {timing_stdev=:.0f}"
        f" {timing_max=:.0f} {timing_min=:.0f} "
    )


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def main():
    buffer_duration = 0.1
    BUFFER_SIZE = int(44100 * buffer_duration)
    from synth import open_sc_stream
    with open_sc_stream(buffer_duration=buffer_duration) as output:
        synth_generator = run(play_melody)
        for chunk in grouper(synth_generator, BUFFER_SIZE, 0):
            output.play_wave(chunk)


if __name__ == "__main__":
    main()
