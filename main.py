# Using kivy 2.0.0 and Python 3.8
"""KaruApp - Motivate children to learn a new language

KaruApp is an app that tries to motivate children to learn
new languages by playing a quiz-like game.

This app is created for
smartphones/tablets in landscape mode, but .apk and .ipa versions are
not available yet.

KaruApp requires that 'kivy' and 'pandas' are installed to be able
to run.

*   Please note that the terms 'destination language' (or 'dest_lang') and
    'origin language' (or origin_lang) are used to adress the language of the words
    that the user wants to learn and the language that the user
    already knows respectively. It is assumed that the user is going to type the answers in the
    destination language, but this is not a requirement. The languages can be
    switched freely and these terms are only used to differentiate between the two.
"""
import os
import importlib
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
#os.environ["KIVY_AUDIO"] = "audio_sdl2"
Config.set('graphics', 'width', '360')  # (New Android smartphones e.g. OnePlus 7 series)
Config.set('graphics', 'height', '640')  # (iPhone X, 11 and 12 series, upsampled)
root_widget = Builder.load_file('layout.kv')


# os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'  # Uncomment to prevent OpenGL error if necesarry

# The parent widget
class WindowManager(ScreenManager):
    """This widget class allows the app to have multiple screens.

    Every class that is not a Popup widget is the child widget of WindowManager.

    """
    pass


class Menu(Screen, BoxLayout):
    """ This widget class is the main menu of the app.

    From here the user can see their wallet and high score. There are 3 buttons
    leading to the game, store and settings screen. The logo contains the apps
    mascotte, Karu. It's appearance can be changed in the store. The buttons'
    colors can be changed there as well.

    """
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
        """This function is used to update the wallet- and high score labels.

        """
        self.wallet = store.get('wallet')['coins']
        self.highscore = store.get('data')['highscore']

    def second_color(self):
        """This function is used for creating accent colors.

                The rgba of a pixel from the current background is read using kivy's
                Image.read_pixel() function and put in main_color. This will be used to
                create accent colors.

                This function exists in all the screen widgets to prevent NoneType errors.

                """
        im = store.get("background")["current_bg"]
        m = Image.load(im, keep_data=True)
        self.main_color = m.read_pixel(20, 10)
        print(self.main_color)

    def check_skin(self):
        """This function is used to check the current skin.

        This ensures that Karu's appearance is updated correctly.

        """
        self.skin = store["skin"]["current_skin"]
        print(self.skin)


class GameWidget(Screen, FloatLayout):
    """This widget class is where the game is located.

    Arguments:
    ----------
    data : packData.py module
    bg : str
        The path of the current background
    main_color : tuple
        RGBA values of the current background
    cd : int
        Countdown time (defaults to 3)
    time : float
        Time per level in seconds
    points : int
        Maximum points per level (defaults to 40)
    score : int
        Total score
    highscore : int
        High score stored in user_data.json
    old_highscore : int
        Previous highscore (defaults to highscore's value)
    broke_record : Bool
        Used for checking if new a high score is achieved
    wallet : int
        Coins stored in user_data.json
    new_wallet : int
        Used for coin_count_anim() (defaults to wallet's value)
    payout : int
        Maximum amount of coins per level
    coins : int
        Coins earned in current level
    coins_total : int
        Coins earned in current game
    coins_earned : int
        Used for count_coins() (defaults to coins_total)
    correct_words : int
        All correct words since playing
    letter_btn1-18 : button widget
        All buttons used for typing
    level_finish : bool
        Used for checking if level is finished
    game_finish : bool
        Used for checking if game is finished
    game_pause : bool
        Used for checking if game is paused
    early_stop : bool
        Used for checking if game is stopped without finishing
    word_list : dict
        W word list in the destination language created in packData.py
    origin_list : dict
        Same word list as word_list, but in the origin language
    index_list : list
        A list containing the index of the current word list
    level : int
        The current level
    index : int
        The index of the word in the current level
    current_word : str
        The current word in the destination language
    current_word_origin : str
        The current word in the origin language
    word : str
        Used for removing ' ' and '-' without altering current_word
    current_image : str
        The path of the image used in current level
    letters_btn : str
        The letters that are needed for letter_btns (defaults to current_word)
    emptyspace : str
        Used for checking how many un-typed characters exist in the answer
    grid : GridLayout widget
        A GridLayout for containing the word_buttons
    grid_exist : bool
        Used for checking if grid exists
    word_buttons : list
        A list containing the word_buttons
    charpos : int
        The position of where the next character will be typed
    hints : int
        The amount of available hints per game (defaults to 5)
    hints_used : int
        The amount of hints used per level
    sound_hint : int
        The amount of available sound hints per game (defaults to 5)
    sound_used : int
        The amount of sound hints used per level
    flawless : bool
        Used for checking if score is perfect (no hints, no mistakes)
    mistakes : int
        Amount of incorrect answers given per level
    answer_to_check : list
        Used for checking if user is finished with typing and if answer is correct
    skip : bool
        Used for checking if current level is skipped

    Methods:
    -------
    proceed()
        This function lets the game proceed to the next level.
    word_letter_buttons()
        This function randomizes letter_btns text and sets word_buttons text.
    type_word()
        This function lets the letter_btns be used for typing words.
    text_cursor()
        This function creates a simple text cursor animation
    backspace()
        A function used for correcting typos.
    hint()
        This function reveals a letter as a hint.
    skip_level()
        This function allows the user to skip the current level.
    victory_sound()
        A function that plays a .wav file when an answer is correct.
    incorrect_sound()
        A function that plays a .wav file when an answer is incorrect.
    play_sound()
        A function that plays a .wav file when sound_button is pressed or when
        level is completed/skipped.
    click_button()
        A function that plays a .wav file at every button press.
    new_best_sound()
        A function that plays a .wav file when new high score is achieved.
    word_checker()
        This function checks if user has finished typing an answer and
        if said answer is correct.
    increment_time(interval)
        *Temporarily not used*
        Used to keep time
    stop_level()
        This function calculates and awards points when a level is finished.
    start_time(interval)
        *Temporarily not used*
        This function calls increment_time() using Kivy's Clock object
    stop_game()
        This function stops the game if game_finish is true. It also prevents
        the high score and coins from being saved if user quits without finishing
        the game.
    pause_time()
        *Temporarily not used*
        This function pauses time when the pause popup is opened
    pay_coins()
        This function awards coins and saves those coins in the user_data.json
        file.
    count_coins(dt)
        A function that is part of an animation. It allows the user to see their
        wallet increase dynamically.
    count_coins_anim(coin_ico, *largs)
        A function that plays a simple animation. It shows how the coins move
        from the in-game wallet label to the PopupFinish's new_wallet label.
    high_score()
        A function that checks if a new high score is achieved and saves that
        new high score in the user_data.json file.
    unlock_notification(notification, notification2, *largs)
        A function that shows one or two notification if a new skin or
        theme is unlocked.
    reload():
        This function resets most of the variables and widget-values.
        Some widgets are added or removed.
    second_color():
        This function retrieves the main_color of the current background, which
        is used to create accent colors. (This function exists in
        all the screen widgets)
    countdown(dt)
        This function is used with the cd_label (countdown_label) to do a
        countdown before the game starts.
    start_game()
        This function deletes and adds widgets, changes or resets variables and
        runs necessary functions to enable the game to start.



    """

    data = packData

    bg = ObjectProperty(data.current_bg)  # The current background
    main_color = ObjectProperty((1, 1, 1, 1))  # Used for setting accent colors
    cd = 3  # Countdown time

    time = NumericProperty()  # Time taken per level

    points = NumericProperty(40)  # Points per level
    score = NumericProperty(0)  # Total score
    highscore = NumericProperty(store.get('data')['highscore'])
    old_highscore = NumericProperty(store.get('data')['highscore'])  # Used in end-game popup when new high score is
    # achieved
    broke_record = BooleanProperty(False)  # Bool for checking if new high score is achieved

    wallet = NumericProperty(store.get('wallet')['coins'])
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
    early_stop = 0  # ???
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

    def __init__(self, **kwargs):

        super(GameWidget, self).__init__(**kwargs)
        #help(self.proceed)

    def proceed(self):
        """This function lets the game proceed to the next level.

        Widgets and variables that need to change to proceed to the next level
        will be changed. Only the 'next_button' widget is removed since it is
        only useable after a level is finished or skipped. Once all of that is
        done, the function 'word_letter_btns()' is called.

        """


        self.level_finish = False

        self.time = 0
        self.coins = 0
        self.mistakes = 0
        self.sound_used = 0
        self.hints_used = 0
        self.skip = False

        self.current_word = self.word_list[self.index]
        self.current_word_origin = self.origin_list[self.index]
        self.ids.origin_label.text = self.current_word_origin
        self.current_image = self.data.pack_img[self.index]
        self.emptyspace = ('_' * len(self.current_word))

        self.letters_btn = self.current_word  # Set letter_btns letters to the letters needed for current level
        self.ids.image_widget.source = self.current_image  # Change image source to current_image
        self.ids.pass_button.disabled = False
        self.remove_widget(self.ids.next_button)

        if self.hints > 0:
            self.ids.help_button.disabled = False

        if self.sound_hint > 0:
            self.ids.sound_button.disabled = False

        self.word_letter_btns()

    # Function that randomises letter_btns text and sets word_buttons text
    def word_letter_btns(self):
        """This function randomizes letter_btns text and sets word_buttons text.

        The destination language will be checked because some languages use
        different alphabets. The letters in current_word will be added to the
        list letters_btn, together with random letters from one of the alphabets.
        When the list contains 18 different characters, each of them will be
        assigned to the letter_btns.

        When that is done, the GridLayout containing word_buttons will be
        created.

        """

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

        # Put characters in a list
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

        # Create the grid and word_buttons
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
        # Create the word_buttons
        for x in range(len(self.current_word)):
            word_button = Factory.WordButton()
            self.grid.add_widget(word_button)
            # word_button.secondary_color = (
            #     1 - self.main_color[0], 1 - self.main_color[1], 1 - self.main_color[2], .75)
            word_button.secondary_color2 = (1, 1, 1, .7)

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

        self.text_cursor()
        self.start_time()

    # Function for typing words
    def type_word(self):
        """This function lets the letter_btns be used for typing words.

        A simple for-loop is used for typing. When a letter_btn is pressed, the
        for-loop will iterate through the word_buttons until it comes across a
        word_button that has the text value '_'. The word_button.text will be
        changed to the letter_btn.text and then the loop will break. Dashes and
        spaces are skipped.

        """

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

                self.text_cursor()
                break
            else:
                continue

    # A simple animation for the text cursor
    def text_cursor(self):
        """This function creates a simple text cursor animation

        The animation fades between the word_button's usual color and the accent color.

        """
        animated_color = 1 - self.main_color[0], 1 - self.main_color[1], 1 - self.main_color[2], 1
        anim = Animation(secondary_color=(animated_color), duration=.75)
        anim += Animation(secondary_color=(1, 1, 1, .7), duration=.75)
        anim.repeat = True

        wordlength = len(self.emptyspace)

        for x in range(wordlength):
            # Check if current character is '_', if True, replace with letter on pressed button
            anim.cancel_all(self.word_buttons[x-1])
            self.word_buttons[x - 1].secondary_color = (1, 1, 1, .7)
            #state = 'normal'

            if self.word_buttons[x].text == '_':
                print(f'button%d animation started' % x)
                anim.start(self.word_buttons[x])
                break


    # Function used for replacing a typo
    def backspace(self):
        """A function used for correcting typos.

        This is a simple function that removes the text from a word_button and
        sets the charpos to that button, allowing a typo to be fixed. It also
        makes sure that the text_cursor() position is correct.

        """
        old_charpos = self.charpos + 1
        for x in range(len(self.word_buttons)):
            Animation.cancel_all(self.word_buttons[x])
            self.word_buttons[x].secondary_color = (1, 1, 1, .7)

        # self.word_buttons[self.charpos].secondary_color = (
        #     1 - self.main_color[0], 1 - self.main_color[1], 1 - self.main_color[2], .75)

        if self.word_buttons[self.charpos] != '_':
            try:
                self.word_buttons[(old_charpos + 1)].state = 'normal'
                self.text_cursor()
            except Exception as e:
                print(e)

    # Function that reveals the first letter in line
    def hint(self):
        """This function reveals a letter as a hint.

        When the help_button is pressed, a for-loop will iterate through the
        word_buttons until it comes across a word_button that has the text value '_'.
        This button's text value will change to the correct letter for that button.

        """

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
                self.text_cursor()

                break
            else:
                continue

    # Function that allows user to skip a level, preventing getting stuck without hints
    def skip_level(self):
        """This function allows the user to skip the current level.

        A for-loop is used to fill in every word_button with the text value '_'.
        The letters filled in by the for-loop are in another color than the
        letters that the user filled in if those letters were correct.

        """

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
        """A function that plays a .wav file when an answer is correct.

        """

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
        """A function that plays a .wav file when an answer is incorrect.

        """

        press_sound = None  # Ensure that no sound is loaded
        file = 'resources/Sounds/incorrect.wav'
        press_sound = SoundLoader.load(file)

        press_sound.volume = .8
        press_sound.play()

    def play_sound(self, *largs):
        """A function that plays a .wav file when sound_button is pressed, or when
        the level is completed/skipped.

        """

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
        """A function that plays a .wav file at every button press.

        """

        press_sound = None  # Ensure that no sound is loaded
        file = 'resources/Sounds/click_button.wav'
        press_sound = SoundLoader.load(file)

        press_sound.volume = .8
        press_sound.play()

    # Play sound when new high score is achieved
    def new_best_sound(self):
        """A function that plays a .wav file when new high score is achieved.

        """

        victory_sound = None  # Ensure that no sound is loaded
        file = 'resources/Sounds/victory.wav'
        victory_sound = SoundLoader.load(file)

        victory_sound.volume = .8
        victory_sound.play()

    # Function that checks if given answer is correct
    def word_checker(self):
        """This function checks if user has finished typing an answer and
        if said answer is correct.

        First, the answer_to_check list will be filled with the word_buttons text
        using a for-loop. After the list in joined into a string, it will go
        through an if-statement to check if the answer is complete. Then,
        answer_to_check will be checked if the answer is correct. If it is, the
        user may proceed to the next level, unless the current level is the final
        level. If the answer was incorrect, the word_buttons' text will be reset
        with an exception of word_buttons that were filled in by the help()
        function.

        """

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
                    self.stop_level()

                    try:
                        self.add_widget(self.ids.next_button)
                    except Exception as e:
                        print(e)
                    self.ids.sound_button.disabled = True
                    self.ids.help_button.disabled = True
                    self.ids.pass_button.disabled = True

                    self.victory_sound()
                    Clock.schedule_once(self.play_sound, .8)

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

                    for x in range(len(self.word_buttons)):
                        Animation.cancel_all(self.word_buttons[x])
                        self.word_buttons[x].secondary_color = (1, 1, 1, .7)

                # if True, game is finished
                elif self.level >= 10:
                    self.game_finish = True
                    self.stop_level()

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
                self.text_cursor()

    # Keeping time. Currently, this function (and the other time functions except stop_time) has no use but I'll keep it
    # in the code
    # since I'm planning to make use of these functions at a later time.
    def increment_time(self, interval):
        """*Temporarily not used*

        Used to keep time

        """

        self.time += .1

    # Function used when level is finished, calculating and awarding a score
    def stop_level(self):
        """This function calculates and awards points when a level is finished.

            """
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
        self.stop_game()


    # See increment_time()
    def start_time(self):
        """*Temporarily not used*

        This function calls increment_time() using Kivy's Clock object

        """

        self.time = 0
        Clock.schedule_interval(self.increment_time, .1)

    # Stops the game if game is finished, also prevents saving new high score if quiting the game before completing
    # all levels
    def stop_game(self):
        """This function stops the game if game_finish is true.

        It also prevents the high score and coins from being saved if user quits
        without finishingthe game.

        """

        if self.game_finish:
            Clock.unschedule(self.increment_time)

            self.high_score()
            popup = Factory.PopupFinish()
            Clock.schedule_once(popup.open, 1)
            #popup.open()
        elif self.early_stop:
            Clock.unschedule(self.increment_time)
            self.reload()
        else:
            Clock.unschedule(self.increment_time)

    # The name explains itself, see increment_time()
    def pause_time(self):
        """*Temporarily not used*

        This function pauses time when the pause popup is opened

        """

        if not self.game_finish:

            if not self.level_finish:

                if self.game_pause:
                    Clock.unschedule(self.increment_time)
                elif not self.game_pause:
                    Clock.schedule_interval(self.increment_time, .1)

    # Awards and saves coins
    def pay_coins(self):
        """This function awards coins and saves those coins in the user_data.json
        file.

        Coins are not saved if the user quits the game before finishing it and no
        coins are awarded if the user skips the level.

        """

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
        """A function that i allows the user to see their wallet increase
        dynamically.

        This function is used together with count_coins_anim

        """

        if self.coins_earned >= 1:
            self.coins_earned -= 1
            self.coins_total -= 1
            self.new_wallet += 1
        else:
            Clock.unschedule(self.count_coins)

    # A simple animation, shows the coins going from the wallet_label to the new_wallet in the end-game popup
    def count_coins_anim(self, coin_ico, *largs):
        """A function that plays a simple animation.

        It shows how the coins move from the in-game wallet label to the
        PopupFinish's new_wallet label.

        :param class coin_ico: the widget that needs to be animated

        """

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
            """ This is a simple function that makes sure that the animation and
            sounds are timed correctly, depending on the amount of coins left to
            add to the new_wallet.

            """

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
        """A function that checks if a new high score is achieved

        If a new high score is achieved it will be saved to user_data.json,
        unless the game has been stopped before finishing it.

        """

        if self.score > self.highscore:
            store["data"]["highscore"] = self.score
            self.highscore = store.get("data")["highscore"]
            self.ids.highscore_label.text = str(self.highscore)
            self.broke_record = True
            print(f'hs:%d' % self.highscore)
            print(f'hs_old:%d' % self.old_highscore)
            print(self.broke_record)

        print(self.broke_record)

    def unlock_notification(self, notification, notification2, *largs):
        """A function that shows one or two notification if a new skin or
        theme is unlocked.

        While-loops and if-statements are used to check if the skin/theme is
        already unlocked and to unlock it if necesarry.

        :param class notification: The notification bar that needs to be animated
        :param class notification2: The notification bar that needs to be animated

        """

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
        """This function resets the game.

        Most of the variables and widget-values will be reset and sp,e of the
        widgets are added or removed. There are a lot of unnecesarry try-except
        blocks that will be replaced in a future update.

        """

        importlib.reload(packData)
        self.data = packData
        self.bg = self.data.current_bg

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
        self.early_stop = False  # ???

        self.i = 0

        self.origin_list = self.data.pack_origin  # Word list in language "main" language
        self.word_list = self.data.pack_dest  # Word list in language that is being learned
        self.index_list = list(self.word_list.keys())  # Index of current word list
        random.shuffle(self.index_list)  # Randomize word order
        self.level = 0  # Current level
        self.index = self.index_list[self.level]  # Index of word used in current level

        # Words for current level
        self.current_word = self.word_list[self.index]
        self.current_word_origin = self.origin_list[self.index]
        self.word = ''
        self.ids.origin_label.text = ''  # Remove label text to prevent it from showing up during countdown

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
            self.ids.image_widget.source = self.current_image
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
            self.ids.image_widget.opacity = 0
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
            self.remove_widget(self.ids.next_button)
        except:
            print('No next_button to remove')

        try:
            self.add_widget(self.ids.cd_label)
        except:
            print('cd_label already exists')

    def second_color(self):
        """This function is used for creating accent colors.

        The rgba of a pixel from the current background is read using kivy's
        Image.read_pixel() function and put in main_color. This will be used to
        create accent colors.

        This function exists in all the screen widgets to prevent NoneType errors.

        """

        im = store.get("background")["current_bg"]
        m = Image.load(im, keep_data=True)
        self.main_color = m.read_pixel(20, 10)
        print(self.main_color)

    # Countdown till game starts
    def countdown(self, dt):
        """This function is used for a countdown before the game starts.

        """

        if self.cd > 1:
            self.cd -= 1
            # try:
            self.ids.cd_label.text = str(self.cd)
            # except Exception as e:
            #     print(e)

            print(self.cd)


        elif self.cd == 1:
            self.start_game()
            Clock.unschedule(self.countdown)

    def start_game(self):
        """This function is used to start the game.

        It deletes and adds widgets, changes or resets variables and
        runs necessary functions to enable the game to start. Like the reload()
        function, there are a lot of try-except blocks that still need to be
        replaced.

        """

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

        self.proceed()
        self.ids.image_widget.opacity = 1
        self.ids.cd_label.text = str(self.cd)
        self.remove_widget(self.ids.cd_label)


# Location of PopupBg, PopupSkins and PopupPacks
class KaruStore(Screen, BoxLayout):
    """This widget class is where the popups for the themes, skins and word
    packs are located.

    """
    main_color = ObjectProperty((1, 1, 1, 1))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.second_color()

    def second_color(self):
        """This function is used for creating accent colors.

        The rgba of a pixel from the current background is read using kivy's
        Image.read_pixel() function and put in main_color. This will be used to
        create accent colors.

        This function exists in all the screen widgets to prevent NoneType errors.

        """

        im = store.get("background")["current_bg"]
        m = Image.load(im, keep_data=True)
        self.main_color = m.read_pixel(20, 10)


# Popup for unlocking and changing backgrounds
class PopupBg(Popup):
    """This class is the Popup widget where themes can be unlocked and changed.

    In the code of KaruApp and it's modules,you will find a lot of refferences to
    'themes' and to 'backgrounds'. These are one and the same (except for the
    background values and functions from Kivy). The term  'background' will be
    completely replaced by 'theme' in a future update"""

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
        """This __init__ function makes sure that the layout is correct.

        All necesarry buttons and progress bars are added using for-loops.
        It will also check which buttons need to be unlocked and assign the
        correct values to the progress bars. The button containing the current
        background will be highlighted.

        """
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
                else:
                    bar_index = self.buy_backgroundnumber - 10
                    unlock_bar = Factory.BgBar()

                    self.bg_bars.append(unlock_bar)
                    if bar_index == 0:
                        print('i equal 0')
                        self.bg_bars[bar_index].max = 50
                        self.bg_bars[bar_index].value = store["data"]["correct_words"]
                        self.bg_bars[bar_index].ids.bar_label.text = "{}/{}".format(self.bg_bars[bar_index].value,
                                                                                    self.bg_bars[bar_index].max)
                        self.bg_bars[bar_index].ids.bar_label.pos = (self.bg_bars[bar_index].x + 70, self.bg_bars[
                            bar_index].y + 70)
                        # if self.bg_bars[bar_index].value >= self.bg_bars[bar_index].max:
                        #     # self.bg_buttons[self.buy_backgroundnumber].
                        #     bg_index = 'bg' + str(self.buy_backgroundnumber)
                        #     self.unlocked_bg[bg_index] = True
                        # else:
                        #     bg_index = 'bg' + str(self.buy_backgroundnumber)
                        #     self.unlocked_bg[bg_index] = False
                    if bar_index == 1:
                        print('i equal 1')
                        self.bg_bars[bar_index].max = 125
                        self.bg_bars[bar_index].value = store["data"]["correct_words"]
                        self.bg_bars[bar_index].ids.bar_label.text = "{}/{}".format(self.bg_bars[bar_index].value,
                                                                                    self.bg_bars[bar_index].max)
                        self.bg_bars[bar_index].ids.bar_label.pos = (self.bg_bars[bar_index].x + 250, self.bg_bars[
                            bar_index].y + 70)
                        # if self.bg_bars[bar_index].value >= self.bg_bars[bar_index].max:
                        #     # self.bg_buttons[self.buy_backgroundnumber].
                        #     bg_index = 'bg' + str(self.buy_backgroundnumber)
                        #     self.unlocked_bg[bg_index] = True
                        # else:
                        #     bg_index = 'bg' + str(self.buy_backgroundnumber)
                        #     self.unlocked_bg[bg_index] = False
                    if bar_index == 2:
                        print('i equal 2')
                        self.bg_bars[bar_index].max = 225
                        self.bg_bars[bar_index].value = store["data"]["correct_words"]
                        self.bg_bars[bar_index].ids.bar_label.text = "{}/{}".format(self.bg_bars[bar_index].value,
                                                                                    self.bg_bars[bar_index].max)
                        self.bg_bars[bar_index].ids.bar_label.pos = (self.bg_bars[bar_index].x + 430, self.bg_bars[
                            bar_index].y + 70)
                        # if self.bg_bars[bar_index].value >= self.bg_bars[bar_index].max:
                        #     # self.bg_buttons[self.buy_backgroundnumber].
                        #     bg_index = 'bg' + str(self.buy_backgroundnumber)
                        #     self.unlocked_bg[bg_index] = True
                        # else:
                        #     bg_index = 'bg' + str(self.buy_backgroundnumber)
                        #     self.unlocked_bg[bg_index] = False

                    bg_grid.add_widget(self.bg_bars[bar_index])

                self.buy_backgroundnumber += 1

        self.add_widget(bg_scrollview)
        print(self.unlocked_bg)

        # Loop to check which backgrounds are unlocked, so the buttons can be enabled and disabled where needed
        self.backgroundnumber = 1
        for x in range(len(self.bg_buy_buttons)):
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
                print('hey ;)')

        for x in range(len(self.bg_bars)):
            try:
                bg_index = 'bg{}'.format(x + 10)
                print(bg_index)
                print(store['unlocked_backgrounds'][bg_index])
                if store['unlocked_backgrounds'][bg_index]:
                    # Remove lock button and img
                    self.bg_buttons[(x + 9)].remove_widget(self.bg_buttons[(x + 9)].ids.lock_img)
                    self.bg_buttons[(x + 9)].remove_widget(self.bg_buttons[(x + 9)].ids.lock_button)
                    self.unlocked_amount += 1

            except Exception as e:
                print(repr(e))


    def update_value(self, val, *largs):
        """This function corrects the value of the backgroundnumbers

        Backgroundnumber and buy_backgroundnumber keep the value of the last
        button that is created. This function prevents that from happening, by
        changing their values to 'val'. which is the (buy_)backgroundnumber of
        the button from when it was created.

        :param int val: the correct (buy_)backgroundnumber

        """
        print(f'value is %d' % val)
        print(f'bg no is %d' % self.backgroundnumber)
        self.backgroundnumber = val
        self.buy_backgroundnumber = val

    def checkout(self):
        """This function unlocks themes using KaruCoins (KC)

        Every theme costs 250KC. An if-statement will check if the amount of
        coins in the wallet exceeds the price and unlocks the theme if it does.

        When a theme is unlocked, the 'lock button' is removed, the buy button
        is disabled and changed to a 'check' icon, the theme is saved in
        user_data.json and the coins are taken out of the wallet.

        """
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
        """This is a simple function that changes and saves the current background

        """
        btn_in_list = self.backgroundnumber - 1
        self.current_bg = self.backgroundnumber

        store.put("background", current_bg=packData.backgrounds[self.current_bg])

        KaruApp.WindowManager.ids.ks.second_color()
        KaruApp.WindowManager.ids.mainmenu.second_color()
        KaruApp.WindowManager.ids.gw.second_color()
        KaruApp.WindowManager.ids.settings.second_color()


# Popup for unlocking and changing skins
class PopupSkins(Popup):
    """This class is the Popup widget where themes can be unlocked and changed.

    The code of this class is relatively short compared to the code of PopupBg.
    This is because most of the code is written in Kivy's kv-language, located in
    layout.kv, and because it's more convenient to use kv-language for these
    kinds of tasks if there aren't many different skins to work with.

    This class will look more like PopupBg when more skins are added in a future
    update.

    """
    current_skin = ObjectProperty(store.get("skin")["current_skin"])

    def __init__(self, **kwargs):
        """This __init__ function ensures that the correct skin is selected
        when the popup is opened."""
        super().__init__(**kwargs)

        self.current_skin = store.get("skin")["current_skin"]

    def skin_switch(self):
        """This is a simple function that changes and saves the current skin.

        """
        print(self.current_skin)
        store.put("skin", current_skin=self.current_skin)


# Popup for unlocking and changing word packs
class PopupPacks(Popup):
    """This class is the Popup widget where word packs can be unlocked and changed.

    There are only two packs available at this moment. That is why, just like PopupSkins,
    this class' code is very short.
    """

    current_pack = ObjectProperty(store.get("current_pack")["source"])
    def __init__(self, **kwargs):
        """This __init__ function ensures that the correct skin is selected
                when the popup is opened."""
        super().__init__(**kwargs)
        self.current_pack = store.get("current_pack")["source"]

    def pack_switch(self):
        """This is a simple function that changes and saves the current pack.

        """
        print(self.current_pack)
        store.put("current_pack", source=self.current_pack)


class SettingsScreen(Screen, BoxLayout):
    """This widget class contains the games settings.

    The only settings that can be changed in this version of KaruApp are the
    destination- and origin languages. More settings will be added in future
    updates."""
    # Empty variables that will be filled using the flag buttons (see layout.kv line 951-1290)
    origin_lang = ""
    dest_lang = ""
    main_color = ObjectProperty((1, 1, 1, 1))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.second_color()

    def second_color(self):
        """This function is used for creating accent colors.

        The rgba of a pixel from the current background is read using kivy's
        Image.read_pixel() function and put in main_color. This will be used to
        create accent colors.

        This function exists in all the screen widgets to prevent NoneType errors.

        """

        im = store.get("background")["current_bg"]
        m = Image.load(im, keep_data=True)
        self.main_color = m.read_pixel(20, 10)
        print(self.main_color)

    # Choose the origin language (would usually be user's native language)
    def choose_origin(self):
        """This is a simple function to change the origin language
        """
        # Changes "origin_lang" in user_data.json to chosen language. packData.py uses this json file for making and
        # importing wordlists
        store.put("origin_lang", language=self.origin_lang)

    # Choose the destination language (this is the language user wants to learn)
    def choose_dest(self):
        """This is a simple function to change the destination language
                """
        # Changes "dest_lang" in user_data.json to chosen language. packData.py uses this json file for making and
        # importing wordlists
        store.put("dest_lang", language=self.dest_lang)


class KaruApp(App):
    """This is the main class of KaruApp, allowing the app to run
    """
    WindowManager = WindowManager()

    def build(self):
        self.icon = 'resources/icons/karuicon.png'
        return self.WindowManager


KaruApp().run()

