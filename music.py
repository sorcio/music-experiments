import random
import functools

from fractions import Fraction
from itertools import cycle, repeat, chain, islice

from instruments import default_tone, kick, silence


def play_sequence(sequence, instrument=default_tone):
    for freq, duration in sequence:
        yield instrument(freq, duration)


def play_drumbase(beats, duration, drum=kick):
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
        other_note = other.note if isinstance(other, Note) else other
        return self.note == other_note
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


# TODO: figure out how to represent and name:
# 1) notes with just a name (e.g. C, E#, or Ab)
# 2) notes on a keyboard, with name and octave/freq
# 3) notes on a keyboard with a note value (as fraction)
# 4) frequencies without a corresponding note
# 1, 2, and 3 are currently represented by Note, NoteF, NoteFV
# but are subject to change in future versions

@functools.total_ordering
class NoteF(Note):
    def __init__(self, note, *, octave=None, freq=None):
        # TODO: split this into two separate constructors
        # and figure out if the freq belongs here
        if octave is not None and freq is not None:
            self.note, self.octave, self.freq = note, octave, freq
        else:
            self.note = note[:-1]
            self.octave = int(note[-1])
            self.freq = notes[note].freq
    def __eq__(self, other):
        return self.freq == other.freq
    def __lt__(self, other):
        return self.freq < other.freq
    def __str__(self):
        return f'{self.note}{self.octave}'
    def __repr__(self):
        return f'{self.note}{self.octave}({self.freq:.2f})'


# This dict maps the name of the notes from C0 (included) to C8 (excluded)
# to the corresponding frequency (in 12-TET).
tones = [tone(i) for i in range(-57, 39)]
names_sharp = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
names_flat  = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
notes = {}

octaves = chain.from_iterable(repeat(o, 12) for o in range(8))
for t, ns, nf, o in zip(tones, cycle(names_sharp), cycle(names_flat), octaves):
    #notes[f'{ns}{o}'] = notes[f'{nf}{o}'] = t
    # TODO: this creates a weird loop with NoteF, figure out a better way
    notes[f'{ns}{o}'] = NoteF(ns, octave=o, freq=t)
    notes[f'{nf}{o}'] = NoteF(nf, octave=o, freq=t)


class NoteFV(NoteF):
    """A note with a frequency and a note value (as fraction)."""
    def __init__(self, note, value, *, octave=None, freq=None):
        super().__init__(note, octave=octave, freq=freq)
        self.value = value  # note value as a fraction

    def uninote(self):
        return note_symbols.get(self.value, ' ')

    def duration(self, bpm):
        return self.value / (bpm / 240.)

    def to_tuple(self, bpm):
        return (self.freq, self.duration(bpm))


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

    def __repr__(self):
        modes = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII'}
        notes = " ".join(map(str, self.notes))
        return (f'<Scale key={self.key!r} scale={self.scale!r} '
                f'mode={modes[self.mode]!r} notes={notes!r}>')

    def __str__(self):
        return ' '.join(map(str, self.notes))

    def __iter__(self):
        return iter(self.notes)

    def range(self, start, end):
        start, end = NoteF(start), NoteF(end)
        # TODO: improve error checking/reporting
        assert start.octave <= end.octave
        return [n for n in notes.values()
                if n.note in self.notes and start <= n < end]



note_values = [Fraction(1,2**n)/Fraction(1,2) for n in range(9)]
note_symbols = dict(zip(note_values, ''.join(map(chr, range(0x1D15C, 0x1D165)))))
rest_symbols = dict(zip(note_values, ''.join(map(chr, range(0x1D13A, 0x1D143)))))

# TODO: all these constants have corresponding symbols.
# The names could be improved and additional constants
# could be added.  Constants for rests need to be added
# too.  Different intervals can be created by multiplying
# and dividing these constants.
NB, N1, N2, N4, N8, N16, N32, N64, N128 = note_values


# TODO: figure out how to handle generative algos and other
# operations (e.g. repetition, serialization, etc.)

# There are 3 main classes:
# * Rhythm: represent a list of note values as fractions
# * Notes: represent a list of notes without note values
# * Melody: represent a list of notes and corresponding values
# "Note value" indicates the relative duration of a note as a fraction

class Melody:
    """A sequence of notes with a rhythm."""
    def __init__(self, timesig, measures, notes=None):
        self.timesig = timesig
        self.measures = measures
        self.notes = notes

    @classmethod
    def from_rhythm_and_notes(cls, timesig, measures, rhythm=None, notes=None):
        notes = [NoteFV(n.note, d, octave=n.octave, freq=n.freq)
                 for n, d in zip(notes, rhythm)]
        return cls(timesig, measures, notes)

    @classmethod
    def from_list(cls, timesig, list):
        notes, rhythm = zip(*list)
        measures = sum(notes) / timesig
        return cls.from_rhythm_and_notes(timesig, measures, rhythm, notes)

    @classmethod
    def from_pattern(cls, timesig, measures, pattern):
        plen = sum(f for n, f in pattern)
        list = pattern * int((timesig*measures) / plen)
        notes, rhythm = zip(*list)
        return cls.from_rhythm_and_notes(timesig, measures, rhythm, notes)

    def __add__(self, other):
        if self.timesig != other.timesig:
            raise ValueError(f'Mismatching time signatures '
                             f'({self.timesig!s} and {other.timesig!s})')
        return Melody(self.timesig, self.measures+other.measures,
                      self.notes+other.notes)

    def __mul__(self, value):
        return Melody(self.timesig, self.measures*value, self.notes*value)

    def __imul__(self, value):
        self.notes *= value
        return self

    def to_sequence(self, bpm):
        return (n.to_tuple(bpm) for n in self.notes)


def gen_rhythm(duration, minnote=N16, maxnote=NB, prob=0.9, decay=0.1):
    if duration <= minnote:
        return [duration]
    if duration >= maxnote or random.random() < prob:
        prob = max(prob-decay, .1)
        return [*gen_rhythm(duration/2, minnote, maxnote, prob),
                *gen_rhythm(duration/2, minnote, maxnote, prob)]
    else:
        return [duration]


class Rhythm:
    """A rhythm as a sequence of note values (fractions)."""
    def __init__(self, timesig, measures, rhythm=None):
        self.timesig = timesig
        self.measures = measures
        self.rhythm = rhythm

    def __add__(self, other):
        if self.timesig != other.timesig:
            raise ValueError(f'Mismatching time signatures '
                             f'({self.timesig!s} and {other.timesig!s}).')
        rhythm = self.rhythm + other.rhythm
        return Rhythm(self.timesig, self.measures+other.measures, rhythm)

    def __mul__(self, value):
        rhythm = self.rhythm * value if self.rhythm else None
        return Rhythm(self.timesig, self.measures*value, rhythm)

    def __len__(self):
        return len(self.rhythm)

    def generate(self, minnote=N16, maxnote=NB, prob=0.9, decay=0.1, func=None):
        # TODO: it might be better to leave generation outside
        # of the class, and define functions that return a
        # Rhythm instance instead
        func = func or gen_rhythm
        self.rhythm = func(self.timesig*self.measures, minnote=minnote,
                           maxnote=maxnote, prob=prob, decay=decay)
        return self

    def pattern(self, pattern):
        repetitions = (self.timesig * self.measures) / sum(pattern)
        if repetitions.denominator != 1:
            raise ValueError('Invalid pattern lenght.')
        self.rhythm = pattern * repetitions
        return self

    def add_notes(self, notes):
        notes = notes.notes if isinstance(notes, Notes) else notes
        return Melody.from_rhythm_and_notes(self.timesig, self.measures, self.rhythm, notes)

    def uninotes(self, fastest=None):
        line, sep = '─', '│'
        fastest = fastest or min(self.rhythm)
        total = 0
        result = ['├─']
        for f in self.rhythm:
            result.append(f'{note_symbols[f]:{line}<{int(f/fastest)}}')
            total += f
            if total == self.timesig:
                result.append('─┼─')
                total = 0
        result[-1] = '─┤'
        return ''.join(result)


class Notes:
    """A sequence of notes with no rhythm."""
    def __init__(self, notes=None):
        self.notes = notes

    def __add__(self, other):
        notes = other.notes if isinstance(other, Notes) else other
        return Notes(self.notes + notes)

    def __mul__(self, value):
        notes = self.notes * value if self.notes else None
        return Notes(notes)

    def __len__(self):
        return len(self.notes)
