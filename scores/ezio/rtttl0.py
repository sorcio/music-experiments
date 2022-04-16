from music import play_sequence, Melody
from instruments import banjo

def make_music(synth):
    rtttls = [
        ('tetris:d=4,o=5,b=160:e6,8b,8c6,8d6,16e6,16d6,8c6,8b,a,8a,8c6,e6,8d6,'
         '8c6,b,8b,8c6,d6,e6,c6,a,2a,8p,d6,8f6,a6,8g6,8f6,e6,8e6,8c6,e6,8d6,'
         '8c6,b,8b,8c6,d6,e6,c6,a,a'),
        ('imperialmarch:d=8,o=5,b=120:4a4,4a4,4a4,f.4,16c,4a4,f.4,16c,2a4,4e,'
         '4e,4e,f.,16c,4g#4,f.4,16c,2a4,4a,a.4,16a4,4a,g#.,16g,16f#,16e,f,p,'
         'a#4,4d#,d.,16c#,16c,16b4,c,p,f4,4g#4,f.4,16a4,4c,a.4,16c,2e,4a,a.4,'
         '16a4,4a,g#.,16g,16f#,16e,f,p,a#4,4d#,d.,16c#,16c,16b4,c,p,f4,4g#4,'
         'f.4,16c,4a4,f.4,16c,2a4'),
        ('starwars:d=4,o=5,b=180:8f,8f,8f,2a#.,2f.6,8d#6,8d6,8c6,2a#.6,f.6,'
         '8d#6,8d6,8c6,2a#.6,f.6,8d#6,8d6,8d#6,2c6,p,8f,8f,8f,2a#.,2f.6,8d#6,'
         '8d6,8c6,2a#.6,f.6,8d#6,8d6,8c6,2a#.6,f.6,8d#6,8d6,8d#6,2c6'),
        ('smb:d=4,o=5,b=100:16e6,16e6,32p,8e6,16c6,8e6,8g6,8p,8g,8p,8c6,16p,'
         '8g,16p,8e,16p,8a,8b,16a#,8a,16g.,16e6,16g6,8a6,16f6,8g6,8e6,16c6,'
         '16d6,8b,16p,8c6,16p,8g,16p,8e,16p,8a,8b,16a#,8a,16g.,16e6,16g6,8a6,'
         '16f6,8g6,8e6,16c6,16d6,8b,8p,16g6,16f#6,16f6,16d#6,16p,16e6,16p,'
         '16g#,16a,16c6,16p,16a,16c6,16d6,8p,16g6,16f#6,16f6,16d#6,16p,16e6,'
         '16p,16c7,16p,16c7,16c7,p,16g6,16f#6,16f6,16d#6,16p,16e6,16p,16g#,'
         '16a,16c6,16p,16a,16c6,16d6,8p,16d#6,8p,16d6,8p,16c6'),
        ('ffvii_boss:d=4,o=5,b=112:16a4,16a4,16a4,8c.,16a4,16a4,16a4,8d.,'
         '16a4,16a4,16a4,16d#,16d,16c,16d,16c,16b4,8c,16b4,16a4,16a4,16a4,'
         '8c.,16a4,16a4,16a4,8d.,16a4,16a4,16a4,16d#,16d,16c,16d,16c,16b4,'
         '8c,16b4,16c,16c,16c,8d#.,16c,16c,16c,8f.,16c,16c,16c,16f#,16f,16d#,'
         '16f,16d#,16d,8d#,16d,16c,16c,16c,8d#.,16c,16c,16c,8f.,16c,16c,16c,'
         '16f#,16f,16d#,16f,16d#,16d,16d#,16d,16c'),
        ('simpsons:d=4,o=5,b=160:c.6, e6, f#6, 8a6, g.6, e6, c6, 8a, 8f#, '
         '8f#, 8f#, 2g, 8p, 8p, 8f#, 8f#, 8f#, 8g, a#., 8c6, 8c6, 8c6, c6'),
    ]
    for rtttl in rtttls:
        melody = Melody.from_rtttl(rtttl)
        synth.play_mix([
            play_sequence(melody.to_sequence(melody.bpm), banjo),
        ])
