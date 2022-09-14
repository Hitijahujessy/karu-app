# Using kivy 2.0.0 and python3.8
# -*- coding: utf-8 -*-


import importlib
import os
from functools import partial

import kivy

from kivy.config import Config  # For setting height (19.5:9)
from kivy.factory import Factory
from kivy.graphics import Rectangle, RoundedRectangle, Color, InstructionGroup
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout

from kivy.app import App
from kivy.lang import Builder

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.core.audio import SoundLoader
from kivy.uix.video import Video

from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock  # For retrieving playtime and getting score
from kivy.storage.jsonstore import JsonStore

import random
import time

import karuData
import packData

kivy.require('2.0.0')  # Version of Kivy)
# os.environ["KIVY_VIDEO"] = "ffpyplayer" #audio_ffpyplayer, audio_sdl2 (audio_gstplayer, audio_avplayer ignored)
Config.set('graphics', 'width', '360')  # (New Android smartphones e.g. OnePlus 7 series)
Config.set('graphics', 'height', '640')  # (iPhone X, 11 and 12 series, upsampled)
store = JsonStore('resources/user_data.json')  # For saving high score
root_widget = Builder.load_file('layout.kv')


# root_widget = Builder.load_string(open("layout.kv", encoding="utf-8").read(), rulesonly=True)


# os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'  # If necessary, uncomment to prevent OpenGL error

# Mascot
class KaruWidget(Widget):
    data = karuData
    speech = data.starttext
    pass


class GameWidget(Screen, FloatLayout):
    importlib.reload(packData)

    karu = KaruWidget()
    # click_sound = SoundLoader.load('resources/Sounds/click_button.wav')

    time = NumericProperty()  # Time taken per image

    points = NumericProperty(50)  # Points per level
    score = NumericProperty()  # Total score
    highscore = NumericProperty(store.get('data')['highscore'])  # Total score
    highscore_label = ObjectProperty()

    wallet = NumericProperty(store.get('wallet')['coins'])
    wallet_label = ObjectProperty()  # In-game label where wallet is viewed
    payout = NumericProperty(10)  # Max amount of coins per level

    coins = NumericProperty(0)  # Amount of coins earned in current level
    coins_total = NumericProperty(0)  # Amount of coins earned in current game
    mistakes = 0  # Amount of mistakes, used for awarding coins

    flawless = False  # Check if score is perfect (<5sec, no hints, no mistakes)

    level_finish = False  # Bool to check if current level is cleared

    bg = ObjectProperty()
    bg = store.get('background')['current_bg']

    # All buttons, most efficient way I could find for now
    letterBtn1 = ObjectProperty(None)
    letterBtn2 = ObjectProperty(None)
    letterBtn3 = ObjectProperty(None)
    letterBtn4 = ObjectProperty(None)
    letterBtn5 = ObjectProperty(None)
    letterBtn6 = ObjectProperty(None)
    letterBtn7 = ObjectProperty(None)
    letterBtn8 = ObjectProperty(None)
    letterBtn9 = ObjectProperty(None)
    letterBtn10 = ObjectProperty(None)
    letterBtn11 = ObjectProperty(None)
    letterBtn12 = ObjectProperty(None)
    letterBtn13 = ObjectProperty(None)
    letterBtn14 = ObjectProperty(None)
    letterBtn15 = ObjectProperty(None)
    letterBtn16 = ObjectProperty(None)
    letterBtn17 = ObjectProperty(None)
    letterBtn18 = ObjectProperty(None)
    letterBtn18 = ObjectProperty(None)

    # Button to go to next level if level_finish == True
    next_button = ObjectProperty(None)

    help_button = ObjectProperty(None)
    app_start = True
    start_btn = ObjectProperty(None)

    game_finish = False
    game_pause = BooleanProperty(True)
    go_to_menu = False
    early_stop = 0

    # i = letterBtn pressed (i.e. i = 0 = letterBtn1)
    i = 0

    # Label for viewing answer (when blank = '_____

    # Image widget for viewing current image
    imagewidget = ObjectProperty(None)

    # WORDS Function #

    # import module packData, containing image's and corresponding words, also randomize index for variation
    data = packData
    originlist = data.pack_origin
    wordlist = data.pack_dest  # Current list of words
    indexlist = list(wordlist.keys())  # Index current word
    random.shuffle(indexlist)
    level = 0
    index = indexlist[level]

    # Word for current level
    currentWord = wordlist[index]
    currentWordOrigin = originlist[index]
    word = ''
    print(currentWord, currentWordOrigin)

    # Image for current level
    currentImage = data.pack_img[index]

    mainlanglabel = ObjectProperty()

    # Used to assign letters to buttons
    letters_btn = currentWord
    print(letters_btn)

    # Used as text for label
    emptyspace = ('_' * len(currentWord))
    grid = GridLayout()
    grid_exist = False
    wordbuttons = []
    charpos = 0  # pos of pressed wordbutton
    answer_to_check = []

    # character location used for backspace and help
    charloc = 0

    # Hints
    hints = 500  # Total amount of hint per game
    hints_used = 0  # Amount of hints used in level
    sound_hint = 5
    sound_used = 0

    skip = False

    def __init__(self, **kwargs):

        super(GameWidget, self).__init__(**kwargs)

        # Start randomizeLetters() to randomize and add letters to letterBtns
        # self.randomizeLetters()

    # Function for changing words and images when answer correct
    def words(self):

        # Check if level is cleared
        # if self.level_finish:

        if self.hints >= 1:
            self.help_button.disabled = False

        self.level_finish = False  # New level started, level finish = false

        if self.sound_hint == 0:
            self.ids.sound_button.disabled = True
        else:
            self.ids.sound_button.disabled = False

        self.time = 0
        self.coins = 0
        self.mistakes = 0
        self.skip = False

        self.currentWord = self.wordlist[self.index]  # New word
        self.currentImage = self.data.pack_img[self.index]  # Corresponding image
        self.currentWordOrigin = self.originlist[self.index]
        self.mainlanglabel.text = self.currentWordOrigin
        self.emptyspace = ('_' * len(self.currentWord))  # Set empty space ('-') to len(currentWord)

        print("function words()", self.currentWord, self.currentWordOrigin, self.emptyspace)
        # Clear answer label

        self.letters_btn = self.currentWord
        print(self.letters_btn)

        self.imagewidget.source = self.currentImage
        # print(self.currentWord)  # Test if currentWord is updated
        # print(self.currentImage)  # Test if currentImage is updated
        # print(self.emptyspace)  # Test if empty space is updated

        self.randomizeLetters()  # Randomize letters for buttons

    # Function for randomizing letters for buttons
    def randomizeLetters(self):

        self.mainlanglabel.text = self.currentWordOrigin
        print("fucntion randomizeLetters()", self.currentWordOrigin, self.mainlanglabel.text)

        if not self.grid_exist:
            self.grid = GridLayout(rows=1, cols=len(self.currentWord), spacing=10, size_hint_x=.55, size_hint_y=.075,
                                   pos_hint={'center_x': .5, 'center_y': .45})
            self.add_widget(self.grid)
            self.grid_exist = True
            print('grid created')
        if self.grid_exist:
            self.answer_to_check = []
            self.wordbuttons = []
            self.charloc = 0
            self.grid.clear_widgets(children=None)
            self.remove_widget(self.grid)
            self.grid = GridLayout(rows=1, cols=len(self.currentWord), spacing=10, size_hint_x=.55, size_hint_y=.075,
                                   pos_hint={'center_x': .5, 'center_y': .45})
            self.add_widget(self.grid)

            print('grid cleared')

        self.start_time()

        self.sound_used = 0

        self.remove_widget(self.next_button)
        self.imagewidget.opacity = 1

        all_letters = list("abcdefghijklmnopqrstuvwxyz")  # Possible letters for randomizing (Roman)
        if self.data.dest_lang == 'Russian':
            all_letters = list("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")  # Possible letters for randomizing (Russian)
        elif self.data.dest_lang == 'Japanese':
            all_letters = list(
                "アァカサタナハマヤャラワガザダバパピビヂジギヰリミヒニチシキィイウゥクスツヌフムユュルグズヅブプペベデゼゲヱレメヘネテセケェエオォコソトノホモヨョロヲゴゾドボポヴッン")  # Possible letters for randomizing (Japanese)
        elif self.data.dest_lang == 'Korean':
            all_letters = list(
                "ᄀᄁᄂᄃᄄᄅᄆᄇᄈᄉᄊᄋᄌᄍᄎᄏᄐᄑ햬양약얀야앵액애앞앙압암알안악아어억언얼엄업엉에여역연열염엽영예용욕요왼왜왕왈완와옹옴올온옥오우욱운울움웅워원월위유육윤율융윷으은을음읍응의이익인일임입잉잎")  # Possible letters for randomizing (Korean)
        self.word = self.currentWord

        if ' ' in self.word:
            self.word = self.word.replace(' ', '')
            print('space removed')
        else:
            print('No space in word')

        self.word = "".join(set(self.word.lower()))

        self.letters_btn = self.word

        letters_needed = 19 - len(
            self.word)  # 18 letters are needed in total, X letters already exist in current Word
        # Turn all letterBtn variables into a list for efficiency
        letterBtn = [self.letterBtn1, self.letterBtn2, self.letterBtn3, self.letterBtn4, self.letterBtn5,
                     self.letterBtn6, self.letterBtn7, self.letterBtn8, self.letterBtn9, self.letterBtn10,
                     self.letterBtn11, self.letterBtn12, self.letterBtn13, self.letterBtn14, self.letterBtn15,
                     self.letterBtn16, self.letterBtn17, self.letterBtn18]

        # turn button opacity to 1
        for x in range(18):
            letterBtn[x].opacity = 1
        # Add possible characters to list including currentWord
        for x in range(letters_needed):

            while True:
                # letters_btn length may not exceed 12
                if len(self.letters_btn) != 18:

                    add_letter = random.choice(all_letters)  # Choose random letter from all_letters

                    if add_letter not in self.letters_btn and add_letter not in self.word:
                        self.letters_btn += add_letter  # Append chosen letter to letters_btn
                        # print(self.letters_btn)
                        break

                    else:
                        continue

                else:
                    break

        self.letters_btn = list(self.letters_btn)
        random.shuffle(self.letters_btn)  # Shuffle letters to prevent currentWord from appearing in correct order
        # print(self.letters_btn)  # Check list of letters to make sure that new list is indeed updated
        self.letters_btn = str(self.letters_btn)
        self.letters_btn = self.letters_btn.replace(' ', '')
        self.letters_btn = self.letters_btn.replace(',', '')
        self.letters_btn = self.letters_btn.replace('[', '')
        self.letters_btn = self.letters_btn.replace(']', '')
        self.letters_btn = self.letters_btn.replace("'", '')
        self.letters_btn = self.letters_btn.upper()

        # Assign characters to buttons
        for x in range(len(self.letters_btn)):
            letterBtn[x].text = self.letters_btn[x]

        for x in range(len(self.currentWord)):
            word_button = Factory.WordButton()
            self.grid.add_widget(word_button)
            word_button.charpos = x
            if self.currentWord[x] == ' ':
                word_button.text = ' '
                word_button.disabled = True
            if self.currentWord[x] == '-':
                word_button.text = '-'
                word_button.disabled = True
            self.wordbuttons.append(word_button)

    # Function for typing words
    def typeWord(self):

        # To prevent tuples, which happens for some reason
        if type(self.i) is tuple:
            self.i = self.i[0]
            int(self.i)

        # Turn all letterBtn variables into a list for efficiency
        letterBtn = [self.letterBtn1, self.letterBtn2, self.letterBtn3, self.letterBtn4, self.letterBtn5,
                     self.letterBtn6, self.letterBtn7, self.letterBtn8, self.letterBtn9, self.letterBtn10,
                     self.letterBtn11, self.letterBtn12, self.letterBtn13, self.letterBtn14, self.letterBtn15,
                     self.letterBtn16, self.letterBtn17, self.letterBtn18]

        # Get amount of characters in 'answer' label for iteration
        wordlength = len(self.emptyspace)

        # Turn emptyspace in list, used for replacing and appending characters.

        for i in range(1, 12):
            letterBtn[i].state = 'normal'
            if self.hints > 0:
                self.help_button.disabled = False
        for x in range(wordlength):

            # Check if current character is '-', if yes, replace with letter on pressed button
            if self.wordbuttons[x].text == '_':

                if self.currentWord[x] == ' ':
                    self.wordbuttons[x].text = ' '
                    self.wordbuttons[x].disabled = True
                    self.wordbuttons[x + 1].text = letterBtn[self.i].text
                    self.wordbuttons[x + 1].state = 'normal'
                if self.currentWord[x] == '-':
                    self.wordbuttons[x].text = '-'
                    self.wordbuttons[x].disabled = True
                    self.wordbuttons[x + 1].text = letterBtn[self.i].text
                    self.wordbuttons[x + 1].state = 'normal'
                # Replace current '_' with button text
                else:
                    self.wordbuttons[x].text = letterBtn[self.i].text
                    self.wordbuttons[x].state = 'normal'

                break

            else:

                continue

    def backspace(self):

        old_charloc = self.charloc + 1

        # print(self.wordbuttons[self.charloc].text)
        if self.wordbuttons[self.charpos] != '_':

            try:
                self.wordbuttons[(old_charloc + 1)].state = 'normal'
            except IndexError:
                print(IndexError)
            self.charloc = old_charloc

            # print(self.charloc)

    def help(self):

        self.hints_used += 1

        if self.hints >= 1:
            self.help_button.disabled = False

        labeltext = list(self.emptyspace)
        wordlength = len(self.emptyspace)

        # Turn all letterBtn variables into a list for efficiency
        letterBtn = [self.letterBtn1, self.letterBtn2, self.letterBtn3, self.letterBtn4, self.letterBtn5,
                     self.letterBtn6, self.letterBtn7, self.letterBtn8, self.letterBtn9, self.letterBtn10,
                     self.letterBtn11, self.letterBtn12, self.letterBtn13, self.letterBtn14, self.letterBtn15,
                     self.letterBtn16, self.letterBtn17, self.letterBtn18]

        for x in range(wordlength):

            # Check if current character is '-', if yes, replace with letter on pressed button
            if self.wordbuttons[x].text == '_':
                self.wordbuttons[x].text = self.currentWord[x].upper()
                self.wordbuttons[x].disabled = True
                self.wordbuttons[x].color = (0, .4, 1, 1)

                self.hints -= 1
                print(self.hints)
                self.ids.help_amount.text = str(self.hints)

                # if self.hints <= 0:
                #     self.help_button.disabled = True

                # if '_' not in self.wordbuttons[(wordlength-1)].text:
                #     self.wordChecker()

                break

            else:

                continue

        print('help')

    def skip_level(self):

        self.skip = True

        labeltext = list(self.emptyspace)
        wordlength = len(self.emptyspace)

        # Turn all letterBtn variables into a list for efficiency
        letterBtn = [self.letterBtn1, self.letterBtn2, self.letterBtn3, self.letterBtn4, self.letterBtn5,
                     self.letterBtn6, self.letterBtn7, self.letterBtn8, self.letterBtn9, self.letterBtn10,
                     self.letterBtn11, self.letterBtn12, self.letterBtn13, self.letterBtn14, self.letterBtn15,
                     self.letterBtn16, self.letterBtn17, self.letterBtn18]

        for x in range(wordlength):

            # Check if current character is '-', if yes, replace with letter on pressed button
            if self.wordbuttons[x].text == '_':
                self.wordbuttons[x].text = self.currentWord[x].upper()
                self.wordbuttons[x].disabled = True
                self.wordbuttons[x].color = (0, .4, 1, 1)

                if '_' in self.emptyspace:

                    continue

                else:

                    break



            else:

                continue

    def victory_sound(self):

        if not self.skip:

            press_sound = None
            file = 'resources/Sounds/correct.wav'
            press_sound = SoundLoader.load(file)

            press_sound.volume = .8
            press_sound.play()
        else:
            print('No sound for a skipper')
            pass

    def incorrect_sound(self):

        press_sound = None
        file = 'resources/Sounds/incorrect.wav'
        press_sound = SoundLoader.load(file)

        press_sound.volume = .8
        press_sound.play()

    def play_sound(self):

        if self.sound_used == 1:
            self.sound_hint -= 1
            self.ids.sound_amount.text = str(self.sound_hint)

        self.sound_used = 0

        print(self.sound_hint)
        print(self.ids.sound_button.text)

        language = self.data.dest_lang.lower()
        source = 'resources/packs/huis/langs' if store.get("current_pack")[
                                                     "source"] == "resources/packs/huis/wordlist_house.csv" else "resources/packs/dieren/langs"
        file = source + language + '/' + self.currentWord + '.mp3'

        click_sound = SoundLoader.load(file)

        click_sound.volume = .8
        click_sound.play()

        click_sound = SoundLoader.load('')

    def play_click_button_sound(self, interval):

        press_sound = None
        file = 'resources/Sounds/click_button.wav'
        press_sound = SoundLoader.load(file)

        press_sound.volume = .8
        press_sound.play()

    def click_button(self):

        Clock.schedule_once(self.play_click_button_sound, -2)

    def wordChecker(self):

        self.answer_to_check = []

        for x in range(len(self.wordbuttons)):
            self.answer_to_check.append(self.wordbuttons[x].text)

        self.answer_to_check = ''.join([str(elem) for elem in self.answer_to_check])
        print('answ to check: ', self.answer_to_check)

        # Check if '-' exists in label, if yes, level is not finished. If '-' does not exist, check if answer is correct
        if '_' in self.answer_to_check:

            self.level_finish = False

        else:

            # if True, answer is correct and level is finished
            if self.answer_to_check.lower() == self.currentWord.lower():

                self.level += 1

                if self.level < 10:

                    self.index = self.indexlist[self.level]  # Index +1 to go to next word
                    # self.answer.color = .021, .4, .006, 1
                    self.level_finish = True  # Level is finished
                    self.stop_game()  # Time is stopped to get score
                    try:
                        self.add_widget(self.next_button)
                    except kivy.uix.widget.WidgetException:
                        print(
                            "kivy.uix.widget.WidgetException: Cannot add <kivy.uix.button.Button object at 0x7fb802ff30b0>, it already has a parent <Screen name='second'")

                    self.next_button.opacity = 1
                    self.ids.sound_button.disabled = True
                    self.ids.help_button.disabled = True
                    self.victory_sound()
                    time.sleep(.8)
                    self.play_sound()

                    # remove buttons for cleaner look

                    # Turn all letterBtn variables into a list for efficiency
                    letterBtn = [self.letterBtn1, self.letterBtn2, self.letterBtn3, self.letterBtn4, self.letterBtn5,
                                 self.letterBtn6, self.letterBtn7, self.letterBtn8, self.letterBtn9, self.letterBtn10,
                                 self.letterBtn11, self.letterBtn12, self.letterBtn13, self.letterBtn14,
                                 self.letterBtn15,
                                 self.letterBtn16, self.letterBtn17, self.letterBtn18]

                    for x in range(len(letterBtn)):
                        try:
                            letterBtn[x].opacity = 0
                        except Exception as e:
                            print(e)

                # if True, all words in game are done
                elif self.level >= 10:
                    self.game_finish = True
                    self.stop_game()

                    # self.answer.color = .021, .4, .006, 1

            # Answer incorrect, change 'answer' label back to emptyspace
            else:

                self.incorrect_sound()
                time.sleep(.5)
                self.emptyspace = ('_' * len(self.currentWord))

                for x in range(len(self.wordbuttons)):
                    if self.wordbuttons[x].text != ' ':
                        self.wordbuttons[x].text = '_'
                        self.wordbuttons[x].color = (1, 1, 1, 1)

                self.mistakes += 1

    # To increase the time / count
    def increment_time(self, interval):

        self.time += .1

    def stop_game(self):

        self.stop_time()

        # If it took 30 seconds or longer to complete level, 5 points are rewarded (instead of 0 points, since the
        # answer was eventually correct)
        if self.skip:

            self.score += 0

        elif self.hints_used >= 1 or self.mistakes >= 1:

            self.score += (30 - (self.hints_used + self.mistakes))
            self.hints_used = 0
            self.mistakes = 0

        elif self.hints_used == 0 and self.mistakes == 0:

            self.score += self.points
            self.flawless = True

        print("Score: %s \nTime: %d\n" % (round(self.score), round(self.time)))

        self.pay_coins()
        self.high_score()
        self.time = 0  # Turn level time back to 0

        self.go_to_menu = True

    def start_time(self):

        self.time = 0

        Clock.schedule_interval(self.increment_time, .1)

    def stop_time(self):

        if self.game_finish:

            Clock.unschedule(self.increment_time)
            print('Game is over')
            self.go_to_menu = True
            self.game_finish = True

            popup = Factory.PopupFinish()
            popup.open()
            # time.sleep(2)
            # self.reload()
            # KaruApp.WindowManager.current = "first"

        elif self.early_stop:
            Clock.unschedule(self.increment_time)
            self.reload()

        else:
            Clock.unschedule(self.increment_time)

    def pause_time(self):

        if not self.game_finish:

            if self.level_finish:
                print('Level finished, nothing to pause.')

            if not self.level_finish:

                if self.game_pause:
                    Clock.unschedule(self.increment_time)
                    print("!!", self.time)
                    print('unscheduled')

                elif not self.game_pause:
                    # Keeping time
                    Clock.schedule_interval(self.increment_time, .1)

    def pay_coins(self):

        if self.skip:
            self.coins += 0

        elif self.flawless:
            self.coins += self.payout
            self.flawless = False
            print('flawless victory')

        elif not self.flawless:

            self.coins += 5

        print("Earned %s coins" % self.coins)
        self.coins_total += self.coins
        if self.game_finish:
            self.wallet += round(self.coins_total)
            store.put("wallet", coins=self.wallet)
            self.wallet = store.get("wallet")["coins"]
            print("Wallet: %s" % self.wallet)

    def high_score(self):
        highscore = self.highscore
        if self.score > highscore:
            store.put("data", highscore=self.score)
            highscore = store.get("data")["highscore"]
            self.highscore_label.text = str(round(highscore))

            print(highscore)

    def reload(self):

        importlib.reload(packData)

        self.score = 0  # Total score
        self.level_finish = False  # Bool to check if current level is cleared

        self.game_finish = False
        self.game_pause = False
        self.go_to_menu = False
        self.early_stop = 0

        self.coins_total = 0
        self.coins = 0

        # i = letterBtn pressed (i.e. i = 0 = letterBtn1)
        self.i = 0

        # import module packData, containing image's and corresponding words, also randomize index for variation
        self.data = packData
        self.originlist = self.data.pack_origin
        self.wordlist = self.data.pack_dest  # Current list of words
        self.indexlist = list(self.wordlist.keys())  # Index current word
        print(self.indexlist)
        random.shuffle(self.indexlist)
        print(self.indexlist)
        self.level = 0
        self.index = self.indexlist[self.level]

        # Word for current level
        self.currentWord = self.wordlist[self.index]
        self.currentWordOrigin = self.originlist[self.index]

        self.mainlanglabel.text = ''

        # Image for current level
        self.currentImage = self.data.pack_img[self.index]

        # Used to assign letters to buttons
        self.letters_btn = self.currentWord

        print(self.currentWord, self.currentWordOrigin)
        print(self.letters_btn)

        # Used as text for label
        self.emptyspace = ('_' * len(self.currentWord))

        # character location used for backspace and help
        self.charloc = 0

        # Hints
        self.hints = 500  # Total amount of hint per game
        self.hints_used = 0  # Amount of hints used in level
        self.sound_hint = 5
        self.sound_used = 0

        try:
            self.ids.help_button.disabled = False

        except Exception as e:
            print(e)

        try:
            self.ids.sound_button.disabled = False
        except Exception as e:
            print(e)
        try:
            self.ids.help_amount.text = str(self.hints)

        except Exception as e:
            print(e)

        try:
            self.ids.sound_amount.text = str(self.sound_hint)

        except Exception as e:
            print(e)

        # Vars and widgets related to wordbuttons
        self.answer_to_check = []
        self.wordbuttons = []

        self.remove_widget(self.grid)
        self.grid.clear_widgets(children=None)

        self.letters_btn = self.currentWord

        try:
            self.imagewidget.source = self.currentImage
        except AttributeError:
            print(AttributeError)

        # try:
        #     self.remove_widget(self.start_btn)
        # except:
        #     print(Exception, '\n no startbtn removed')
        #
        try:
            self.add_widget(self.start_btn)
        except Exception as e:
            print(e, '\n no startbtn added')
        #
        # try:
        #     self.start_btn.text = 'Raak het scherm aan\n   om te beginnen!'
        # except:
        #     print(Exception, '\n no startbtn text added')

        try:

            # Empty out all buttons
            letterBtn = [self.letterBtn1, self.letterBtn2, self.letterBtn3, self.letterBtn4, self.letterBtn5,
                         self.letterBtn6, self.letterBtn7, self.letterBtn8, self.letterBtn9, self.letterBtn10,
                         self.letterBtn11, self.letterBtn12]

            for x in range(0, 12):
                letterBtn[x].text = ''
        except AttributeError:
            print(AttributeError)

        try:
            self.imagewidget.opacity = 0
        except AttributeError:
            print(AttributeError)

        with self.canvas.before:
            Rectangle(source=store.get('background')['current_bg'], size=self.size, pos=self.pos)

    def start_or_menu(self):

        if not self.game_finish:

            with self.canvas.before:
                Rectangle(source=store.get('background')['current_bg'], size=self.size, pos=self.pos)

            self.reload()
            self.words()
            self.go_to_menu = False

            self.remove_widget(self.start_btn)

        elif self.game_finish:
            self.stop_time()


class Menu(Screen, BoxLayout):
    wallet = NumericProperty(store.get('wallet')['coins'])
    highscore = NumericProperty(store.get('data')['highscore'])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_vars, .5)

    def update_vars(self, dt):
        self.wallet = store.get('wallet')['coins']
        self.highscore = store.get('data')['highscore']


class PopupPacks(Popup):
    current_pack = ObjectProperty(store.get("current_pack")["source"])

    # pack_name = ObjectProperty()

    def pack_switch(self):
        print(self.current_pack)
        store.put("current_pack", source=self.current_pack)


# Popup for unlocking and changing backgrounds
class PopupBg(Popup):
    data = packData
    wallet = store.get("wallet")["coins"]
    backgroundnumber = 1
    buy_backgroundnumber = 1
    current_bg = 1

    bg_buttons = []
    bg_buy_buttons = []

    bg = store.get('background')['current_bg']

    unlocked_bg = store.get('unlocked_backgrounds')

    bg_index = 'bg' + str(backgroundnumber)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        bg_scrollview = ScrollView(do_scroll_y=True, do_scroll_x=False)

        data = packData

        selected = 0  # View currently selected background
        selection_rects = []

        self.bg_buttons = []
        self.bg_buy_buttons = []

        bg_grid = GridLayout(rows=(len(data.backgrounds)), cols=3, size_hint_x=1, size_hint_y=None,
                             pos_hint={'center_x': .5, 'center_y': .5}, spacing=(25, 25), padding=(50, 50, 50, 50))
        bg_grid.bind(minimum_height=bg_grid.setter('height'))
        bg_scrollview.add_widget(bg_grid)
        obj = InstructionGroup()

        backgroundnumber_buy = 1
        bg_index = 'bg' + str(self.backgroundnumber)
        bg_buy_index = 'bg' + str(backgroundnumber_buy)

        backgrounddict = {}  # used for bg_unlocked in json file

        for x in range(int(len(data.backgrounds) / 3)):

            for i in range(3):
                bg_button = Factory.BackgroundButton()

                bg_grid.add_widget(bg_button)
                bg_button.backgroundnumber = self.backgroundnumber
                bg_button.bind(on_press=lambda y: self.change_bg_value())
                # bg_button.bind(on_release=lambda x: self.background_change)

                self.bg_buttons.append(bg_button)

                backgrounddict[bg_index] = False

                self.backgroundnumber += 1
                bg_index = 'bg' + str(self.backgroundnumber)

            for j in range(3):
                btn_index = self.buy_backgroundnumber - 1
                bg_buy_button = Factory.BuyButton()
                self.bg_buy_buttons.append(bg_buy_button)

                bg_grid.add_widget(self.bg_buy_buttons[btn_index])
                self.bg_buy_buttons[btn_index].backgroundnumber_buy = self.buy_backgroundnumber
                #new_val = self.bg_buy_buttons[btn_index].backgroundnumber_buy
                number = self.buy_backgroundnumber
                print(number)

                self.bg_buy_buttons[btn_index].bind(on_press=partial(self.verandervalue, number))#, on_release=lambda y: self.checkout())

                #self.verandervalue(new_val)


                self.buy_backgroundnumber += 1

        self.add_widget(bg_scrollview)
        print(self.unlocked_bg)

        # Loop to check which backgrounds are unlocked, so the buttons can be enabled and disabled where needed
        self.backgroundnumber = 1
        for x in range(len(self.bg_buttons)):
            try:
                bg_index = 'bg' + str(self.backgroundnumber)
                if self.unlocked_bg[bg_index]:
                    self.bg_buttons[x].remove_widget(self.bg_buttons[x].ids.lock_img)  # Remove lock button and img
                    self.bg_buttons[x].remove_widget(self.bg_buttons[x].ids.lock_button)
                    self.bg_buy_buttons[
                        x].disabled = True  # BuyButton also has to be disabled and the coin_icon should be
                    self.bg_buy_buttons[x].text = ''  # replaced with a check icon

                if self.backgroundnumber != 9:
                    self.backgroundnumber += 1

            except Exception as e:
                print(repr(e))

    def verandervalue(self, val, *largs):
        print(f'value is %d' % val)
        print(f'bg no is %d' % self.backgroundnumber)
        self.backgroundnumber = val
        self.buy_backgroundnumber = val


    def checkout(self):
        print('checking out')
        price = 250
        btn_in_list = self.buy_backgroundnumber - 1

        if price <= self.wallet:
            index = 'bg' + str(self.buy_backgroundnumber)
            print(index, str(self.buy_backgroundnumber))
            self.bg_buttons[btn_in_list].remove_widget(
                self.bg_buttons[btn_in_list].ids.lock_img)  # Remove lock button and img
            self.bg_buttons[btn_in_list].remove_widget(
                self.bg_buttons[btn_in_list].ids.lock_button)
            self.bg_buy_buttons[
                btn_in_list].disabled = True  # BuyButton also has to be disabled and the coin_icon should be
            self.bg_buy_buttons[btn_in_list].text = ''  # replaced with a check icon

            store["unlocked_backgrounds"][index] = True
            store["unlocked_backgrounds"] = store["unlocked_backgrounds"]

    # backgroundnumber = 1
    # backgroundnumber_buy = 1
    # current_bg = 1
    #
    # bg = store.get('custom')['current_bg']
    #
    # bg_unlocked = store.get('backgrounds')
    #
    # bg_index = 'bg' + str(backgroundnumber)
    #
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #
    #     bg_scrollview = ScrollView(do_scroll_y=True, do_scroll_x=False)
    #
    #     data = packData
    #
    #     selected = 0  # View currently selected background
    #     selection_rects = []
    #
    #     bg_buttons = []
    #     bg_buy_buttons = []
    #
    #     bg_grid = GridLayout(rows=(len(data.backgrounds)), cols=3, size_hint_x=1, size_hint_y=None,
    #                          pos_hint={'center_x': .5, 'center_y': .5}, spacing=(25, 25), padding=(50, 50, 50, 50))
    #     bg_grid.bind(minimum_height=bg_grid.setter('height'))
    #     bg_scrollview.add_widget(bg_grid)
    #     obj = InstructionGroup()
    #
    #     backgroundnumber_buy = 1
    #     bg_index = 'bg' + str(self.backgroundnumber)
    #     bg_buy_index = 'bg' + str(backgroundnumber_buy)
    #
    #     backgrounddict = {}  # used for bg_unlocked in json file
    #
    #     for x in range(int(len(data.backgrounds) / 3)):
    #
    #         for i in range(3):
    #             bg_button = Factory.BackgroundButton()
    #
    #             bg_grid.add_widget(bg_button)
    #             bg_button.backgroundnumber = self.backgroundnumber
    #             bg_button.bind(on_press=lambda j: self.change_bg_value())
    #             # bg_button.bind(on_release=lambda x: self.background_change)
    #
    #             bg_buttons.append(bg_button)
    #
    #             backgrounddict[bg_index] = False
    #
    #             self.backgroundnumber += 1
    #             bg_index = 'bg' + str(self.backgroundnumber)
    #
    #         for x in range(3):
    #             bg_buy_button = Factory.BuyButton()
    #             bg_grid.add_widget(bg_buy_button)
    #
    #             bg_buy_button.backgroundnumber_buy = self.backgroundnumber_buy
    #             bg_buy_button.bind(on_press=lambda j: self.checkout())
    #             bg_buy_buttons.append(bg_buy_button)
    #
    #             self.backgroundnumber_buy += 1
    #
    #
    #
    #     self.add_widget(bg_scrollview)
    #     print(self.bg_unlocked)
    #
    #     # Loop to check which backgrounds are unlocked, so the buttons can be enabled and disabled where needed
    #     self.backgroundnumber = 1
    #     for x in range(len(bg_buttons)):
    #         try:
    #             bg_index = 'bg' + str(self.backgroundnumber)
    #             if self.bg_unlocked[bg_index]:
    #                 bg_buttons[x].remove_widget(bg_buttons[x].ids.lock_img)  # Remove lock button and img
    #                 bg_buttons[x].remove_widget(bg_buttons[x].ids.lock_button)
    #                 bg_buy_buttons[x].disabled = True  # BuyButton also has to be disabled and the coin_icon should be
    #                 bg_buy_buttons[x].text = ''  # replaced with a check icon
    #
    #             self.backgroundnumber += 1
    #         except Exception as e:
    #             print(repr(e))
    #
    # price = 250
    #
    # wallet = store.get("wallet")["coins"]
    # print(wallet)
    #
    # def change_bg_value(self):
    #
    #     for x in range(len(self.bg_buttons)):
    #         if self.data[x] == self.bg_buttons[x].backgroundnumber:
    #             self.current_bg = self.bg_buttons[x].backgroundnumber
    #             store.put("custom", current_bg=self.bg_buttons[x].source)
    #             print('works')
    #
    #             break
    #         else:
    #             continue
    #
    # def checkout(self):
    #
    #     print('checkout')
    #
    #     if self.price <= self.wallet:
    #
    #         bg_buy_index = 'bg' + str(self.backgroundnumber_buy)
    #         print(bg_buy_index)
    #
    #         print("Kaching!")
    #         self.wallet = self.wallet - self.price
    #         print('current wallet: ', self.wallet)
    #         store.put("wallet", coins=self.wallet)
    #
    #         store['unlocked_backgrounds'][self.bg_index] = True
    #         self.bg_buttons[self.backgroundnumber_buy].remove_widget(
    #             self.bg_buttons[self.backgroundnumber_buy].ids.lock_img)  # Remove lock button and img
    #         self.bg_buttons[self.backgroundnumber_buy].remove_widget(
    #             self.bg_buttons[self.backgroundnumber_buy].ids.lock_button)
    #         # self.bg_buttons[self.backgroundnumber_buy]
    #
    #         self.title = ('KaruCoins: ' + str(round(self.wallet)))
    #
    #     else:
    #         print("Not enough coins")
    #
    # def background_change(self):
    #     pass
    #     # self.current_bg = self.bg_button.backgroundnumber
    #     #
    #     # self.bg_index = 'bg' + str(self.current_bg)
    #     #
    #     # # self.current_bg = self.backgroundnumber
    #     #
    #     # store.put("custom", current_bg=packData.backgrounds[self.current_bg])


class KaruHouse(Screen, BoxLayout):
    pass


class PopupMenu(Popup):
    pass


class PopupOutfit(Popup):
    # data = packData
    # wallet = store.get("wallet")["coins"]
    pass


class SettingsScreen(Screen, BoxLayout):
    # Empty variables that will be filled using the flag buttons (see layout.kv line 951-1290)
    origin_lang = ""
    dest_lang = ""

    # Choose the origin language (would usually be user's native language)
    def choose_origin(self):
        # Changes "origin_lang" in user_data.json to chosen language. packData.py uses this json file for making and
        # importing wordlists
        store.put("origin_lang", language=self.origin_lang)

    # Choose the destination language (this is the language user wants to learn)
    def choose_dest(self):
        # Changes "dest_lang" in user_data.json to chosen language. packData.py uses this json file for making and
        # importing wordlists
        store.put("dest_lang", language=self.dest_lang)


class WindowManager(ScreenManager):
    pass


class KaruApp(App):
    WindowManager = WindowManager()

    def build(self):
        self.icon = 'resources/icons/karuicon.png'
        return self.WindowManager


KaruApp().run()
