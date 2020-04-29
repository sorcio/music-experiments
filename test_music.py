import pytest

from music import Note, Scale

major_scales = {
    'Cb': ['Cb', 'Db', 'Eb', 'Fb', 'Gb', 'Ab', 'Bb', 'Cb'],
    'Gb': ['Gb', 'Ab', 'Bb', 'Cb', 'Db', 'Eb', 'F', 'Gb'],
    'Db': ['Db', 'Eb', 'F', 'Gb', 'Ab', 'Bb', 'C', 'Db'],
    'Ab': ['Ab', 'Bb', 'C', 'Db', 'Eb', 'F', 'G', 'Ab'],
    'Eb': ['Eb', 'F', 'G', 'Ab', 'Bb', 'C', 'D', 'Eb'],
    'Bb': ['Bb', 'C', 'D', 'Eb', 'F', 'G', 'A', 'Bb'],
    'F': ['F', 'G', 'A', 'Bb', 'C', 'D', 'E', 'F'],
    'C': ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C'],
    'G': ['G', 'A', 'B', 'C', 'D', 'E', 'F#', 'G'],
    'D': ['D', 'E', 'F#', 'G', 'A', 'B', 'C#', 'D'],
    'A': ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#', 'A'],
    'E': ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#', 'E'],
    'B': ['B', 'C#', 'D#', 'E', 'F#', 'G#', 'A#', 'B'],
    'F#': ['F#', 'G#', 'A#', 'B', 'C#', 'D#', 'E#', 'F#'],
    'C#': ['C#', 'D#', 'E#', 'F#', 'G#', 'A#', 'B#', 'C#'],
}
major_scales = {key: [Note(n) for n in notes]
                for key, notes in major_scales.items()}

@pytest.mark.parametrize(('key', 'notes'), major_scales.items())
def test_major_scales_mode_I(key, notes):
    assert Scale(key, 'major', mode=1).notes == notes


@pytest.mark.parametrize(('key', 'notes'), major_scales.items())
@pytest.mark.parametrize('mode', range(1,8))
def test_major_scales_modes(key, notes, mode):
    assert set(Scale(key, 'major', mode=1).notes) == set(Scale(notes[mode-1], 'major', mode=mode).notes)


heptatonic_scales = {
    'major':            ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C'],
    'melodic minor':    ['C', 'D', 'Eb', 'F', 'G', 'A', 'B', 'C'],
    'harmonic minor':   ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'B', 'C'],
    'harmonic major':   ['C', 'D', 'E', 'F', 'G', 'Ab', 'B', 'C'],
}
heptatonic_scales = {scale: [Note(n) for n in notes]
                     for scale, notes in heptatonic_scales.items()}

@pytest.mark.parametrize(('scale', 'notes'), heptatonic_scales.items())
def test_heptatonic_scales(scale, notes):
    assert Scale('C', scale, mode=1).notes == notes

other_scales = {
    'diminished':       ['C', 'D', 'Eb', 'F', 'F#', 'G#', 'A', 'B', 'C'],
    'augmented':        ['C', 'D#', 'E', 'G', 'Ab', 'B', 'C'],
    'whole-tone':       ['C', 'D', 'E', 'F#', 'G#', 'Bb', 'C'],
    'pentatonic major': ['C', 'D', 'E', 'G', 'A', 'C'],
}
other_scales = {scale: [Note(n) for n in notes]
                for scale, notes in other_scales.items()}

@pytest.mark.xfail
@pytest.mark.parametrize(('scale', 'notes'), other_scales.items())
def test_other_scales(scale, notes):
    assert Scale('C', scale, mode=1).notes == notes
