import pytest

from music import Note, Scale, N8

notes = [
    ('C0', 'C', 0, 16.351597831287414),
    ('C1', 'C', 1, 32.70319566257483),
    ('C8', 'C', 8, 4186.009044809578),
    ('Ab0', 'Ab', 0, 25.956543598746567),
    ('A0', 'A', 0, 27.5),
    ('A#0', 'A#', 0, 29.135235094880617),
    ('A4', 'A', 4, 440),
]

@pytest.mark.parametrize('name, note, octave, freq', notes)
def test_note_init(name, note, octave, freq):
    n = Note(name)
    assert n.name == name == str(name)
    assert n.note == note
    assert n.octave == octave
    assert pytest.approx(n.freq) == freq
    assert n.value == None

def test_note_init_with_value():
    n = Note('A4', N8)
    assert n.name == 'A4'
    assert n.note == 'A'
    assert n.octave == 4
    assert pytest.approx(n.freq) == 440
    assert n.value == N8

def note_names():
    for note in 'ABCDEFG':
        for octave in '012345678':
            if note not in {'E', 'B'}:
                yield note + '#' + octave
            yield note + octave
            if note not in {'F', 'C'}:
                yield note + 'b' + octave

@pytest.mark.parametrize('name', note_names())
def test_note_from_freq(name):
    n1 = Note(name)
    n2 = Note.from_freq(n1.freq)
    assert n1 == n2
    assert n2.name is not None

@pytest.mark.parametrize('value', [None, N8])
def test_note_from_freq_no_name(value):
    n = Note.from_freq(435, value)
    assert n.name == None
    assert n.note == None
    assert n.octave == None
    assert n.freq == 435
    assert n.value == value


def test_note_repr():
    assert repr(Note('A4')) == 'A4(440.00)'
    assert repr(Note.from_freq(435)) == 'Note(435.00)'

def test_note_uninote():
    assert Note('A4', N8).uninote() == '𝅘𝅥𝅮'
    assert Note.rest(N8).uninote() == '𝄾'


@pytest.mark.parametrize('note', [Note('A4', N8), Note.rest(N8)])
def test_note_duration(note):
    assert note.duration(60) == 0.5
    assert note.duration(120) == 0.25

def test_note_to_tuple():
    assert Note('A4', N8).to_tuple(120) == (439.99999999999994, 0.25)
    assert Note.rest(N8).to_tuple(120) == (0, 0.25)


@pytest.mark.parametrize('value', [None, N8])
def test_note_rest(value):
    n = Note.rest(value)
    assert n.name == 'Rest'
    assert n.note == None
    assert n.octave == None
    assert n.freq == 0
    assert n.value == value

@pytest.fixture
def cmajor():
    return Scale('C', 'major', mode=1)

def test_scale_iter(cmajor):
    assert list(cmajor) == cmajor.notes

def test_scale_len(cmajor):
    assert len(cmajor) == len(cmajor.notes)

def test_scale_getitem(cmajor):
    assert [cmajor[k] for k in range(len(cmajor))] == list(cmajor)

def test_scale_range(cmajor):
    r = cmajor.range('C4', 'C5')
    assert len(r) == 7
    assert r[0] == 'C4'
    assert r[-1] == 'B4'
    assert all(n.octave == 4 for n in r)

@pytest.mark.parametrize('end', ['C4', 'G3'])
def test_scale_invalid_range(cmajor, end):
    with pytest.raises(ValueError):
        cmajor.range('G4', end)

major_scales = {
    'Cb': ['Cb', 'Db', 'Eb', 'Fb', 'Gb', 'Ab', 'Bb'],
    'Gb': ['Gb', 'Ab', 'Bb', 'Cb', 'Db', 'Eb', 'F'],
    'Db': ['Db', 'Eb', 'F', 'Gb', 'Ab', 'Bb', 'C'],
    'Ab': ['Ab', 'Bb', 'C', 'Db', 'Eb', 'F', 'G'],
    'Eb': ['Eb', 'F', 'G', 'Ab', 'Bb', 'C', 'D'],
    'Bb': ['Bb', 'C', 'D', 'Eb', 'F', 'G', 'A'],
    'F': ['F', 'G', 'A', 'Bb', 'C', 'D', 'E'],
    'C': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
    'G': ['G', 'A', 'B', 'C', 'D', 'E', 'F#'],
    'D': ['D', 'E', 'F#', 'G', 'A', 'B', 'C#'],
    'A': ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#'],
    'E': ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#'],
    'B': ['B', 'C#', 'D#', 'E', 'F#', 'G#', 'A#'],
    'F#': ['F#', 'G#', 'A#', 'B', 'C#', 'D#', 'E#'],
    'C#': ['C#', 'D#', 'E#', 'F#', 'G#', 'A#', 'B#'],
}

@pytest.mark.parametrize(('key', 'notes'), major_scales.items())
def test_major_scales_mode_I(key, notes):
    assert Scale(key, 'major', mode=1).notes == notes

@pytest.mark.parametrize(('key', 'notes'), major_scales.items())
@pytest.mark.parametrize('mode', range(1, 8))
def test_major_scales_modes(key, notes, mode):
    # When the number of the mode matches the position (1-based)
    # of the note in the scale, the resulting notes are the same,
    # but shifted, e.g.:
    # key=C (1st note), mode=1: C D E F G A B
    # key=D (2nd note), mode=2: D E F G A B C
    # key=E (3rd note), mode=3: E F G A B C D
    # Verify that this is true for each key/mode combination
    assert (set(Scale(key, 'major', mode=1).notes) ==
            set(Scale(notes[mode-1], 'major', mode=mode).notes))


heptatonic_scales = {
    'major':            ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
    'melodic minor':    ['C', 'D', 'Eb', 'F', 'G', 'A', 'B'],
    'harmonic minor':   ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'B'],
    'harmonic major':   ['C', 'D', 'E', 'F', 'G', 'Ab', 'B'],
}

@pytest.mark.parametrize(('scale', 'notes'), heptatonic_scales.items())
def test_heptatonic_scales(scale, notes):
    assert Scale('C', scale, mode=1).notes == notes

other_scales = {
    'diminished':       ['C', 'D', 'Eb', 'F', 'F#', 'G#', 'A', 'B'],
    'augmented':        ['C', 'D#', 'E', 'G', 'Ab', 'B'],
    'whole-tone':       ['C', 'D', 'E', 'F#', 'G#', 'Bb'],
    'pentatonic major': ['C', 'D', 'E', 'G', 'A'],
}

@pytest.mark.xfail
@pytest.mark.parametrize(('scale', 'notes'), other_scales.items())
def test_other_scales(scale, notes):
    assert Scale('C', scale, mode=1).notes == notes
