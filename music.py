from itertools import cycle, repeat, chain, islice

from synth import (
    play_tone,
    play_kick,
    silence,
)


def play_sequence(sequence, instrument=play_tone):
    for freq, duration in sequence:
        yield instrument(freq, duration)


def play_drumbase(beats, duration, drum=play_kick):
    for x in beats:
        if x:
            yield drum(duration)
        else:
            yield silence(duration)


def tone(n, base_freq=440.0):
    """Return the frequency of the nth interval from base_freq (in 12-TET)."""
    # -2 -1 0  1  2  3  4  5  6  7  8  9  10 11 12
    # G  G# A  A# B  C  C# D  D# E  F  F# G  G# A
    # G  Ab A  Bb B  C  Db D  Eb E  F  Gb G  Ab A
    return base_freq * 2 ** (n/12)


# This dict maps the name of the notes from C0 (included) to C8 (excluded)
# to the corresponding frequency (in 12-TET).
tones = [tone(i) for i in range(-57, 39)]
names_sharp = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
names_flat  = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
notes = {}

octaves = chain.from_iterable(repeat(o, 12) for o in range(8))
for t, ns, nf, o in zip(tones, cycle(names_sharp), cycle(names_flat), octaves):
    notes[f'{ns}{o}'] = notes[f'{nf}{o}'] = t


# This dict maps the names of the notes with the name of the
# following note, depending on the amount of semitones in the
# interval.  This ensures that e.g., a C will always be followed
# by a D, and that, if you go up 1 semitone from a A, you get a
# B flat  and not an A sharp.
next_notes = {
    'C':  {1: 'Db', 2: 'D', 3: 'D#'},
    'C#': {1: 'D',  2: 'D#'},
    'Db': {2: 'Eb', 3: 'E'},
    'D':  {1: 'Eb', 2: 'E', 3: 'E#'},
    'D#': {1: 'E',  2: 'E#'},
    'Eb': {1: 'Fb', 2: 'F'},
    'E':  {1: 'F',  2: 'F#'},
    'E#': {1: 'F#'},
    'Fb': {2: 'Gb', 3: 'G'},
    'F':  {1: 'Gb', 2: 'G', 3: 'G#'},
    'F#': {1: 'G',  2: 'G#'},
    'Gb': {2: 'Ab', 3: 'A'},
    'G':  {1: 'Ab', 2: 'A', 3: 'A#'},
    'G#': {1: 'A',  2: 'A#'},
    'Ab': {2: 'Bb', 3: 'B'},
    'A':  {1: 'Bb', 2: 'B', 3: 'B#'},
    'A#': {1: 'B',  2: 'B#'},
    'Bb': {1: 'Cb', 2: 'C'},
    'B':  {1: 'C',  2: 'C#'},
    'B#': {1: 'C#'},
    'Cb': {2: 'Db', 3: 'D'},
}


class Note:
    """A note with a name and no frequency/duration."""
    def __init__(self, note):
        self.note = note.note if isinstance(note, Note) else note
    def __eq__(self, other):
        return self.note == other.note
    def __hash__(self):
        return hash(self.note)
    def __repr__(self):
        return self.note
    def __str__(self):
        return self.note
    def next_note(self, interval):
        # this assumes heptatonic scales
        return Note(next_notes[self.note][interval])
    def get_freq(self, octave):
        """Return the frequency of the note at the given octave."""
        return notes[f'{self.note}{octave}']


# intervals for some common scales
intervals = {
    'major':            [2, 2, 1, 2, 2, 2, 1],
    'melodic minor':    [2, 1, 2, 2, 2, 2, 1],
    'harmonic minor':   [2, 1, 2, 2, 1, 3, 1],
    'harmonic major':   [2, 2, 1, 2, 1, 3, 1],
    'diminished':       [2, 1, 2, 1, 2, 1, 2, 1],
    'augmented':        [3, 1, 3, 1, 3, 1],
    'whole-tone':       [2, 2, 2, 2, 2, 2],
    'pentatonic major': [2, 2, 3, 2, 3],
}

# currently only works with heptatonic scales
class Scale:
    def __init__(self, key, scale, mode=1):
        self.key, self.scale, self.mode = key, scale, mode
        mode -= 1  # start from 0
        scale_intervals = intervals[scale]
        self.intervals = list(islice(cycle(scale_intervals), mode,
                                     mode+len(scale_intervals)))
        notes = [Note(key)]
        for i in self.intervals:
            notes.append(notes[-1].next_note(i))
        self.notes = notes
    #def __init__(self, key, scale, mode):
        #self.key, self.scale, self.mode = key, scale, mode
        #mode -= 1  # start from 0
        #scale_intervals = intervals[scale]
        #self.intervals = list(islice(cycle(scale_intervals), mode,
                                     #mode+len(scale_intervals)))
        #offsets = [0, *self.intervals]
        #sharps = names_sharp * 2
        #flats = names_flat * 2
        #key_offset = sharps.index(key) if key in sharps else flats.index(key)
        #self.notes = [sharps[key_offset+k] for k in accumulate(offsets)]
        #print(self.notes)
        #if any(note[0] in self.notes for note in self.notes if '#' in note):
            #self.notes = [flats[key_offset+k] for k in accumulate(offsets)]
    def __repr__(self):
        modes = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII'}
        notes = " ".join(map(str, self.notes))
        return (f'<Scale key={self.key!r} scale={self.scale!r} '
                f'mode={modes[self.mode]!r} notes={notes!r}>')
    def __str__(self):
        return ' '.join(map(str, self.notes))
    def __iter__(self):
        return iter(self.notes)
