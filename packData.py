"""A module that is used for storing and accessing data for KaruApp

This module stores different data that is used in KaruApp. It also divides the
word list DataFrames into seperate dictionary.

"""
from kivy.storage.jsonstore import JsonStore
import pandas as pd

store = JsonStore('resources/user_data.json')

# backgrounds
backgrounds = {1: 'resources/backgrounds/wallpaper.png', 2: 'resources/backgrounds/wallpaper2.png',
               3: 'resources/backgrounds/wallpaper3.png', 4: 'resources/backgrounds/wallpaper4.png',
               5: 'resources/backgrounds/wallpaper5.png', 6: 'resources/backgrounds/wallpaper6.png',
               7: 'resources/backgrounds/wallpaper7.png', 8: 'resources/backgrounds/wallpaper8.png',
               9: 'resources/backgrounds/wallpaper9.png', 10: 'resources/backgrounds/wallpaper10.png',
               11: 'resources/backgrounds/wallpaper11.png', 12: 'resources/backgrounds/wallpaper12.png'}

current_bg = store.get("background")["current_bg"]

# Current pack (category)
df = pd.read_csv(store.get("current_pack")["source"])

# Language titles for settings screen
language_names = {"Dutch": "Dutch - Nederlands",
                  "English": "English",
                  "German": "German - Deutsch",
                  "Russian": "Russian - Русский",
                  "Indonesian": "Indonesian - Bahasa Indonesia",
                  "French": "French - Français",
                  "Korean": "Korean - 한국어",
                  "Japanese": "Japanese - 日本語",
                  "Spanish": "Spanish - Español",
                  "Italian": "Italian - Italiano",
                  "Ambonese": "Ambonese Malay - Ambon Malayu"}

origin_lang = store.get("origin_lang")["language"]
dest_lang = store.get("dest_lang")["language"]
origin = df[origin_lang].tolist()
dest = df[store.get("dest_lang")["language"]].tolist()
imgs = df['IMG'].tolist()
print("module", origin)
print("module", dest)

pack_len = len(origin)
pack_origin = {}
pack_dest = {}
pack_img = {}
for i in range(pack_len):
    pack_origin[i] = origin[i]
    pack_dest[i] = dest[i]
    pack_img[i] = imgs[i]
