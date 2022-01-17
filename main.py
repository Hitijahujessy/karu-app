import kivy
import os

from kivy.config import Config  # For setting height (19.5:9)
from kivy.graphics import Rectangle

Config.set('graphics', 'width', '360')  # (New Android smartphones e.g. OnePlus 7 series)
Config.set('graphics', 'height', '640')  # (iPhone X, 11 and 12 series, upsampled)

from kivy.app import App
from kivy.lang import Builder

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.image import Image, CoreImage  # For accessing pictures
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup

from kivy.properties import ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.clock import Clock  # For retrieving playtime and getting score
from kivy.storage.jsonstore import JsonStore
import json

import random
import time
import packData
import karuData

kivy.require('2.0.0')  # Version of Kivy
store = JsonStore('resources/user_data.json')  # For saving high score


# os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'  # To prevent OpenGL error


# Mascot
class KaruWidget(Widget):
    data = karuData
    speech = data.starttext
    pass


class AmbonWidget(Widget):
    karu = KaruWidget()
    karulabel = ObjectProperty(None)

    time_total = NumericProperty()  # Total playtime
    time = NumericProperty()  # Time taken per image

    points = NumericProperty(50)  # Points per level
    score = NumericProperty()  # Total score
    highscore = NumericProperty(store.get('data')['highscore'])  # Total score
    highscore_label = ObjectProperty()

    wallet = NumericProperty(store.get('wallet')['coins'])  # User's saved coins
    wallet_label = ObjectProperty()  # In-game label where wallet is viewed
    payout = NumericProperty(10)  # Max amount of coins per level
    coins = NumericProperty(0)  # Amount of coins earned in current level
    mistakes = 0  # Amount of mistakes, used for awarding coins

    flawless = False  # Check if score is perfect (<5sec, no hints, no mistakes)

    level_finish = False  # Bool to check if current level is cleared

    bg = ObjectProperty()
    bg = store.get('custom')['current_bg']

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

    # Button to go to next level if level_finish == True
    next_button = ObjectProperty(None)

    help_button = ObjectProperty(None)
    app_start = True
    start_btn = ObjectProperty(None)
    start_img = ObjectProperty(None)

    back_to_menu = ObjectProperty(None)
    finish_label = ObjectProperty(None)
    game_finish = False
    game_pause = True
    go_to_menu = False

    # i = letterBtn pressed (i.e. i = 0 = letterBtn1)
    i = 0

    # Label for viewing answer (when blank = '_____')
    answer = ObjectProperty(None)

    # Image widget for viewing current image
    imagewidget = ObjectProperty(None)

    ### WORDS Function ###

    # import module packData, containing image's and corresponding words, also randomize index for variation
    data = packData
    wordlist = data.pack1  # Current list of words
    indexlist = [0, 1, 2, 3, 4]  # Index current word
    random.shuffle(indexlist)
    level = 0
    index = indexlist[level]

    # Word for current level
    currentWord = wordlist[index]

    # Image for current level
    currentImage = data.pack1img[index]

    # Used to assign letters to buttons
    letters_btn = currentWord

    # Used as text for label
    emptyspace = ('_' * len(currentWord))

    # character location used for backspace and help
    charloc = 0

    # Hints
    hints = 5  # Total amount of hint per game
    hints_used = 0  # Amount of hints used in level

    def __init__(self, **kwargs):

        super(AmbonWidget, self).__init__(**kwargs)

        # Start randomizeLetters() to randomize and add letters to letterBtns
        # self.randomizeLetters()

    # Function for changing words and images when answer correct
    def words(self):

        # Check if level is cleared
        if self.level_finish:

            if self.hints <= 0:
                self.karulabel.text = self.karu.data.nohints
            else:
                self.karulabel.text = self.karu.data.starttext
                self.help_button.disabled = False

            self.level_finish = False  # New level started, level finish = false
            self.next_button.disabled = True
            self.next_button.text = ''
            self.answer.color = 1, 1, 1

            self.time = 0
            self.coins = 0
            self.mistakes = 0

            self.currentWord = self.wordlist[self.index]  # New word
            self.currentImage = self.data.pack1img[self.index]  # Corresponding image
            self.emptyspace = ('_' * len(self.currentWord))  # Set empty space ('-') to len(currentWord)

            # Clear answer label
            self.answer.text = self.emptyspace

            self.letters_btn = self.currentWord

            self.imagewidget.source = self.currentImage

            print(self.answer.text)  # Test if answer label is updated
            print(self.currentWord)  # Test if currentWord is updated
            print(self.currentImage)  # Test if currentImage is updated
            print(self.emptyspace)  # Test if empty space is updated

            self.randomizeLetters()  # Randomize letters for buttons

    # Function for randomizing letters for buttons
    def randomizeLetters(self):

        self.pause()

        self.imagewidget.opacity = 1

        all_letters = list("abcdefghijklmnopqrstuvwxyz")  # Possible letters for randomizing
        letters_needed = 12 - len(
            self.currentWord)  # 12 letters are needed in total, X letters already exist in current Word
        # Turn all letterBtn variables into a list for efficiency
        letterBtn = [self.letterBtn1, self.letterBtn2, self.letterBtn3, self.letterBtn4, self.letterBtn5,
                     self.letterBtn6, self.letterBtn7, self.letterBtn8, self.letterBtn9, self.letterBtn10,
                     self.letterBtn11, self.letterBtn12]
        # self.letters_btn = self.letters_btn

        # Add possible characters to list including currentWord
        for x in range(letters_needed):

            # letters_btn length may not exceed 12
            if len(self.letters_btn) != 12:

                add_letter = random.choice(all_letters)  # Choose random letter from all_letters
                self.letters_btn += add_letter  # Append chosen letter to letters_btn
                continue

            else:
                break
        self.letters_btn = list(self.letters_btn)
        random.shuffle(self.letters_btn)  # Shuffle letters to prevent currentWord from appearing in correct order
        print(self.letters_btn)  # Check list of letters to make sure that new list is indeed updated
        self.letters_btn = str(self.letters_btn)
        self.letters_btn = self.letters_btn.replace(' ', '')
        self.letters_btn = self.letters_btn.replace(',', '')
        self.letters_btn = self.letters_btn.replace('[', '')
        self.letters_btn = self.letters_btn.replace(']', '')
        self.letters_btn = self.letters_btn.replace("'", '')
        self.letters_btn = self.letters_btn.upper()

        # Assign characters to buttons
        for x in range(12):
            letterBtn[x].text = self.letters_btn[x]

    # Function for typing words
    def typeWord(self):

        # To prevent tuples, which happens for some reason
        if type(self.i) is tuple:
            self.i = self.i[0]
            int(self.i)

        # Turn all letterBtn variables into a list for efficiency
        letterBtn = [self.letterBtn1, self.letterBtn2, self.letterBtn3, self.letterBtn4, self.letterBtn5,
                     self.letterBtn6, self.letterBtn7, self.letterBtn8, self.letterBtn9, self.letterBtn10,
                     self.letterBtn11, self.letterBtn12]

        # Get amount of characters in 'answer' label for iteration
        wordlength = len(self.emptyspace)

        # Turn emptyspace in list, used for replacing and appending characters.
        labeltext = list(self.emptyspace)

        for i in range(1, 12):
            letterBtn[i].state = 'normal'
            if self.hints > 0:
                self.help_button.disabled = False
        for x in range(wordlength):

            # Check if current character is '-', if yes, replace with letter on pressed button
            if labeltext[x] == '_':

                # Replace current '-' with button text
                labeltext[x] = letterBtn[self.i].text

                # Turn list in string so it can be used in 'answer' label
                labeltext = ''.join(map(str, labeltext))

                # Update label and emptyspace
                self.emptyspace = labeltext
                self.answer.text = labeltext
                self.charloc = x

                break

            else:

                continue

    def backspace(self):

        labeltext = list(self.emptyspace)
        labeltext[self.charloc] = '_'

        # Turn list in string so it can be used in 'answer' label
        labeltext = ''.join(map(str, labeltext))

        # Update label and emptyspace
        self.emptyspace = labeltext
        self.answer.text = labeltext

        if self.charloc != 0:
            self.charloc -= 1

    def help(self):

        self.hints_used += 1

        if self.hints <= 0:
            self.karulabel.text = self.karu.data.nohints
        else:
            self.karulabel.text = self.karu.data.starttext
            self.help_button.disabled = False

        labeltext = list(self.emptyspace)
        wordlength = len(self.emptyspace)

        # Turn all letterBtn variables into a list for efficiency
        letterBtn = [self.letterBtn1, self.letterBtn2, self.letterBtn3, self.letterBtn4, self.letterBtn5,
                     self.letterBtn6, self.letterBtn7, self.letterBtn8, self.letterBtn9, self.letterBtn10,
                     self.letterBtn11, self.letterBtn12]

        for x in range(wordlength):

            # Check if current character is '-', if yes, replace with letter on pressed button
            if labeltext[x] == '_':

                for i in range(1, 12):

                    if letterBtn[i].text == list(self.currentWord)[x].upper():
                        # Replace current '-' with button text
                        letterBtn[i].state = 'down'
                        self.help_button.disabled = True
                        continue

                    else:
                        continue

                if self.charloc != (len(labeltext) - 1):
                    self.hints -= 1
                    print(self.hints)
                if self.hints <= 0:
                    self.karulabel.text = self.karu.data.nohints
                    print(self.karulabel.text)
                    self.help_button.disabled = True

                break

            else:

                continue

        print('help')

    # Function to check if entry is correct
    def wordChecker(self):

        # Check if '-' exists in label, if yes, level is not finished. If '-' does not exist, check if answer is correct
        if '_' in self.answer.text:

            self.level_finish = False

        else:

            # if True, answer is correct and level is finished
            if self.answer.text.lower() == self.currentWord:

                self.level += 1

                if self.level <= 4:
                    self.index = self.indexlist[(self.level)]  # Index +1 to go to next word
                    self.answer.color = .021, .4, .006, 1
                    self.level_finish = True  # Level is finished
                    self.stop_game()  # Time is stopped to get score
                    self.next_button.disabled = False  # Button to proceed to next level is enabled
                    self.next_button.text = '>'
                    self.karulabel.text = (self.karu.data.correcttext + '\n+%s KaruCoins!' % round(self.coins))

                # if True, all words in pack are done
                elif self.level > 4:

                    self.karulabel.text = (self.karu.data.correcttext + '\n+%s KaruCoins!' % round(self.coins))
                    self.answer.color = .021, .4, .006, 1
                    self.stop_game()
                    ############################
                    ###################################
                    ##################

                    self.add_widget(self.start_btn)
                    self.add_widget(self.start_img)
                    self.add_widget(self.finish_label)
                    self.finish_label.color = 1, 1, 1, 1
                    self.game_finish = True
                    self.start_btn.text = ''



            # Answer incorrect, change 'answer' label back to emptyspace
            else:

                self.karulabel.text = self.karu.data.incorrecttext
                self.emptyspace = ('_' * len(self.currentWord))
                self.labeltext = self.emptyspace
                self.answer.text = self.emptyspace
                self.mistakes += 1

    # To increase the time / count
    def increment_time(self, interval):

        self.time_total += .1
        self.time += .1
        print(self.time)

    # def start(self):
    #
    #     if self.game_pause:
    #         print('PAUSE.........................................................')
    #     elif not self.game_pause:
    #         print(self.game_pause)
    #         Clock.unschedule(self.increment_time)
    #         Clock.schedule_interval(self.increment_time, .1)

    def stop_game(self):

        Clock.unschedule(self.increment_time)

        # If it took 30 seconds or longer to complete level, no points are awarded.
        if self.time >= 30:

            self.score += 5

        elif self.time <= 5 and self.hints_used == 0 and self.mistakes == 0:

            self.score += self.points
            self.flawless = True

        else:

            if (self.points - ((self.hints_used * 2) + (self.time * 2))) < 5:
                self.score += 5

            else:

                self.score += (self.points - ((self.hints_used * 2) + (
                        self.time * 2)))  # Formula to calculate awarded points:
                # total score + (50 points - ((hints*2) + (seconds * 2)))

        print("Score: %s \nTime: %d\n" % (round(self.score), round(self.time)))

        self.time = 0  # Turn level time back to 0
        self.pay_coins()
        self.high_score()

        self.go_to_menu = True

    def pause(self):

        """First time when pause is initiated, clock unschedules. When game is resumed and paused again, script returns
        game_pause = True, initialises if-statement(if self.game_pause: print(...), Clock.unsch.... but clock does not
        unschedule."""

        print("try to pause")

        if self.level_finish:
            print('Level finished, nothing to pause.')

        if not self.level_finish:
            if self.game_pause:
                print('PAUSEEEEE !!!!!!!!!!!')
                Clock.unschedule(self.increment_time)
                print('unscheduled')

            elif not self.game_pause:
                # Keeping time
                Clock.schedule_interval(self.increment_time, .1)

                try:
                    self.remove_widget(self.start_btn)
                    self.remove_widget(self.start_img)
                    self.remove_widget(self.back_to_menu)
                    self.remove_widget(self.finish_label)
                except:
                    print("No widgets to remove")

    def pay_coins(self):

        if self.flawless:
            self.coins += self.payout
            self.flawless = False
            print('flawless victory')
        elif not self.flawless:

            if (self.payout - ((self.mistakes + self.hints_used) + (self.time / 2))) <= 0:
                self.coins += 1
                print('0 of minder')
            else:
                self.coins += round((self.payout - ((self.mistakes + self.hints_used) + (self.time / 2))))
                print("%a - ((%s + %d) + (%f/2) = %g" % (
                    self.payout, self.mistakes, self.hints_used, self.time, self.coins))

        print("Earned %s coins" % self.coins)
        self.wallet += round(self.coins)
        store.put("wallet", coins=self.wallet)
        self.wallet = store.get("wallet")["coins"]
        self.wallet_label.text = (str(round(self.wallet)) + 'KC')
        print("Wallet: %s" % self.wallet)

    def high_score(self):
        highscore = self.highscore
        if self.score > highscore:
            store.put("data", highscore=self.score)
            highscore = store.get("data")["highscore"]
            self.highscore_label.text = str(round(highscore))

            print(highscore)

    def reload(self):

        self.time_total = 0  # Total playtime
        self.score = 0  # Total score
        self.level_finish = False  # Bool to check if current level is cleared

        self.game_finish = False
        self.game_pause = False
        self.go_to_menu = False

        # i = letterBtn pressed (i.e. i = 0 = letterBtn1)
        self.i = 0

        ### WORDS Function ###

        # import module packData, containing image's and corresponding words
        self.indexlist = [0, 1, 2, 3, 4]  # Index current word
        random.shuffle(self.indexlist)
        self.level = 0
        self.index = self.indexlist[self.level]

        # Word for current level
        self.currentWord = self.wordlist[self.index]

        # Image for current level
        self.currentImage = self.data.pack1img[self.index]

        # Used to assign letters to buttons
        self.letters_btn = self.currentWord

        # Used as text for label
        self.emptyspace = ('_' * len(self.currentWord))

        # character location used for backspace and help
        self.charloc = 0

        # Hints
        self.hints = 5  # Total amount of hints per game
        self.hints_used = 0  # Amount of hints used in level

        # Clear answer label
        self.answer.text = self.emptyspace
        self.answer.color = 1, 1, 1, 1

        self.letters_btn = self.currentWord

        self.imagewidget.source = self.currentImage

        self.remove_widget(self.finish_label)
        self.karulabel.text = karuData.starttext

        # Empty out all buttons
        letterBtn = [self.letterBtn1, self.letterBtn2, self.letterBtn3, self.letterBtn4, self.letterBtn5,
                     self.letterBtn6, self.letterBtn7, self.letterBtn8, self.letterBtn9, self.letterBtn10,
                     self.letterBtn11, self.letterBtn12]

        for x in range(0, 12):
            letterBtn[x].text = ''

        self.imagewidget.opacity = 0

        with self.canvas.before:
            Rectangle(source='', size=self.size, pos=self.pos)

    def start_or_menu(self):

        if not self.game_finish:
            with self.canvas.before:
                Rectangle(source=store.get('custom')['current_bg'], size=self.size, pos=self.pos)
            self.randomizeLetters()
            self.go_to_menu = False

        elif self.game_finish:
            self.reload()


class Menu(Screen, BoxLayout):
    pass


class KaruHouse(Screen, BoxLayout):
    bg = store.get('custom')['current_bg']

    data = packData
    current_bg = 0

    # def background_change(self):
    #     if self.current_bg == 1:
    #         store.put("custom", current_bg="resources/backgrounds/wallpaper.png")
    #
    #         print("click")

    # elif self.current_bg == 2:
    #     store.put("custom", current_bg="resources/backgrounds/wallpaper2.png")
    #     WindowManager.bg = "resources/backgrounds/wallpaper2.png"
    #     # with self.canvas.before:
    #     #     Rectangle(source=store.get('custom')['current_bg'], size=self.size, pos=self.pos)
    #
    #     print("click")

    def outfit_change(self):
        pass

    def checkout(self):
        pass


class PopupMenu(Popup):
    pause = AmbonWidget.game_pause
    aw = AmbonWidget()


class PopupBg(Popup):
    bg = store.get('custom')['current_bg']
    data = packData
    bg_unlocked = store.get('backgrounds')['unlocked']
    #bg_no_unlocked = store.get('backgrounds')['amount']
    bg_price = store.get('backgrounds')['price']

    current_bg = 1
    bg_index = 'bg' + str(current_bg)

    bg_btn1 = ObjectProperty(None)

    bg_btn2 = ObjectProperty(None)
    buy_btn2 = ObjectProperty(None)

    bg_btn3 = ObjectProperty(None)
    buy_btn3 = ObjectProperty(None)

    bg_btn = [None, bg_btn1, bg_btn2, bg_btn3]

    price = ObjectProperty(0)
    price_str = str(bg_price) + 'KC'


    wallet = store.get("wallet")["coins"]

    # while True:
    #     x = 1
    #     try:
    #         if bg_unlocked[x]:
    #
    #             if bg_unlocked[x] == 'bg2':
    #                 if not buy_btn2.disabled:
    #                     buy_btn2.disabled = True
    #                     bg_btn2.disabled = False
    #                     break
    #
    #             elif bg_unlocked[x] == 'bg3':
    #                 if not buy_btn3.disabled:
    #                     buy_btn3.disabled = True
    #                     bg_btn2.disabled = False
    #                     break
    #     except:
    #         break

    def checkout(self):

        if self.price <= self.wallet:

            print("Kaching!")
            self.wallet -= self.price
            store.put("wallet", coins=self.wallet)

            store['backgrounds']['unlocked'][self.bg_index] = True

            self.title = ('KaruCoins: ' + str(round(self.wallet)))

            #self.bg_btn[self.current_bg].text = ''


            self.background_change()
        else:
            print("Not enough coins")

    def background_change(self):

        self.bg_index = 'bg' + str(self.current_bg)

        if self.bg_unlocked[self.bg_index]:

            store.put("custom", current_bg=self.data.backgrounds[self.current_bg])

            print("click")

        elif not self.bg_unlocked[self.bg_index]:

            print("Not bought")
            self.checkout()

            if self.bg_unlocked[self.bg_index]:

                store.put("custom", current_bg=self.data.backgrounds[self.current_bg])
                print("Bought and active")

            else:

                print('passing...')
                pass
        # if self.current_bg == 1:
        #     store.put("custom", current_bg="resources/backgrounds/wallpaper.png")
        #
        #     print("click")
        #
        # elif self.current_bg == 2:
        #
        #     if self.bg_btn2_lock:
        #         print("Not bought")
        #         self.checkout()
        #         self.bg_btn2_lock = False
        #         store.put("custom", current_bg="resources/backgrounds/wallpaper2.png")
        #     else:
        #         store.put("custom", current_bg="resources/backgrounds/wallpaper2.png")
        #         WindowManager.bg = "resources/backgrounds/wallpaper2.png"




class PopupOutfit(Popup):
    data = packData
    wallet = store.get("wallet")["coins"]


class SettingsScreen(Screen, BoxLayout):
    pass


class WindowManager(ScreenManager):
    pass


class Interface(BoxLayout, Screen):
    AmbonWidget = AmbonWidget()


root_widget = Builder.load_file('ambon.kv')


class KaruApp(App):
    AmbonWidget = AmbonWidget()

    def build(self):
        return root_widget


KaruApp().run()
