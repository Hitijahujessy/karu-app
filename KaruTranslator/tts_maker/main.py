
import pandas as pd
from gtts import gTTS
import os

# Test translating an entire list to multiple languages, and adding them to a dataframe

#wordlist = ['Huis', 'Deur', 'Lamp', 'Bed', 'Bank', 'Stoel', 'Televisie', 'Keuken', 'Douche', 'Wc']  # In huis
#data = {'Nederlands': wordlist}
df = pd.read_csv('wordlist_huis.csv')

lang_dict = {'English': 'en', 'German': 'de', 'Russian': 'ru', 'Indonesian': 'id', 'French': 'fr', 'Chinese': 'cn', 'Korean': 'ko', 'Japanese': 'ja', 'Spanish': 'es', 'Italian': 'it', 'Ambonese': 'id'}
wordlist = df['Spanish']
spoken_lang = 'es'

print(df[list(lang_dict.keys())[0]])
# for x in range(len(lang_dict)): # loop through all languages in lang_list

    # dir_name = 'langs' + list(lang_dict.keys())[x].lower()
    # if not os.path.exists(dir_name):
    #     os.mkdir(dir_name)

#index = list(lang_dict.keys())[x]
#current_lang = lang_dict[index]
print(f'Creating audio files for Spanish') #{index}...\n')

for i in range(len(df['English'])):
        tts = gTTS(wordlist[i], lang=spoken_lang)
        tts.save('langsspanish/' + wordlist[i] + '.mp3')
        print(f'Entry {(i+1)} complete.')



print('File created!')

# with pd.option_context('display.max_rows', None,
#                        'display.max_columns', None,
#                        'display.precision', 3,
#                        ):
#
#     print('\n', df)
