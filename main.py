# Using kivy 2.0.0 and python3.8
# -*- coding: utf-8 -*-


import importlib
import os
from functools import partial

import kivy
from kivy.animation import Animation

from kivy.config import Config  # For setting height (19.5:9)
from kivy.core.image import Image
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

from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty, ReferenceListProperty
from kivy.clock import Clock  # For retrieving playtime and getting score
from kivy.storage.jsonstore import JsonStore

import random
import time

from kivy.vector import Vector

import karuData
import packData

kivy.require('2.0.0')  # Version of Kivy)
os.environ["KIVY_AUDIO"] = "audio_sdl2" #audio_ffpyplayer, audio_sdl2 (audio_gstplayer, audio_avplayer ignored)
Config.set('graphics', 'width', '360')  # (New Android smartphones e.g. OnePlus 7 series)
Config.set('graphics', 'height', '640')  # (iPhone X, 11 and 12 series, upsampled)
store = JsonStore('resources/user_data.json')  # For saving high score
root_widget = Builder.load_file('layout.kv')


# root_widget = Builder.load_string(open("layout.kv", encoding="utf-8").read(), rulesonly=True)


# os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'  # If necessary, uncomment to prevent OpenGL error

class GameWidget(Screen, FloatLayout):
    importlib.reload(packData)
    data = packData

    time = NumericProperty()  # Time taken per image

    points = NumericProperty(50)  # Points per level
    score = NumericProperty(0)  # Total score
    highscore = NumericProperty(store.get('data')['highscore'])  # High score
    old_highscore = NumericProperty(store.get('data')['highscore'])
    broke_record = BooleanProperty(False)
    highscore_label = ObjectProperty()

    correct_words = NumericProperty(store.get('data')[ 'correct_words'])  # All correct words since playing, used to unlock categories and more in the future

    wallet = NumericProperty(store.get('wallet')['coins'])
    wallet_label = ObjectProperty()  # In-game label where wallet is viewed
    new_wallet = wallet
    payout = NumericProperty(10)  # Max amount of coins per level

    coins = NumericProperty(0)  # Amount of coins earned in current level
    coins_total = NumericProperty(0)  # Amount of coins earned in current game
    coins_earned = NumericProperty(0)
    mistakes = 0  # Amount of mistakes, used for awarding coins

    flawless = False  # Check if score is perfect (<5sec, no hints, no mistakes)

    level_finish = False  # Bool to check if current level is cleared

    bg = ObjectProperty(data.current_bg)

    main_color = ObjectProperty((1, 1, 1, 1))

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
    cd_label = ObjectProperty(None)

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
    hints = 5  # Total amount of hint per game
    hints_used = 0  # Amount of hints used in level
    sound_hint = 5
    sound_used = 0

    skip = False

    cd = 3

    def __init__(self, **kwargs):

        super(GameWidget, self).__init__(**kwargs)

        # Start randomizeLetters() to randomize and add letters to letterBtns
        # self.randomizeLetters()

    # Function for changing words and images when answer correct
    def words(self):

        # Check if level is cleared
        # if self.level_finish:

        self.ids.pass_button.disabled = False

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
            self.grid = GridLayout(rows=1, cols=len(self.currentWord), spacing=8, size_hint_x=.55, size_hint_y=.175,
                                   pos_hint={'center_x': .5, 'center_y': .4})
            self.add_widget(self.grid)
            self.grid_exist = True
            print('grid created')
        if self.grid_exist:
            self.answer_to_check = []
            self.wordbuttons = []
            self.charloc = 0
            self.grid.clear_widgets(children=None)
            self.remove_widget(self.grid)
            self.grid = GridLayout(rows=1, cols=len(self.currentWord), spacing=8, size_hint_x=.55, size_hint_y=.175,
                                   pos_hint={'center_x': .5, 'center_y': .4})
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

        elif '-' in self.word:
            self.word = self.word.replace('-', '')
            print('dash removed')
        else:
            print('No space or dash in word')

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
            letterBtn[x].secondary_color2 = (1.1 - self.main_color[0], 1.1 - self.main_color[1], 1.1 - self.main_color[2], .8)

            if self.level == 0:
                with letterBtn[x].canvas.before:
                    Color(1 - self.main_color[0], 1 - self.main_color[1], 1 - self.main_color[2], .9)
                    RoundedRectangle(pos=letterBtn[x].pos, size=letterBtn[x].size)
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
                self.wordbuttons[x].color = (1 - self.main_color[0], 1 - self.main_color[1], 1 - self.main_color[2], 1)

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
                self.wordbuttons[x].color = (1 - self.main_color[0], 1 - self.main_color[1], 1 - self.main_color[2], 1)

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

    def new_best_sound(self):

        victory_sound = None
        file = 'resources/Sounds/victory.wav'
        victory_sound = SoundLoader.load(file)

        victory_sound.volume = .8
        victory_sound.play()

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
                    self.ids.pass_button.disabled = True
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
                        self.wordbuttons[x].main_color = (1, 1, 1, 1)

                self.mistakes += 1

    # To increase the time / count
    def increment_time(self, interval):

        self.time += .1

    def stop_game(self):



        # If it took 30 seconds or longer to complete level, 5 points are rewarded (instead of 0 points, since the
        # answer was eventually correct)
        if self.skip:

            self.score += 0

        elif self.hints_used >= 1 or self.mistakes >= 1:

            self.score += (30 - (self.hints_used*2 + self.mistakes*2))
            self.correct_words += 1
            store["data"]["correct_words"] = self.correct_words
            self.hints_used = 0
            self.mistakes = 0

        elif self.hints_used == 0 and self.mistakes == 0:

            self.score += self.points
            self.correct_words += 1
            store["data"]["correct_words"] = self.correct_words
            self.flawless = True

        print("Score: %s \nTime: %d\n" % (round(self.score), round(self.time)))

        self.time = 0  # Turn level time back to 0

        #self.go_to_menu = True
        self.pay_coins()
        self.high_score()

        self.stop_time()


    def start_time(self):

        self.time = 0

        Clock.schedule_interval(self.increment_time, .1)

    def stop_time(self):

        if self.game_finish:

            Clock.unschedule(self.increment_time)
            print('Game is over')
            self.high_score()
            self.time = 0  # Turn level time back to 0

            self.pay_coins()
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
            self.coins_earned = self.coins_total
            self.wallet += self.coins_total
            store.put("wallet", coins=self.wallet)
            self.wallet = store.get("wallet")["coins"]
            print("Wallet: %s" % self.wallet)
            self.new_wallet -= self.coins_total

    def count_coins(self, dt):

        if self.coins_earned >= 1:
            self.coins_earned -= 1
            self.coins_total -= 1
            self.new_wallet += 1
        else:
            Clock.unschedule(self.count_coins)

    def count_coins_anim(self, coin_ico):

        anim = Animation(opacity=0, duration=.01)
        anim += Animation(pos_hint={'center_x':.5, 'y':.55}, opacity=1, duration=.1)
        anim += Animation(pos_hint={'center_x': .875, 'y': 1.07}, opacity=0, duration=0)

        anim.repeat = True
        anim.start(coin_ico)

        coin_sound = None
        file = 'resources/Sounds/coin copy.wav'
        coin_sound = SoundLoader.load(file)

        coin_sound.volume = .8
        if self.coins_earned > 2:
            coin_sound.loop = True
        if self.coins_earned != 0:
            coin_sound.play()

        def check_amount(dt):

            if self.coins_earned == 2:
                coin_sound.stop()

                file = 'resources/Sounds/coin.wav'
                coin_sound2 = SoundLoader.load(file)

                coin_sound2.volume = .8
                coin_sound2.play()

            elif self.coins_earned == 0:
                anim.stop(coin_ico)
                coin_ico.opacity = 0
                Clock.unschedule(check_amount)

        Clock.schedule_interval(self.count_coins, .1)
        Clock.schedule_interval(check_amount, .1)

    def high_score(self):
        print("I'm highscore")
        if self.score > self.highscore:
            store["data"]["highscore"] = self.score
            self.highscore = store.get("data")["highscore"]
            self.highscore_label.text = str(self.highscore)
            self.broke_record = True
            print(f'hs:%d' % self.highscore)
            print(f'hs_old:%d' % self.old_highscore)
            print(self.broke_record)

        print(self.broke_record)

    def unlock_notification(self, notification, notification2, *largs):

        x = 10
        y = 2
        first_unlock_theme = True
        first_unlock_skin = True

        skin_prices = [75, 125]
        theme_prices = [50, 125, 225]

        anim = Animation(pos_hint={'center_x': .5, 'y': .65}, duration=1)
        anim += Animation(pos_hint={'center_x': .5, 'y': .65}, duration=2)
        anim += Animation(pos_hint={'center_x': .5, 'y': .75}, duration=1)

        # Check if theme is already unlocked
        while x != 13:
            index = 'bg{}'.format(x)
            print(index)
            if store["unlocked_backgrounds"][index]:
                first_unlock_theme = False
                print('already unlocked!')
            elif not store["unlocked_backgrounds"][index]:
                print("not unlocked, but are you ready?")
                if theme_prices[x - 10] <= store["data"]["correct_words"]:
                    first_unlock_theme = True
                    store["unlocked_backgrounds"][index] = True
                    print('first unlock!')
                    store["unlocked_backgrounds"] = store["unlocked_backgrounds"]
                    print(store["unlocked_backgrounds"][index])

            if theme_prices[x-10] <= store["data"]["correct_words"]:
                print("I got the keys to the door")
                x += 1
            else:
                break

        # Check if skin is already unlocked
        while y != 4:
            index = '{}'.format(y)
            print(index)
            if store["unlocked_skins"][index]:
                first_unlock_skin = False
                print('already unlocked!')
            elif not store["unlocked_skins"][index]:
                print("not unlocked, but are you ready?")
                if skin_prices[y - 2] <= store["data"]["correct_words"]:
                    first_unlock_skin = True
                    store["unlocked_skins"][index] = True
                    print('first unlock!')
                    store["unlocked_skins"] = store["unlocked_skins"]
                    print(store["unlocked_skins"][index])

            if skin_prices[y - 2] <= store["data"]["correct_words"]:
                print("I got the keys to the door")
                y += 1
            else:
                break

        if first_unlock_theme:

            if theme_prices[0] <= store["data"]["correct_words"] or theme_prices[1] <= store["data"]["correct_words"] or theme_prices[2] <= store["data"]["correct_words"]:

                anim.start(notification)

                if first_unlock_skin:
                    if skin_prices[0] <= store["data"]["correct_words"] or skin_prices[1] <= store["data"]["correct_words"]:
                        notification2.pos_hint = {'center_x': .5, 'y': .65}
                        notification2.opacity = 0
                        anim = Animation(pos_hint={'center_x': .5, 'y': .65}, opacity=1, duration=.1)
                        anim = Animation(pos_hint={'center_x': .5, 'y': .565}, opacity=1, duration=1)
                        anim += Animation(pos_hint={'center_x': .5, 'y': .565}, opacity=1, duration=2)
                        anim += Animation(pos_hint={'center_x': .5, 'y': .75}, opacity=0, duration=1)
                        notification2.text = '\n\n' + notification2.text
                        anim.start(notification2)

        if first_unlock_skin:
            if skin_prices[0] <= store["data"]["correct_words"] or skin_prices[1] <= store["data"]["correct_words"]:
                anim.start(notification2)


    def reload(self):

        importlib.reload(packData)
        self.data = packData
        self.bg = self.data.current_bg

        self.score = 0  # Total score
        self.old_highscore = self.highscore
        self.broke_record = False
        self.level_finish = False  # Bool to check if current level is cleared

        self.game_finish = False
        self.game_pause = False
        self.go_to_menu = False
        self.early_stop = 0

        self.coins_total = 0
        self.coins_earned = 0
        self.coins = 0

        # i = letterBtn pressed (i.e. i = 0 = letterBtn1)
        self.i = 0

        # import module packData, containing image's and corresponding words, also randomize index for variation

        self.originlist = self.data.pack_origin
        self.wordlist = self.data.pack_dest  # Current list of words
        self.indexlist = list(self.wordlist.keys())  # Index current word
        print(self.indexlist)
        random.shuffle(self.indexlist)
        print(self.indexlist)
        self.level = 9
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

        try:
            self.add_widget(self.cd_label)
        except Exception as e:
            print(e, '\n no cd_label added')

        try:

            # Empty out all buttons
            letterBtn = [self.letterBtn1, self.letterBtn2, self.letterBtn3, self.letterBtn4, self.letterBtn5,
                     self.letterBtn6, self.letterBtn7, self.letterBtn8, self.letterBtn9, self.letterBtn10,
                     self.letterBtn11, self.letterBtn12, self.letterBtn13, self.letterBtn14, self.letterBtn15,
                     self.letterBtn16, self.letterBtn17, self.letterBtn18]

            for x in range(0, 18):
                letterBtn[x].text = ''
                letterBtn[x].canvas.before.clear()

        except AttributeError:
            print(AttributeError)

        try:
            self.imagewidget.opacity = 0
        except AttributeError:
            print(AttributeError)

        try:
            self.remove_widget(self.ids.menupop)
        except Exception as e:
            print(e)

        try:
            self.remove_widget(self.ids.pass_button)
        except Exception as e:
            print(e)

        try:
            self.remove_widget(self.ids.sound_button)
        except Exception as e:
            print(e)

        try:
            self.remove_widget(self.ids.sound_amount)
        except Exception as e:
            print(e)

        try:
            self.remove_widget(self.ids.help_button)
        except Exception as e:
            print(e)

        try:
            self.remove_widget(self.ids.help_amount)
        except Exception as e:
            print(e)

        try:
            self.remove_widget(self.ids.pass_button)
        except Exception as e:
            print(e)

        try:
            self.remove_widget(self.ids.score_label)
        except Exception as e:
            print(e)

        try:
            self.remove_widget(self.ids.highscore_label)
        except Exception as e:
            print(e)

        try:
            self.remove_widget(self.ids.wallet_label)
        except Exception as e:
            print(e)

        try:
            self.remove_widget(self.ids.coin_icon)
        except Exception as e:
            print(e)


        try:
            self.remove_widget(self.ids.crown_icon)
        except Exception as e:
            print(e)

        try:
            self.remove_widget(self.next_button)
        except:
            print('No next_button to remove')

        try:
            self.add_widget(self.cd_label)
        except:
            print('cd_label already exists')


    def second_color(self):

        im = store.get("background")["current_bg"]
        m = Image.load(im, keep_data=True)
        self.main_color = m.read_pixel(20, 10)
        print(self.main_color)

    # Countdown till game starts
    def countdown(self, dt):
        print('start cd')
        if self.cd > 1:
            self.cd -= 1
            try:
                self.cd_label.text = str(self.cd)
            except Exception as e:
                print(e)

            print(self.cd)


        elif self.cd == 1:
            self.start_or_menu()
            Clock.unschedule(self.countdown)

    def start_or_menu(self):

        # if not self.game_finish:

        self.reload()

        # add necessary widgets
        try:
            self.add_widget(self.ids.menupop)
        except Exception as e:
            print(e)

        try:
            self.add_widget(self.ids.pass_button)
        except Exception as e:
            print(e)

        try:
            self.add_widget(self.ids.sound_button)
        except Exception as e:
            print(e)

        try:
            self.add_widget(self.ids.sound_amount)
        except Exception as e:
            print(e)

        try:
            self.add_widget(self.ids.help_button)
        except Exception as e:
            print(e)

        try:
            self.add_widget(self.ids.help_amount)
        except Exception as e:
            print(e)

        try:
            self.add_widget(self.ids.pass_button)
        except Exception as e:
            print(e)

        try:
            self.add_widget(self.ids.score_label)
        except Exception as e:
            print(e)

        try:
            self.add_widget(self.ids.highscore_label)
        except Exception as e:
            print(e)

        try:
            self.add_widget(self.ids.wallet_label)
        except Exception as e:
            print(e)

        try:
            self.add_widget(self.ids.coin_icon)
        except Exception as e:
            print(e)


        try:
            self.add_widget(self.ids.crown_icon)
        except Exception as e:
            print(e)
        # self.add_widget(self.ids.menupop)
        # self.add_widget(self.ids.pass_button)
        # self.add_widget(self.ids.sound_button)
        # self.add_widget(self.ids.sound_amount)
        # self.add_widget(self.ids.help_button)
        # self.add_widget(self.ids.help_amount)
        # self.add_widget(self.ids.score_label)
        # self.add_widget(self.ids.highscore_label)
        # self.add_widget(self.ids.wallet_label)
        # self.add_widget(self.ids.coin_icon)
        # self.add_widget(self.ids.crown_icon)

        self.words()
        # self.go_to_menu = False
        self.cd = 3
        self.cd_label.text = str(self.cd)
        self.remove_widget(self.cd_label)




        # elif self.game_finish:
        #     self.stop_time()



class Menu(Screen, BoxLayout):
    wallet = NumericProperty(store.get('wallet')['coins'])
    highscore = NumericProperty(store.get('data')['highscore'])
    main_color = ObjectProperty((1, 1, 1, 1))
    skin = ObjectProperty(store.get("skin")["current_skin"])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_vars, .5)
        self.second_color()
        self.check_skin()

    def update_vars(self, dt):
        self.wallet = store.get('wallet')['coins']
        self.highscore = store.get('data')['highscore']

    def second_color(self):
        im = store.get("background")["current_bg"]
        m = Image.load(im, keep_data=True)
        self.main_color = m.read_pixel(20, 10)
        print(self.main_color)

    def check_skin(self):
        self.skin = store["skin"]["current_skin"]
        print(self.skin)


class PopupPacks(Popup):
    current_pack = ObjectProperty(store.get("current_pack")["source"])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_pack = store.get("current_pack")["source"]

    def pack_switch(self):
        print(self.current_pack)
        store.put("current_pack", source=self.current_pack)


# Popup for unlocking and changing backgrounds
class PopupBg(Popup):
    data = packData
    wallet = ObjectProperty(store.get("wallet")["coins"])
    backgroundnumber = 1
    buy_backgroundnumber = 1
    current_bg = 1

    bg_buttons = []
    bg_buy_buttons = []
    bg_bars = []

    bg = ObjectProperty(store.get('background')['current_bg'])

    unlocked_bg = store.get('unlocked_backgrounds')
    unlocked_amount = NumericProperty(0)

    bg_index = 'bg' + str(backgroundnumber)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        bg_scrollview = ScrollView(do_scroll_y=True, do_scroll_x=False)

        data = packData

        self.bg_buttons = []
        self.bg_buy_buttons = []
        self.bg_bars = []

        bg_grid = GridLayout(rows=(len(data.backgrounds)), cols=3, size_hint_x=1, size_hint_y=None,
                             pos_hint={'center_x': .5, 'center_y': .5}, spacing=(25, 25), padding=(50, 50, 50, 50))
        bg_grid.bind(minimum_height=bg_grid.setter('height'))

        bg_scrollview.add_widget(bg_grid)
        obj = InstructionGroup()

        backgroundnumber_buy = 1
        bg_index = 'bg' + str(self.backgroundnumber)
        bg_buy_index = 'bg' + str(backgroundnumber_buy)

        #backgrounddict = {}  # used for bg_unlocked in json file

        for x in range(int(len(data.backgrounds) / 3)):

            for i in range(3):

                bg_button = Factory.BackgroundButton()

                bg_button.backgroundnumber = self.backgroundnumber
                path = f"resources/backgrounds/wallpaper%d.png" % self.backgroundnumber

                if store["background"]["current_bg"] == path:

                    bg_button.state = "down"

                bg_button.bind(on_press=partial(self.update_value, self.backgroundnumber), on_release=partial(self.background_change))
                bg_grid.add_widget(bg_button)
                self.bg_buttons.append(bg_button)

                #backgrounddict[bg_index] = False

                self.backgroundnumber += 1


            for j in range(3):

                if self.buy_backgroundnumber < 10:
                    btn_index = self.buy_backgroundnumber - 1
                    bg_buy_button = Factory.BuyButton()
                    self.bg_buy_buttons.append(bg_buy_button)

                    bg_grid.add_widget(self.bg_buy_buttons[btn_index])
                    self.bg_buy_buttons[btn_index].backgroundnumber_buy = self.buy_backgroundnumber

                    self.bg_buy_buttons[btn_index].bind(on_press=partial(self.update_value, self.buy_backgroundnumber), on_release=lambda y: self.checkout())

                    #self.verandervalue(new_val)

                else:
                    bar_index = self.buy_backgroundnumber - 10
                    unlock_bar = Factory.BgBar()
                    self.bg_bars.append(unlock_bar)
                    if bar_index == 0:
                        self.bg_bars[bar_index].max = 50
                        self.bg_bars[bar_index].value = store["data"]["correct_words"]
                        if self.bg_bars[bar_index].value == self.bg_bars[bar_index].max:
                            #self.bg_buttons[self.buy_backgroundnumber].
                            bg_index = 'bg' + str(self.buy_backgroundnumber)
                            self.unlocked_bg[bg_index] = True
                        else:
                            bg_index = 'bg' + str(self.buy_backgroundnumber)
                            self.unlocked_bg[bg_index] = False
                    elif bar_index == 1:
                        self.bg_bars[bar_index].max = 125
                        self.bg_bars[bar_index].value = store["data"]["correct_words"]
                        if self.bg_bars[bar_index].value == self.bg_bars[bar_index].max:
                            #self.bg_buttons[self.buy_backgroundnumber].
                            bg_index = 'bg' + str(self.buy_backgroundnumber)
                            self.unlocked_bg[bg_index] = True
                        else:
                            bg_index = 'bg' + str(self.buy_backgroundnumber)
                            self.unlocked_bg[bg_index] = False
                    elif bar_index == 2:
                        self.bg_bars[bar_index].max = 225
                        self.bg_bars[bar_index].value = store["data"]["correct_words"]
                        if self.bg_bars[bar_index].value == self.bg_bars[bar_index].max:
                            #self.bg_buttons[self.buy_backgroundnumber].
                            bg_index = 'bg' + str(self.buy_backgroundnumber)
                            self.unlocked_bg[bg_index] = True
                        else:
                            bg_index = 'bg' + str(self.buy_backgroundnumber)
                            self.unlocked_bg[bg_index] = False

                    bg_grid.add_widget(self.bg_bars[bar_index])

                self.buy_backgroundnumber += 1

        self.add_widget(bg_scrollview)
        print(self.unlocked_bg)

        # Loop to check which backgrounds are unlocked, so the buttons can be enabled and disabled where needed
        self.backgroundnumber = 1
        for x in range(len(self.bg_buy_buttons)+2):
            try:
                bg_index = 'bg' + str(self.backgroundnumber)
                if self.unlocked_bg[bg_index]:
                    self.bg_buttons[x].remove_widget(self.bg_buttons[x].ids.lock_img)  # Remove lock button and img
                    self.bg_buttons[x].remove_widget(self.bg_buttons[x].ids.lock_button)
                    self.bg_buy_buttons[
                        x].disabled = True  # BuyButton also has to be disabled and the coin_icon should be
                    self.bg_buy_buttons[x].text = ''  # replaced with a check icon
                    self.unlocked_amount += 1


                if self.backgroundnumber != 12:
                    self.backgroundnumber += 1

            except Exception as e:
                print(repr(e))

        for x in range(len(self.bg_bars)):
            try:
                bg_index = 'bg1' + str(x)
                if self.unlocked_bg[bg_index]:
                    self.bg_buttons[x].remove_widget(self.bg_buttons[x].ids.lock_img)  # Remove lock button and img
                    self.bg_buttons[x].remove_widget(self.bg_buttons[x].ids.lock_button)
                    self.unlocked_amount += 1

            except Exception as e:
                print(repr(e))

    def update_value(self, val, *largs):
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


            self.wallet = self.wallet - price
            store.put("wallet", coins=self.wallet)

            store["unlocked_backgrounds"][index] = True
            store["unlocked_backgrounds"] = store["unlocked_backgrounds"]

    def background_change(self, *largs):
        btn_in_list = self.backgroundnumber - 1
        self.current_bg = self.backgroundnumber

        store.put("background", current_bg=packData.backgrounds[self.current_bg])

        KaruApp.WindowManager.ids.kh.second_color()
        KaruApp.WindowManager.ids.mainmenu.second_color()
        KaruApp.WindowManager.ids.gw.second_color()
        KaruApp.WindowManager.ids.settings.second_color()

class KaruHouse(Screen, BoxLayout):

    main_color = ObjectProperty((1, 1, 1, 1))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.second_color()

    def second_color(self):
        # from kivy.core.window import Window

        im = store.get("background")["current_bg"]
        m = Image.load(im, keep_data=True)
        self.main_color = m.read_pixel(20, 10)
        print(self.main_color)


class PopupMenu(Popup):
    pass


class PopupOutfit(Popup):
    current_skin = ObjectProperty(store.get("skin")["current_skin"])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.current_skin = store.get("skin")["current_skin"]

    def skin_switch(self):
        print(self.current_skin)
        store.put("skin", current_skin=self.current_skin)



class SettingsScreen(Screen, BoxLayout):
    # Empty variables that will be filled using the flag buttons (see layout.kv line 951-1290)
    origin_lang = ""
    dest_lang = ""
    main_color = ObjectProperty((1, 1, 1, 1))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.second_color()

    def second_color(self):
        # from kivy.core.window import Window

        im = store.get("background")["current_bg"]
        m = Image.load(im, keep_data=True)
        self.main_color = m.read_pixel(20, 10)
        print(self.main_color)

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
