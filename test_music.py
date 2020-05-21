import pytest

from music import Scale


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
