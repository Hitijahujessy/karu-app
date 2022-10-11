# Using kivy 2.0.0 and Python 3.8

import importlib
import os
from functools import partial

import kivy

from kivy.animation import Animation
from kivy.config import Config
from kivy.core.image import Image
from kivy.factory import Factory
from kivy.graphics import Rectangle, RoundedRectangle, Color, InstructionGroup
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.core.audio import SoundLoader
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty, ReferenceListProperty
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
import random
import time

import packData

store = JsonStore('resources/user_data.json')  # For saving high score

kivy.require('2.0.0')
os.environ["KIVY_AUDIO"] = "audio_sdl2"
Config.set('graphics', 'width', '360')  # (New Android smartphones e.g. OnePlus 7 series)
Config.set('graphics', 'height', '640')  # (iPhone X, 11 and 12 series, upsampled)
root_widget = Builder.load_file('layout.kv')


# os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'  # Uncomment to prevent OpenGL error if necesarry


class GameWidget(Screen, FloatLayout):

    data = packData

    bg = ObjectProperty(data.current_bg)  # ???
    main_color = ObjectProperty((1, 1, 1, 1))  # Used for setting accent colors
    cd = 3  # Countdown time

    app_start = True  # ???

    time = NumericProperty()  # Time taken per level

    points = NumericProperty(40)  # Points per level
    score = NumericProperty(0)  # Total score
    highscore = NumericProperty(store.get('data')['highscore'])
    old_highscore = NumericProperty(store.get('data')['highscore'])  # Used in end-game popup when new high score is
    # achieved
    broke_record = BooleanProperty(False)  # Bool for checking if new high score is achieved
    highscore_label = ObjectProperty()  # Shows high score on menu screen and in-game

    wallet = NumericProperty(store.get('wallet')['coins'])
    wallet_label = ObjectProperty()
    new_wallet = wallet  # Used in the end-game popup's coin animation
    payout = NumericProperty(10)  # Max amount of coins per level
    coins = NumericProperty(0)  # Amount of coins earned in current level
    coins_total = NumericProperty(0)  # Amount of coins earned in current game
    coins_earned = NumericProperty(0)  # ???

    correct_words = NumericProperty(store.get('data')['correct_words'])  # All correct words since playing, used to
    # unlock themes, categories and skins

    # All letter buttons, most efficient way I could find at the time. Planning to use a more efficient way of doing
    # this at a later moment. Same goes for all the letter_btns lists.
    letter_btn1 = ObjectProperty(None)
    letter_btn2 = ObjectProperty(None)
    letter_btn3 = ObjectProperty(None)
    letter_btn4 = ObjectProperty(None)
    letter_btn5 = ObjectProperty(None)
    letter_btn6 = ObjectProperty(None)
    letter_btn7 = ObjectProperty(None)
    letter_btn8 = ObjectProperty(None)
    letter_btn9 = ObjectProperty(None)
    letter_btn10 = ObjectProperty(None)
    letter_btn11 = ObjectProperty(None)
    letter_btn12 = ObjectProperty(None)
    letter_btn13 = ObjectProperty(None)
    letter_btn14 = ObjectProperty(None)
    letter_btn15 = ObjectProperty(None)
    letter_btn16 = ObjectProperty(None)
    letter_btn17 = ObjectProperty(None)
    letter_btn18 = ObjectProperty(None)
    letter_btn18 = ObjectProperty(None)

    level_finish = False
    game_finish = False
    game_pause = BooleanProperty(True)
    go_to_menu = False  # ???
    early_stop = 0  # ???

    i = 0  # ???

    word_list = data.pack_dest
    origin_list = data.pack_origin  # Word list in language "main" language
    index_list = list(word_list.keys())  # Index of current word list
    random.shuffle(index_list)  # Randomize word order
    level = 0
    index = index_list[level]

    # Words for current level
    current_word = word_list[index]
    current_word_origin = origin_list[index]
    word = ''  # Used to remove ' ' and '-' without altering current_word
    origin_label = ObjectProperty()  # Label showing current word in "main" language

    image_widget = ObjectProperty(None)
    current_image = data.pack_img[index]

    letters_btn = current_word

    emptyspace = ('_' * len(current_word))  # Used as text for word_buttons
    grid = GridLayout()  # GridLayout containing the word_buttons
    grid_exist = False
    word_buttons = []
    charpos = 0  # used for help and backspace

    # Hints
    hints = 5
    hints_used = 0
    sound_hint = 5
    sound_used = 0

    flawless = False  # Bool for checking if score is perfect (no hints, no mistakes)
    mistakes = 0
    answer_to_check = []  # Used for checking if user is finished with typing and if answer is correct
    skip = False  # Bool for checking if level is skipped
    next_button = ObjectProperty(None)



    def __init__(self, **kwargs):

        super(GameWidget, self).__init__(**kwargs)

    # Function for changing words and images when proceeding to next level
    def words(self):

        self.level_finish = False

        self.time = 0
        self.coins = 0
        self.mistakes = 0
        self.sound_used = 0
        self.hints_used = 0
        self.skip = False

        self.current_word = self.word_list[self.index]
        self.current_word_origin = self.origin_list[self.index]
        self.origin_label.text = self.current_word_origin
        self.current_image = self.data.pack_img[self.index]
        self.emptyspace = ('_' * len(self.current_word))

        self.letters_btn = self.current_word  # Set letter_btns letters to the letters needed for current level
        self.image_widget.source = self.current_image  # Change image source to current_image
        self.ids.pass_button.disabled = False
        self.remove_widget(self.ids.next_button)

        if self.hints > 0:
            self.ids.help_button.disabled = False

        if self.sound_hint > 0:
            self.ids.sound_button.disabled = False

        self.word_letter_btns()

    # Function that randomises letter_btns text and sets word_buttons text
    def word_letter_btns(self):

        if not self.grid_exist:
            self.grid = GridLayout(rows=1, cols=len(self.current_word), spacing=8, size_hint_x=.55, size_hint_y=.175,
                                   pos_hint={'center_x': .5, 'center_y': .4})
            self.add_widget(self.grid)
            self.grid_exist = True
        else:
            self.answer_to_check = []
            self.word_buttons = []
            self.charpos = 0
            self.grid.clear_widgets(children=None)
            self.remove_widget(self.grid)
            self.grid = GridLayout(rows=1, cols=len(self.current_word), spacing=8, size_hint_x=.55, size_hint_y=.175,
                                   pos_hint={'center_x': .5, 'center_y': .4})
            self.add_widget(self.grid)

        if self.data.dest_lang == 'Russian':
            all_letters = list("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")  # Possible letters for randomizing (Russian)
        elif self.data.dest_lang == 'Japanese':
            all_letters = list(
                "アァカサタナハマヤャラワガザダバパピビヂジギヰリミヒニチシキィイウゥクスツヌフムユュルグズヅブプペベデゼゲヱレメヘネテ"
                "セケェエオォコソトノホモヨョロヲゴゾドボポヴッン")  # Possible letters for randomizing (Japanese)
        elif self.data.dest_lang == 'Korean':
            all_letters = list(
                "ᄀᄁᄂᄃᄄᄅᄆᄇᄈᄉᄊᄋᄌᄍᄎᄏᄐᄑ햬양약얀야앵액애앞앙압암알안악아어억언얼엄업엉에여역연열염엽영예용욕요왼왜왕왈완와옹옴올온옥오우욱운울움웅"
                "워원월위유육윤율융윷으은을음읍응의이익인일임입잉잎")  # Possible letters for randomizing (Korean)
        else:
            all_letters = list("abcdefghijklmnopqrstuvwxyz")  # Possible letters for randomizing (Roman)

        self.word = self.current_word

        if ' ' in self.word:
            self.word = self.word.replace(' ', '')
        elif '-' in self.word:
            self.word = self.word.replace('-', '')
        else:
            print('No space or dash in word')

        self.word = "".join(set(self.word.lower()))
        self.letters_btn = self.word

        letters_needed = 18 - len(
            self.word)  # 18 letters are needed in total, - the x amount of letters already existing in current_word

        letter_btn = [self.letter_btn1, self.letter_btn2, self.letter_btn3, self.letter_btn4, self.letter_btn5,
                      self.letter_btn6, self.letter_btn7, self.letter_btn8, self.letter_btn9, self.letter_btn10,
                      self.letter_btn11, self.letter_btn12, self.letter_btn13, self.letter_btn14, self.letter_btn15,
                      self.letter_btn16, self.letter_btn17, self.letter_btn18]

        # Makes the letter_btns visible and sets the correct color
        for x in range(18):
            letter_btn[x].opacity = 1
            letter_btn[x].secondary_color2 = (
                1.1 - self.main_color[0], 1.1 - self.main_color[1], 1.1 - self.main_color[2], .8)

            # Only add a canvas at the first level
            if self.level == 0:
                with letter_btn[x].canvas.before:
                    Color(1 - self.main_color[0], 1 - self.main_color[1], 1 - self.main_color[2], .9)
                    RoundedRectangle(pos=letter_btn[x].pos, size=letter_btn[x].size)

        # Put possible characters in a list
        for x in range(letters_needed):

            while True:

                if len(self.letters_btn) != 18:
                    add_letter = random.choice(all_letters)

                    if add_letter not in self.letters_btn and add_letter not in self.word:
                        self.letters_btn += add_letter
                        break
                    else:
                        continue
                else:
                    break

        self.letters_btn = list(self.letters_btn)
        random.shuffle(self.letters_btn)

        self.letters_btn = str(self.letters_btn)
        self.letters_btn = self.letters_btn.replace(' ', '')
        self.letters_btn = self.letters_btn.replace(',', '')
        self.letters_btn = self.letters_btn.replace('[', '')
        self.letters_btn = self.letters_btn.replace(']', '')
        self.letters_btn = self.letters_btn.replace("'", '')
        self.letters_btn = self.letters_btn.upper()

        # Assign characters to buttons
        for x in range(len(self.letters_btn)):
            letter_btn[x].text = self.letters_btn[x]

        # Create the word_buttons
        for x in range(len(self.current_word)):
            word_button = Factory.WordButton()
            self.grid.add_widget(word_button)
            word_button.secondary_color = (1 - self.main_color[0], 1 - self.main_color[1], 1 - self.main_color[2], .75)

            # Used for correcting typos
            word_button.charpos = x

            if self.current_word[x] == ' ':
                word_button.text = ' '
                word_button.canvas.before.clear()
                word_button.disabled = True
            elif self.current_word[x] == '-':
                word_button.text = '-'
                word_button.canvas.before.clear()
                word_button.disabled = True
                word_button.color = (1 - self.main_color[0], 1 - self.main_color[1], 1 - self.main_color[2], 1)
            self.word_buttons.append(word_button)

        self.start_time()

    # Function for typing words
    def type_word(self):

        # self.i turns into a tuple, causing an error. Not sure why this happens
        if type(self.i) is tuple:
            self.i = self.i[0]
            int(self.i)

        letter_btn = [self.letter_btn1, self.letter_btn2, self.letter_btn3, self.letter_btn4, self.letter_btn5,
                      self.letter_btn6, self.letter_btn7, self.letter_btn8, self.letter_btn9, self.letter_btn10,
                      self.letter_btn11, self.letter_btn12, self.letter_btn13, self.letter_btn14, self.letter_btn15,
                      self.letter_btn16, self.letter_btn17, self.letter_btn18]

        wordlength = len(self.emptyspace)

        for x in range(wordlength):
            # Check if current character is '_', if True, replace with letter on pressed button
            if self.word_buttons[x].text == '_':

                # ' ' and '-' are skipped
                if self.current_word[x] == ' ':
                    self.word_buttons[x + 1].text = letter_btn[self.i].text
                    self.word_buttons[x + 1].state = 'normal'
                elif self.current_word[x] == '-':
                    self.word_buttons[x + 1].text = letter_btn[self.i].text
                    self.word_buttons[x + 1].state = 'normal'
                else:
                    self.word_buttons[x].text = letter_btn[self.i].text
                    self.word_buttons[x].state = 'normal'
                    self.word_buttons[x].disabled = False
                    self.word_buttons[x].color = (1 - self.main_color[0], 1 - self.main_color[1], 1 - self.main_color[2], 1)

                break
            else:
                continue

    # Function used for replacing a typo
    def backspace(self):

        old_charpos = self.charpos + 1

        if self.word_buttons[self.charpos] != '_':
            try:
                self.word_buttons[(old_charpos + 1)].state = 'normal'
            except Exception as e:
                print(e)

    # Function that reveals the first letter in line
    def help(self):

        self.hints_used += 1
        wordlength = len(self.emptyspace)

        if self.hints >= 1:
            self.ids.help_button.disabled = False
        else:
            self.ids.help_button.disabled = True

        letter_btn = [self.letter_btn1, self.letter_btn2, self.letter_btn3, self.letter_btn4, self.letter_btn5,
                      self.letter_btn6, self.letter_btn7, self.letter_btn8, self.letter_btn9, self.letter_btn10,
                      self.letter_btn11, self.letter_btn12, self.letter_btn13, self.letter_btn14, self.letter_btn15,
                      self.letter_btn16, self.letter_btn17, self.letter_btn18]

        # Find out which word_button.text needs to be changed
        for x in range(wordlength):
            # Check if current character is '-', if yes, replace with letter on pressed button
            if self.word_buttons[x].text == '_':
                self.word_buttons[x].text = self.current_word[x].upper()
                self.word_buttons[x].disabled = True  # To ensure that user doesn't remove the hint by accident
                self.word_buttons[x].color = self.main_color
                self.word_buttons[x].hint = True  # To make sure that this button text won't be removed if answer is
                # incorrect

                self.hints -= 1
                self.ids.help_amount.text = str(self.hints)

                break
            else:
                continue

    # Function that allows user to skip a level, preventing getting stuck without hints
    def skip_level(self):

        self.skip = True
        wordlength = len(self.current_word)
        print(self.current_word)

        letter_btn = [self.letter_btn1, self.letter_btn2, self.letter_btn3, self.letter_btn4, self.letter_btn5,
                      self.letter_btn6, self.letter_btn7, self.letter_btn8, self.letter_btn9, self.letter_btn10,
                      self.letter_btn11, self.letter_btn12, self.letter_btn13, self.letter_btn14, self.letter_btn15,
                      self.letter_btn16, self.letter_btn17, self.letter_btn18]

        for x in range(wordlength):
            # Make sure that the correct letters keep the same color, making it easier to see what parts of the word
            # are correct
            if self.word_buttons[x].text == self.current_word[x].upper():
                self.word_buttons[x].text = self.current_word[x].upper()
                self.word_buttons[x].disabled = True
                self.word_buttons[x].color = (1 - self.main_color[0], 1 - self.main_color[1], 1 - self.main_color[2],
                                              .9)
            elif self.word_buttons[x].text != self.current_word[x].upper():
                self.word_buttons[x].text = self.current_word[x].upper()
                self.word_buttons[x].disabled = True
                self.word_buttons[x].color = self.main_color

    # Play a sound if answer is correct
    def victory_sound(self):

        if not self.skip:
            press_sound = None  # Ensure that no sound is loaded
            file = 'resources/Sounds/correct.wav'
            press_sound = SoundLoader.load(file)

            press_sound.volume = .8
            press_sound.play()
        else:
            pass

    # Play a sound if answer is incorrect
    def incorrect_sound(self):

        press_sound = None  # Ensure that no sound is loaded
        file = 'resources/Sounds/incorrect.wav'
        press_sound = SoundLoader.load(file)

        press_sound.volume = .8
        press_sound.play()

    def play_sound(self):

        button_sound = None  # Ensure that no sound is loaded

        # Sound_hint may be reused per word without cost
        if self.sound_used == 1:
            self.sound_hint -= 1
            self.ids.sound_amount.text = str(self.sound_hint)

        self.sound_used = 1

        # Source differs depending on which category is used
        source = 'resources/packs/huis/langs' if store.get("current_pack")["source"] == \
                 "resources/packs/huis/wordlist_house.csv" else "resources/packs/dieren/langs"
        language = self.data.dest_lang.lower()
        file = source + language + '/' + self.current_word + '.mp3'

        button_sound = SoundLoader.load(file)
        button_sound.volume = .8
        button_sound.play()

    # Play sound on button press
    def click_button(self):

        press_sound = None  # Ensure that no sound is loaded
        file = 'resources/Sounds/click_button.wav'
        press_sound = SoundLoader.load(file)

        press_sound.volume = .8
        press_sound.play()

    # Play sound when new high score is achieved
    def new_best_sound(self):

        victory_sound = None  # Ensure that no sound is loaded
        file = 'resources/Sounds/victory.wav'
        victory_sound = SoundLoader.load(file)

        victory_sound.volume = .8
        victory_sound.play()

    # Function that checks if given answer is correct
    def word_checker(self):

        self.answer_to_check = []

        # Typed text will be appended to answer_to_check and the list will be converted to a string to compare it to
        # current_word
        for x in range(len(self.word_buttons)):
            self.answer_to_check.append(self.word_buttons[x].text)

        self.answer_to_check = ''.join([str(elem) for elem in self.answer_to_check])

        # Check if '-' exists in label. If true, level is not finished. If false, check if answer is correct
        if '_' in self.answer_to_check:
            pass
        else:
            # if True, answer is correct and level is finished
            if self.answer_to_check.lower() == self.current_word.lower():

                self.level += 1

                if self.level < 10:

                    self.index = self.index_list[self.level]  # Index +1 to go to next word
                    self.level_finish = True  # Level is finished
                    self.stop_game()

                    self.add_widget(self.next_button)
                    self.ids.sound_button.disabled = True
                    self.ids.help_button.disabled = True
                    self.ids.pass_button.disabled = True

                    self.victory_sound()
                    time.sleep(.8)
                    self.play_sound()

                    # Make letter_btns invisible
                    letter_btn = [self.letter_btn1, self.letter_btn2, self.letter_btn3, self.letter_btn4,
                                  self.letter_btn5,
                                  self.letter_btn6, self.letter_btn7, self.letter_btn8, self.letter_btn9,
                                  self.letter_btn10,
                                  self.letter_btn11, self.letter_btn12, self.letter_btn13, self.letter_btn14,
                                  self.letter_btn15,
                                  self.letter_btn16, self.letter_btn17, self.letter_btn18]

                    for x in range(len(letter_btn)):
                        try:
                            letter_btn[x].opacity = 0
                        except Exception as e:
                            print(e)

                # if True, game is finished
                elif self.level >= 10:
                    self.game_finish = True
                    self.stop_game()

            # Answer incorrect
            else:
                self.incorrect_sound()
                time.sleep(.5)
                self.emptyspace = ('_' * len(self.current_word))

                for x in range(len(self.word_buttons)):
                    if self.word_buttons[x].text != ' ' and self.word_buttons[x].text != '-':
                        if not self.word_buttons[x].hint:
                            self.word_buttons[x].text = '_'
                            self.word_buttons[x].color = (0, 0, 0, 0)
                        else:
                            continue

                self.mistakes += 1

    # Keeping time. Currently, this function (and the other time functions except stop_time) has no use but I'll keep it
    # in the code
    # since I'm planning to make use of these functions at a later time.
    def increment_time(self, interval):

        self.time += .1

    # Function used when level is finished, calculating and awarding a score
    def stop_game(self):
        if self.skip:
            self.score += 0
        elif self.hints_used >= 1 or self.mistakes >= 1 or self.sound_used:
            self.score += (30 - (self.hints_used * 3 + self.mistakes * 3 + self.sound_used * 5))
            self.correct_words += 1
            store["data"]["correct_words"] = self.correct_words
            self.hints_used = 0
            self.mistakes = 0
        elif self.hints_used == 0 and self.mistakes == 0 and self.sound_used == 0:
            self.score += self.points
            self.correct_words += 1
            store["data"]["correct_words"] = self.correct_words
            self.flawless = True

        self.pay_coins()
        self.stop_time()

    # See increment_time()
    def start_time(self):

        self.time = 0
        Clock.schedule_interval(self.increment_time, .1)

    # Stops the game if game is finished, also prevents saving new high score if quiting the game before completing
    # all levels
    def stop_time(self):

        if self.game_finish:
            Clock.unschedule(self.increment_time)

            self.high_score()
            popup = Factory.PopupFinish()
            popup.open()
        elif self.early_stop:
            Clock.unschedule(self.increment_time)
            self.reload()
        else:
            Clock.unschedule(self.increment_time)

    # The name explains itself, see increment_time()
    def pause_time(self):

        if not self.game_finish:

            if not self.level_finish:

                if self.game_pause:
                    Clock.unschedule(self.increment_time)
                elif not self.game_pause:
                    Clock.schedule_interval(self.increment_time, .1)

    # Awards and saves coins
    def pay_coins(self):

        if self.skip:
            self.coins += 0
        elif self.flawless:
            self.coins += self.payout
            self.flawless = False
        elif not self.flawless:
            self.coins += 5

        self.coins_total += self.coins
        if self.game_finish:
            self.coins_earned = self.coins_total  # coins_earned is used for the animation
            self.wallet += self.coins_total
            store.put("wallet", coins=self.wallet)
            self.wallet = store.get("wallet")["coins"]
            print("Wallet: %s" % self.wallet)
            self.new_wallet -= self.coins_total  # new_wallet is used for the animation

    # Function allowing the user to see their wallet increase dynamically, part of the coin animation
    def count_coins(self, dt):

        if self.coins_earned >= 1:
            self.coins_earned -= 1
            self.coins_total -= 1
            self.new_wallet += 1
        else:
            Clock.unschedule(self.count_coins)

    # A simple animation, shows the coins going from the wallet_label to the new_wallet in the end-game popup
    def count_coins_anim(self, coin_ico):

        anim = Animation(opacity=0, duration=.01)
        anim += Animation(pos_hint={'center_x': .5, 'y': .55}, opacity=1, duration=.1)
        anim += Animation(pos_hint={'center_x': .875, 'y': 1.07}, opacity=0, duration=0)

        anim.repeat = True
        anim.start(coin_ico)

        coin_sound = None
        file = 'resources/Sounds/coin copy.wav'
        coin_sound = SoundLoader.load(file)

        coin_sound.volume = .8

        # Make sure the coin sounds are timed as good as possible
        if self.coins_earned > 2:
            coin_sound.loop = True
        if self.coins_earned != 0:
            coin_sound.play()

        # Make sure the coin sounds and animation are timed as good as possible
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

            if theme_prices[x - 10] <= store["data"]["correct_words"]:
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

            if theme_prices[0] <= store["data"]["correct_words"] or theme_prices[1] <= store["data"]["correct_words"] or \
                    theme_prices[2] <= store["data"]["correct_words"]:

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
        self.app_start = True  # ???

        self.time = 0  # Time taken per level

        # self.points = NumericProperty(50)  # Points per level
        self.score = 0  # Total score
        self.highscore = store.get('data')['highscore']  # High score
        self.old_highscore = store.get('data')['highscore']  # Used in end-game popup when new high score is achieved
        self.broke_record = False  # Bool for checking if new high score is achieved
        # self.highscore_label = ObjectProperty()  # Shows high score on menu screen and in-game

        self.correct_words = store.get('data')['correct_words']  # All correct words since playing, used to unlock
        # themes, categories and skins

        self.wallet = store.get('wallet')['coins']  # Coins saved in user_data.json
        # self.wallet_label = ObjectProperty()  # In-game label where wallet is viewed
        self.new_wallet = self.wallet  # Used in the end-game popup's coin animation
        # self.payout = NumericProperty(10)  # Max amount of coins per level

        self.coins = 0  # Amount of coins earned in current level
        self.coins_total = 0  # Amount of coins earned in current game
        self.coins_earned = 0  # ???
        self.mistakes = 0  # Amount of mistakes, used for calculatinh coins

        self.flawless = False  # Check if score is perfect (no hints, no mistakes)

        self.level_finish = False  # Bool to check if current level is cleared
        self.game_finish = False  # Bool to check if game is finished
        self.game_pause = True  # Bool to check if game is paused
        self.early_stop = 0  # ???

        self.i = 0

        self.origin_list = self.data.pack_origin  # Word list in language "main" language
        self.word_list = self.data.pack_dest  # Word list in language that is being learned
        self.index_list = list(self.word_list.keys())  # Index of current word list
        random.shuffle(self.index_list)  # Randomize word order
        self.level = 9  # Current level
        self.index = self.index_list[self.level]  # Index of word used in current level

        # Words for current level
        self.current_word = self.word_list[self.index]
        self.current_word_origin = self.origin_list[self.index]
        self.word = ''
        self.origin_label.text = ''  # Remove label text to prevent it from showing up during countdown

        self.current_image = self.data.pack_img[self.index]  # Image for current level

        self.letters_btn = self.current_word  # Used to assign letters to buttons

        self.emptyspace = ('_' * len(self.current_word))  # Used as text for word_buttons
        # self.grid = GridLayout()  # GridLayout containing the word_buttons
        self.grid_exist = False  # Bool for checking if grid already exists to prevent errors
        self.word_buttons = []  # List containing the word_buttons
        self.charpos = 0  # Position of pressed wordbutton
        self.answer_to_check = []  # Used for checking if user is finished with typing and if answer is correct

        self.charpos = 0  # character location used for backspace and help

        # Hints
        self.hints = 5  # Total amount of hints per game
        self.hints_used = 0  # Amount of hints used in level
        self.sound_hint = 5  # Total amount of sound hints per game
        self.sound_used = 0  # Amount of sound hints used in level

        self.skip = False  # Bool for checking if level is skipped

        self.cd = 3  # Cooldown time

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
        self.word_buttons = []

        self.remove_widget(self.grid)
        self.grid.clear_widgets(children=None)

        self.letters_btn = self.current_word

        try:
            self.image_widget.source = self.current_image
        except AttributeError:
            print(AttributeError)

        try:

            # Empty out all buttons
            letter_btn = [self.letter_btn1, self.letter_btn2, self.letter_btn3, self.letter_btn4, self.letter_btn5,
                          self.letter_btn6, self.letter_btn7, self.letter_btn8, self.letter_btn9, self.letter_btn10,
                          self.letter_btn11, self.letter_btn12, self.letter_btn13, self.letter_btn14, self.letter_btn15,
                          self.letter_btn16, self.letter_btn17, self.letter_btn18]

            for x in range(0, 18):
                letter_btn[x].text = ''
                letter_btn[x].canvas.before.clear()

        except AttributeError:
            print(AttributeError)

        try:
            self.image_widget.opacity = 0
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
            self.add_widget(self.ids.cd_label)
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
            # try:
            self.ids.cd_label.text = str(self.cd)
            # except Exception as e:
            #     print(e)

            print(self.cd)


        elif self.cd == 1:
            self.start_or_menu()
            Clock.unschedule(self.countdown)

    def start_or_menu(self):

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
        self.image_widget.opacity = 1
        self.ids.cd_label.text = str(self.cd)
        self.remove_widget(self.ids.cd_label)

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

        # backgrounddict = {}  # used for bg_unlocked in json file

        for x in range(int(len(data.backgrounds) / 3)):

            for i in range(3):

                bg_button = Factory.BackgroundButton()

                bg_button.backgroundnumber = self.backgroundnumber
                path = f"resources/backgrounds/wallpaper%d.png" % self.backgroundnumber

                if store["background"]["current_bg"] == path:
                    bg_button.state = "down"

                bg_button.bind(on_press=partial(self.update_value, self.backgroundnumber),
                               on_release=partial(self.background_change))
                bg_grid.add_widget(bg_button)
                self.bg_buttons.append(bg_button)

                # backgrounddict[bg_index] = False

                self.backgroundnumber += 1

            for j in range(3):

                if self.buy_backgroundnumber < 10:
                    btn_index = self.buy_backgroundnumber - 1
                    bg_buy_button = Factory.BuyButton()
                    self.bg_buy_buttons.append(bg_buy_button)

                    bg_grid.add_widget(self.bg_buy_buttons[btn_index])
                    self.bg_buy_buttons[btn_index].backgroundnumber_buy = self.buy_backgroundnumber

                    self.bg_buy_buttons[btn_index].bind(on_press=partial(self.update_value, self.buy_backgroundnumber),
                                                        on_release=lambda y: self.checkout())

                    # self.verandervalue(new_val)

                else:
                    bar_index = self.buy_backgroundnumber - 10
                    unlock_bar = Factory.BgBar()
                    self.bg_bars.append(unlock_bar)
                    if bar_index == 0:
                        self.bg_bars[bar_index].max = 50
                        self.bg_bars[bar_index].value = store["data"]["correct_words"]
                        if self.bg_bars[bar_index].value == self.bg_bars[bar_index].max:
                            # self.bg_buttons[self.buy_backgroundnumber].
                            bg_index = 'bg' + str(self.buy_backgroundnumber)
                            self.unlocked_bg[bg_index] = True
                        else:
                            bg_index = 'bg' + str(self.buy_backgroundnumber)
                            self.unlocked_bg[bg_index] = False
                    elif bar_index == 1:
                        self.bg_bars[bar_index].max = 125
                        self.bg_bars[bar_index].value = store["data"]["correct_words"]
                        if self.bg_bars[bar_index].value == self.bg_bars[bar_index].max:
                            # self.bg_buttons[self.buy_backgroundnumber].
                            bg_index = 'bg' + str(self.buy_backgroundnumber)
                            self.unlocked_bg[bg_index] = True
                        else:
                            bg_index = 'bg' + str(self.buy_backgroundnumber)
                            self.unlocked_bg[bg_index] = False
                    elif bar_index == 2:
                        self.bg_bars[bar_index].max = 225
                        self.bg_bars[bar_index].value = store["data"]["correct_words"]
                        if self.bg_bars[bar_index].value == self.bg_bars[bar_index].max:
                            # self.bg_buttons[self.buy_backgroundnumber].
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
        for x in range(len(self.bg_buy_buttons) + 2):
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
