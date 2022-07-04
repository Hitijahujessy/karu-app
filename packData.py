from kivy.uix.image import CoreImage
import random
import pandas as pd

# backgrounds
backgrounds = {1: 'resources/backgrounds/wallpaper.png', 2: 'resources/backgrounds/wallpaper2.png', 3: 'resources/backgrounds/wallpaper3.png', 4: 'resources/backgrounds/wallpaper4.png', 5: 'resources/backgrounds/wallpaper5.png', 6: 'resources/backgrounds/wallpaper6.png', 7: 'resources/backgrounds/wallpaper7.png', 8: 'resources/backgrounds/wallpaper8.png', 9: 'resources/backgrounds/wallpaper9.png'}

# pack1
monyet = 'resources/packs/pack1/monyet.png'
tiga = 'resources/packs/pack1/tiga.png'
ruma = 'resources/packs/pack1/ruma.png'
pisang = 'resources/packs/pack1/pisang.png'
pohong ='resources/packs/pack1/pohong.png'
#nan = '/Users/jessyliewes/Pictures/Icons'
pack1 = {0: 'monyet', 1: 'tiga', 2: 'ruma', 3: 'pisang', 4: 'pohong'}
pack1img = {0: monyet, 1: tiga, 2: ruma, 3: pisang, 4: pohong}

# Pack: In huis
df = pd.read_csv('resources/packs/huis/wordlist_huis.csv')

origin = df['Nederlands'].tolist()
dest = df['Ambonese'].tolist()
imgs = df['IMG'].tolist()
print(origin)

pack_len = len(origin)
pack_origin = {}
pack_dest= {}
pack_img = {}
for i in range(pack_len):
    pack_origin[i] = origin[i]
    pack_dest[i] = dest[i]
    pack_img[i] = imgs[i]


