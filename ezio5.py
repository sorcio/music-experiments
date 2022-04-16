import random

from itertools import chain
from fractions import Fraction

from music import play_sequence, play_drumbase, Scale, Melody, Rhythm, Note
from music import NB, N1, N2, N4, N8, N16, N32, N64, N128
from instruments import kick, snare, hh, bass, violin, banjo, metallic_ufo

def duration(note, tempo):
    return note / (tempo / 240.)

def untune(seq, bpm, amount):
    return ((freq+random.choice([-1,+1])*amount, duration)
            for freq, duration in seq.to_sequence(bpm))

def gen_notes(rhythm, scale):
    scale_len = len(scale)
    index = scale_len // 2
    interval = random.choice([1,2,3])
    direction = +1
    melody_notes = []
    while len(melody_notes) < len(rhythm):
        if random.random() < .3:
            direction *= -1
        #choices = []
        #if index > interval:
            #choices.append(-interval)
        #if index < scale_len-interval-1:
            #choices.append(+interval)
        #index += random.choice(choices)
        index += direction * interval
        if not (0 <= index < scale_len):
            index += -direction * (interval*2)
        melody_notes.append(scale[index])
    return melody_notes

def make_music(synth):
    TIMESIG = TS = Fraction(4, 4)
    MEASURES = MS = 4
    BPM = 110
    distortion = 0
    for k, fun in enumerate('CCEEGG'*4):
        scale = Scale(fun, 'melodic minor')
        melody_scale = scale.range(fun+'4', 'G6')
        melody2_scale = scale.range(fun+'3', 'C5')
        melody_rhythm1 = Rhythm(TS, MS//4).generate(N16, N4) * 2
        melody_rhythm2 = Rhythm(TS, MS//4).generate(N16, N4) * 2
        melody_rhythm = melody_rhythm1 + melody_rhythm2
        melody = melody_rhythm.add_notes(gen_notes(melody_rhythm, melody_scale))


        bass_rhythm = Rhythm(TIMESIG, MEASURES).generate(N8, N2)
        bass_line1 = bass_rhythm.add_notes(gen_notes(bass_rhythm, melody_scale))

        bass_rhythm = Rhythm(TIMESIG, MEASURES).generate(N4, N2)
        bass_line2 = bass_rhythm.add_notes(gen_notes(bass_rhythm, melody2_scale))

        filler1 = Melody.from_pattern(TIMESIG, MEASURES, [(Note(fun+'5'), N2)])

        if k < 6:
            distortion = 0
            patterns = [[1,0,0,0,0,0,0,0], [1,0,1,0,1,0,1,0]]
        elif k < 12:
            patterns = [[0,1,0,1,0,1,0,1], [1,1,0,0,1,1,0,0]]
        elif k < 18:
            patterns = [[0,1,0,1,1,0,0,1], [1,1,0,0,0,1,1,0], [0,1,1,1,1,0,0,1]]
        pattern = chain.from_iterable(random.choice(patterns) for n in range(MEASURES))
        if k >= 18:
            BPM += 5
            distortion += 5
            pattern = random.choices([0,1], k=MEASURES*8)

        mix = [
            #play_drumbase(drumify(rhythm), duration(N8, BPM), snare),
            play_drumbase([0,1]*4*MEASURES, duration(N8, BPM), hh),
            play_drumbase([1,0]*4*MEASURES, duration(N8, BPM), kick),
            play_drumbase(pattern, duration(N8, BPM), snare),
            play_sequence(untune(melody, BPM, distortion), banjo),
            play_sequence(bass_line1.to_sequence(BPM), bass),
            play_sequence(untune(bass_line2, BPM, distortion), violin),
            play_sequence(filler1.to_sequence(BPM), bass),
        ]
        if k >= 14:
            mix.append(play_sequence(untune(melody, BPM, distortion*1.1), banjo))
        if k >= 16:
            mix.append(play_sequence(untune(bass_line2, BPM, distortion*1.5), metallic_ufo))
        if k >= 18:
            mix.append(play_sequence(untune(melody, BPM, distortion*1.3), banjo))
            mix.append(play_sequence(untune(bass_line2, BPM, distortion*2), metallic_ufo))
        synth.play_mix(mix)
        BPM += 7
        distortion += 2

    synth.play_mix([
        play_sequence(untune(melody, BPM, distortion*1.2), bass),
        play_sequence(untune(melody, BPM, distortion*1.3), violin),
        #play_sequence(untune(melody, BPM, distortion*1.2), metallic_ufo),
        play_sequence(untune(melody, BPM, distortion*1.5), bass),
        play_sequence(untune(melody, BPM, distortion*1.7), violin),
        #play_sequence(untune(bass_line2, BPM, distortion*1.5), metallic_ufo),
    ])


    v = Melody.from_pattern(TIMESIG, MEASURES*2, [(Note(fun+'4'), NB*4)])
    synth.play_mix([
        play_sequence(untune(v, BPM, distortion*1.2), bass),
        play_sequence(untune(v, BPM, distortion*1.3), violin),
        play_sequence(untune(v, BPM, distortion*1.2), metallic_ufo),
        play_sequence(untune(v, BPM, distortion*1.5), bass),
        play_sequence(untune(v, BPM, distortion*1.7), violin),
        play_sequence(untune(v, BPM, distortion*1.5), metallic_ufo),
    ])
