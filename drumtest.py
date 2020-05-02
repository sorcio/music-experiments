import random
from itertools import product

from music import play_drumbase
from instruments import play_drum1, play_drum2, play_drum3, play_kick

def make_music(synth):
    tempos = [400, 600, 900]
    drums = [play_drum2, play_drum3, play_kick]
    for tempo, drum in product(tempos, drums):
        BASE = 60 / tempo
        beats = 16
        pattern = random.choice([[1,0,0,0], [1,0,1,0], [0,1,0,1]])
        synth.play_mix([
            play_drumbase([1]*beats*2, BASE, drum),
            #play_drumbase([1,0]*beats), BASE, drum)
            #play_drumbase(pattern*beats, BASE, drum)
        ])
