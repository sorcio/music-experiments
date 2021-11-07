import re
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



## Tuning ##


def tone(n, base_freq=440.0, divisions=12):
    """Return the frequency of the nth interval from base_freq (in 12-TET)."""
    # -2 -1 0  1  2  3  4  5  6  7  8  9  10 11 12
    # G  G# A  A# B  C  C# D  D# E  F  F# G  G# A
    # G  Ab A  Bb B  C  Db D  Eb E  F  Gb G  Ab A
    return base_freq * 2 ** (n/divisions)

def tet_generator(start_freq, tones):
    """Generate a list of *tones* frequencies from start_freq to start_freq*2."""
    return [tone(n, start_freq, tones) for n in range(tones)]

def map_names(tones, *names):
    """Map one or more lists of names to a list of frequencies."""
    assert all(len(tones) == len(n) for n in names)
    res = {}
    for num, ns in enumerate(zip(*names)):
        for name in ns:
            res[name] = tones[num]
    return res


# The tunings dict maps the names of different tuning systems to a tuning dict.
# Each tuning dict maps the names of the notes to a frequency.
# The name of the note can be e.g. 'C', 'Db', 'E#', or other strings, and
# does not include the octave.  Multiple names can have the same frequency.
# Each tuning dict generally (but not necessarily) cover the lowest octave
# (e.g. C0-C1) and its frequencies will be multiplied to find the
# frequencies for the other octaves.  For example, 'C7' will be calculated
# by doing: tuning_dict['C'] * (2**7), and 'DO#5' by doing:
# tuning_dict['DO#'] * (2**5).
names_sharp = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
names_flat  = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
C0 = 16.351597831287414

tunings = {
    '12TET': map_names(tet_generator(C0, 12), names_sharp, names_flat),
}
# default tuning
TUNING = tunings['12TET']



## Notes ##


note_values = [Fraction(1,2**n)/Fraction(1,2) for n in range(9)]
note_symbols = dict(zip(note_values, ''.join(map(chr, range(0x1D15C, 0x1D165)))))
rest_symbols = dict(zip(note_values, ''.join(map(chr, range(0x1D13A, 0x1D143)))))

# TODO: all these constants have corresponding symbols.
# The names could be improved and additional constants
# could be added.  Constants for rests need to be added
# too.  Different intervals can be created by multiplying
# and dividing these constants.
NB, N1, N2, N4, N8, N16, N32, N64, N128 = note_values


#TODO: figure out whether to create a separate Rest class
@functools.total_ordering
class Note:
    """A note with a name, a frequency, and an optional note value."""
    def __init__(self, name, value=None):
        self.name = name
        self.note = note = name[:-1] if name else None
        self.octave = int(name[-1]) if name and len(name) >= 2 else None
        self.freq = TUNING[note]*(2**self.octave) if note in TUNING else None
        self.value = value

    @classmethod
    def from_freq(cls, freq, value=None):
        # Try to find out if the freq has a corresponding named note,
        # by first dividing the freq until we reach the range of the
        # first octave and then by looking for a match there
        max_freq = max(TUNING.values())
        freq0 = freq
        octave = 0
        while freq0 > max_freq:
            freq0 /= 2
            octave += 1
        freq0 = round(freq0, 2)
        for name, tfreq in TUNING.items():
            if freq0 == round(tfreq, 2):
                return cls(name + str(octave), value=value)
        # if we can't find a corresponding name, set it to None
        inst = cls(None, value=value)
        inst.freq = freq
        return inst

    @classmethod
    def rest(cls, value=None):
        # TODO figure out name/octave
        inst = cls(None, value=value)
        inst.name = 'Rest'
        inst.freq = 0
        return inst

    def _to_note(self, note):
        # if note is a str, convert it to a Note inst
        return Note(note) if isinstance(note, str) else note

    def __eq__(self, other):
        return self.freq == self._to_note(other).freq

    def __lt__(self, other):
        return self.freq < self._to_note(other).freq

    def __str__(self):
        return self.name or 'Note'

    def __repr__(self):
        return f'{str(self)}({self.freq:.2f})'

    def uninote(self):
        symbols = rest_symbols if self.name == 'Rest' else note_symbols
        return symbols.get(self.value, ' ')

    def duration(self, bpm):
        return self.value / (bpm / 240.)

    def to_tuple(self, bpm):
        return (self.freq, self.duration(bpm))



## Scales ##


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

def find_next_note(note, interval):
    return next_notes[note][interval]


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


# map mode number to grade/name
mode_names = {
    1: 'I/Ionian',
    2: 'II/Dorian',
    3: 'III/Phrygian',
    4: 'IV/Lydian',
    5: 'V/Mixolydian',
    6: 'VI/Aeolian',
    7: 'VII/Locrian',
}


# TODO: currently only works with heptatonic scales
class Scale:
    def __init__(self, key, scale, mode=1):
        self.key, self.scale, self.mode = key, scale, mode

        # TODO: workaround for pentatonic scales, doesn't work for other
        # non-hepta scales and for different modes -- see also
        # https://music.stackexchange.com/q/30361 and the scale omnibus
        is_penta = scale == 'pentatonic major'
        if is_penta:
            if mode != 1:
                raise ValueError('Only the first mode is valid '
                                 'for pentatonic major scales.')
            scale = 'major'

        self.intervals = self.calc_intervals(scale, mode)
        notes = [key]
        for i in self.intervals:
            notes.append(find_next_note(notes[-1], i))
        self.notes = notes[:-1]

        if is_penta:
            # remove the 4th and 7th notes and adjust intervals
            del self.notes[(mode+5)%7]
            del self.notes[(mode+2)%7]
            self.intervals = self.calc_intervals(self.scale, mode)

    def calc_intervals(self, scale, mode):
        mode -= 1  # start from 0
        scale_intervals = intervals[scale]
        return list(islice(cycle(scale_intervals), mode,
                           mode+len(scale_intervals)))

    def __repr__(self):
        notes = " ".join(map(str, self.notes))
        return (f'<Scale key={self.key!r} scale={self.scale!r} '
                f'mode={mode_names[self.mode]!r} notes={notes!r}>')

    def __str__(self):
        return ' '.join(map(str, self.notes))

    def __iter__(self):
        return iter(self.notes)

    def __getitem__(self, index):
        return self.notes[index]

    def __len__(self):
        return len(self.notes)

    def range(self, start, end):
        start, end = Note(start), Note(end)
        if end < start:
            raise ValueError('Invalid range (end < start).')
        res = []
        for octave in range(start.octave, end.octave+1):
            for note in self.notes:
                n = Note(f'{note}{octave}')
                if start <= n < end:
                    res.append(n)
        return res



## Melodies and Rhythms ##


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
        notes = [Note.rest(v) if n.name == 'R' else Note(n.name, value=v)
                 for n, v in zip(notes, rhythm)]
        return cls(timesig, measures, notes)

    @classmethod
    def from_list(cls, timesig, list):
        notes, rhythm = zip(*list)
        measures = sum(rhythm) / timesig
        return cls.from_rhythm_and_notes(timesig, measures, rhythm, notes)

    @classmethod
    def from_pattern(cls, timesig, measures, pattern):
        plen = sum(f for n, f in pattern)
        list = pattern * int((timesig*measures) / plen)
        notes, rhythm = zip(*list)
        return cls.from_rhythm_and_notes(timesig, measures, rhythm, notes)

    @classmethod
    def from_rtttl(cls, ringtone):
        sections = ringtone.split(':')
        if len(sections) == 3:
            jintu, defaults, data = map(str.strip, sections)
        else:
            defaults, data = sections
        defaults = dict(d.split('=') for d in defaults.split(','))
        r = re.compile(r'(\d+)?([^\d.]+)(\d)?(\.)?')
        notes = []
        dur_total = Fraction(0)
        for note in map(str.strip, data.split(',')):
            m = r.match(note)
            if not m:
                raise ValueError(f'Invalid note: {note!r}')
            dur = Fraction(1, int(m[1] if m[1] is not None else defaults['d']))
            pitch = m[2].upper()
            octave = m[3] if m[3] is not None else defaults['o']
            if m[4] is not None:
                dur += dur / 2
            dur_total += dur
            n = Note.rest(dur) if pitch in {'P', 'R'} else Note(pitch+octave, dur)
            notes.append(n)
        inst = cls(Fraction(4,4), dur_total.numerator, notes)
        inst.bpm = int(defaults['b'])
        return inst


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
        # TODO: a separate function that accepts a list of
        # [(minnote, maxnote), (minnote, maxnote), ...]
        # might be better
        seq = minnote if isinstance(minnote, list) else [(minnote, maxnote)]
        func = func or gen_rhythm
        if (self.measures % len(seq)) != 0:
            raise ValueError('The number of min/max note pairs must be '
                             'a dividend of the number of measures.')
        measures = self.measures // len(seq)
        rhythm = []
        for minnote, maxnote in seq:
            rhythm.extend(func(self.timesig*measures, minnote=minnote,
                               maxnote=maxnote, prob=prob, decay=decay))
        self.rhythm = rhythm
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
