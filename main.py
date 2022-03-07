# Using kivy 2.0.0 and python3.8

import kivy

from kivy.config import Config  # For setting height (19.5:9)
from kivy.factory import Factory
from kivy.graphics import Rectangle, RoundedRectangle, Color, InstructionGroup
from kivy.uix.gridlayout import GridLayout

from kivy.app import App
from kivy.lang import Builder

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup

from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock  # For retrieving playtime and getting score
from kivy.storage.jsonstore import JsonStore

import random
import time
import packData
import karuData

kivy.require('2.0.0')  # Version of Kivy
Config.set('graphics', 'width', '360')  # (New Android smartphones e.g. OnePlus 7 series)
Config.set('graphics', 'height', '640')  # (iPhone X, 11 and 12 series, upsampled)
store = JsonStore('resources/user_data.json')  # For saving high score
root_widget = Builder.load_file('layout.kv')

# os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'  # If necessary, uncomment to prevent OpenGL error

# Mascot
class KaruWidget(Widget):
    data = karuData
    speech = data.starttext
    pass


class GameWidget(Screen, FloatLayout):
    karu = KaruWidget()
    karulabel = ObjectProperty(None)

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
    wordlist = data.pack1  # Current list of words
    indexlist = list(wordlist.keys())  # Index current word
    print(indexlist)
    random.shuffle(indexlist)
    print(indexlist)
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

    def __init__(self, **kwargs):

        super(GameWidget, self).__init__(**kwargs)

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

            self.time = 0
            self.coins = 0
            self.mistakes = 0

            self.currentWord = self.wordlist[self.index]  # New word
            self.currentImage = self.data.pack1img[self.index]  # Corresponding image
            self.emptyspace = ('_' * len(self.currentWord))  # Set empty space ('-') to len(currentWord)

            # Clear answer label

            self.letters_btn = self.currentWord



            self.imagewidget.source = self.currentImage
            print(self.currentWord)  # Test if currentWord is updated
            print(self.currentImage)  # Test if currentImage is updated
            print(self.emptyspace)  # Test if empty space is updated

            self.randomizeLetters()  # Randomize letters for buttons

    # Function for randomizing letters for buttons
    def randomizeLetters(self):


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

            self.remove_widget(self.grid)
            self.grid = GridLayout(rows=1, cols=len(self.currentWord), spacing=10, size_hint_x=.55, size_hint_y=.075,
                                   pos_hint={'center_x': .5, 'center_y': .45})
            self.add_widget(self.grid)
            self.grid.clear_widgets(children=None)
            print('grid cleared')

        self.start_time()

        self.remove_widget(self.next_button)
        self.imagewidget.opacity = 1

        all_letters = list("abcdefghijklmnopqrstuvwxyz")  # Possible letters for randomizing
        letters_needed = 12 - len(
            self.currentWord)  # 12 letters are needed in total, X letters already exist in current Word
        # Turn all letterBtn variables into a list for efficiency
        letterBtn = [self.letterBtn1, self.letterBtn2, self.letterBtn3, self.letterBtn4, self.letterBtn5,
                     self.letterBtn6, self.letterBtn7, self.letterBtn8, self.letterBtn9, self.letterBtn10,
                     self.letterBtn11, self.letterBtn12]

        # turn button opacity to 1
        for x in range(12):
            letterBtn[x].opacity = 1
        # Add possible characters to list including currentWord
        for x in range(letters_needed):

            while True:
                # letters_btn length may not exceed 12
                if len(self.letters_btn) != 12:

                    add_letter = random.choice(all_letters)  # Choose random letter from all_letters

                    if add_letter not in self.letters_btn:
                        self.letters_btn += add_letter  # Append chosen letter to letters_btn
                        break

                    else:
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

        for x in range(len(self.currentWord)):
            word_button = Factory.WordButton()
            self.grid.add_widget(word_button)
            word_button.charpos = x
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
                     self.letterBtn11, self.letterBtn12]

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

                # Replace current '-' with button text
                self.wordbuttons[x].text = letterBtn[self.i].text
                self.wordbuttons[x].state = 'normal'

                break

            else:

                continue

    def backspace(self):

        old_charloc = self.charloc + 1

        print(self.wordbuttons[self.charloc].text)
        if self.wordbuttons[self.charpos] != '_':

            try:
                self.wordbuttons[(old_charloc + 1)].state = 'normal'
            except IndexError:
                print(IndexError)
            self.charloc = old_charloc

            print(self.charloc)

        # labeltext = list(self.emptyspace)
        # labeltext[self.charloc] = '_'
        #
        # # Turn list in string so it can be used in 'answer' label
        # labeltext = ''.join(map(str, labeltext))
        #
        # # Update label and emptyspace
        # self.emptyspace = labeltext
        #
        # if self.charloc != 0:
        #     self.charloc -= 1

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

        self.answer_to_check = []

        for x in range(len(self.wordbuttons)):
            self.answer_to_check.append(self.wordbuttons[x].text)

        self.answer_to_check = ''.join([str(elem) for elem in self.answer_to_check])
        print(self.answer_to_check)

        # Check if '-' exists in label, if yes, level is not finished. If '-' does not exist, check if answer is correct
        if '_' in self.answer_to_check:

            self.level_finish = False

        else:

            # if True, answer is correct and level is finished
            if self.answer_to_check.lower() == self.currentWord:

                self.level += 1

                if self.level < len(self.indexlist):
                    self.index = self.indexlist[self.level]  # Index +1 to go to next word
                    # self.answer.color = .021, .4, .006, 1
                    self.level_finish = True  # Level is finished
                    self.stop_game()  # Time is stopped to get score
                    self.add_widget(self.next_button)

                    self.next_button.opacity = 1
                    self.karulabel.text = (self.karu.data.correcttext + '\n+%s KaruCoins!' % round(self.coins))

                    # remove buttons for cleaner look

                    # Turn all letterBtn variables into a list for efficiency
                    letterBtn = [self.letterBtn1, self.letterBtn2, self.letterBtn3, self.letterBtn4, self.letterBtn5,
                                 self.letterBtn6, self.letterBtn7, self.letterBtn8, self.letterBtn9, self.letterBtn10,
                                 self.letterBtn11, self.letterBtn12]

                    for x in range(12):
                        try:
                            letterBtn[x].opacity = 0
                        except Exception as e:
                            print(e)

                # if True, all words in pack are done
                elif self.level >= len(self.indexlist):
                    self.game_finish = True
                    self.stop_game()
                    self.karulabel.text = (self.karu.data.correcttext + '\n+%s KaruCoins!' % round(self.coins))
                    # self.answer.color = .021, .4, .006, 1

            # Answer incorrect, change 'answer' label back to emptyspace
            else:

                self.karulabel.text = self.karu.data.incorrecttext
                time.sleep(.5)
                self.emptyspace = ('_' * len(self.currentWord))

                for x in range(len(self.wordbuttons)):
                    self.wordbuttons[x].text = '_'

                self.mistakes += 1



    # To increase the time / count
    def increment_time(self, interval):

        self.time += .1

    def stop_game(self):

        self.stop_time()

        # If it took 30 seconds or longer to complete level, 5 points are rewarded (instead of 0 points, since the
        # answer was eventually correct)
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

            self.remove_widget(self.start_btn)
            self.add_widget(self.start_btn)

            self.start_btn.text = 'Goed gedaan!'

        elif self.early_stop:
            print('Heading back to menu')
            Clock.unschedule(self.increment_time)
            self.reload()

        else:
            Clock.unschedule(self.increment_time)

    def pause_time(self):

        print("try to pause")

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
        self.coins_total += self.coins
        if self.game_finish:
            self.wallet += round(self.coins_total)
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

        # WORDS Function #

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
            self.karulabel.text = karuData.starttext
        except AttributeError:
            print(AttributeError)

        try:
            self.add_widget(self.start_btn)
        except:
            print(Exception, '\n no startbtn added')

        try:
            self.start_btn.text = 'Raak het scherm aan\n   om te beginnen!'
        except:
            print(Exception, '\n no startbtn text added')

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
            Rectangle(source=store.get('custom')['current_bg'], size=self.size, pos=self.pos)

    def start_or_menu(self):

        if not self.game_finish:

            with self.canvas.before:
                Rectangle(source=store.get('custom')['current_bg'], size=self.size, pos=self.pos)

            self.randomizeLetters()
            self.go_to_menu = False

            self.remove_widget(self.start_btn)

        elif self.game_finish:
            print('happening fam')
            self.stop_time()


class Menu(Screen, BoxLayout):
    wallet = store.get("wallet")["coins"]
    highscore = NumericProperty(store.get('data')['highscore'])


class PopupBg(Popup):
    bg = store.get('custom')['current_bg']
    packData = packData
    bg_unlocked = store.get('backgrounds')['unlocked']
    bg_price = store.get('backgrounds')['price']

    selected = 0  # View currently selected background
    selection_rects = []

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
    print(wallet)

    # Function to ensure buttons are disabled/enabled where need to
    def update(self, dt):

        if store['backgrounds']['unlocked']['bg2']:
            self.buy_btn2.disabled = True
            self.bg_btn2.disabled = False
            self.buy_btn2.text = 'Gekocht'
            print('bg2')

        if store['backgrounds']['unlocked']['bg3']:
            self.buy_btn3.disabled = True
            self.bg_btn2.disabled = False
            self.buy_btn3.text = 'Gekocht'
            print('bg3')

        if store.get('custom')['current_bg'] == 'resources/backgrounds/wallpaper.png':

            if self.selected == 0:

                self.selected = 1

                if len(self.selection_rects) != 0:
                    item = self.selection_rects.pop(-1)
                    try:
                        self.bg_btn1.canvas.before.remove(item)
                    except ValueError:
                        print('nothing to remove')
                    try:
                        self.bg_btn2.canvas.before.remove(item)
                    except ValueError:
                        print('nothing to remove')
                    try:
                        self.bg_btn3.canvas.before.remove(item)
                    except ValueError:
                        print('nothing to remove')

                self.obj = InstructionGroup()
                self.obj.add(Color(0, .7, .7, .7))
                self.obj.add(RoundedRectangle(size=self.bg_btn1.size, pos=self.bg_btn1.pos))
                self.selection_rects.append(self.obj)
                self.bg_btn1.canvas.before.add(self.obj)

        if store.get('custom')['current_bg'] == 'resources/backgrounds/wallpaper2.png':

            if self.selected == 0:

                self.selected = 1

                if len(self.selection_rects) != 0:
                    item = self.selection_rects.pop(-1)
                    try:
                        self.bg_btn1.canvas.before.remove(item)
                    except ValueError:
                        print('nothing to remove')
                    try:
                        self.bg_btn2.canvas.before.remove(item)
                        self.bg_btn2.text = ''
                    except ValueError:
                        print('nothing to remove')
                    try:
                        self.bg_btn3.canvas.before.remove(item)
                    except ValueError:
                        print('nothing to remove')

                self.obj = InstructionGroup()
                self.obj.add(Color(0, .7, .7, .7))
                self.obj.add(RoundedRectangle(size=self.bg_btn2.size, pos=self.bg_btn2.pos))
                self.selection_rects.append(self.obj)
                self.bg_btn2.canvas.before.add(self.obj)

        if store.get('custom')['current_bg'] == 'resources/backgrounds/wallpaper3.png':

            if self.selected == 0:

                self.selected = 1

                if len(self.selection_rects) != 0:
                    item = self.selection_rects.pop(-1)
                    try:
                        self.bg_btn1.canvas.before.remove(item)
                    except ValueError:
                        print('nothing to remove')
                    try:
                        self.bg_btn2.canvas.before.remove(item)
                    except ValueError:
                        print('nothing to remove')
                    try:
                        self.bg_btn3.canvas.before.remove(item)
                    except ValueError:
                        print('nothing to remove')

                self.obj = InstructionGroup()
                self.obj.add(Color(0, .7, .7, .7))
                self.obj.add(RoundedRectangle(size=self.bg_btn3.size, pos=self.bg_btn3.pos))
                self.selection_rects.append(self.obj)
                self.bg_btn3.canvas.before.add(self.obj)

    def checkout(self):

        if self.price <= self.wallet:

            print("Kaching!")
            self.wallet = self.wallet - self.bg_price
            print('current wallet: ', self.wallet)
            store.put("wallet", coins=self.wallet)

            store['backgrounds']['unlocked'][self.bg_index] = True

            self.title = ('KaruCoins: ' + str(round(self.wallet)))

            # self.bg_btn[self.current_bg].text = ''

            # self.background_change()
        else:
            print("Not enough coins")

    def background_change(self):

        self.bg_index = 'bg' + str(self.current_bg)

        if self.bg_unlocked[self.bg_index]:

            store.put("custom", current_bg=self.packData.backgrounds[self.current_bg])

            print("click")
            Clock.schedule_once(self.update, -1)

        elif not self.bg_unlocked[self.bg_index]:

            print("Not bought")
            self.checkout()

            # if self.bg_unlocked[self.bg_index]:
            #
            #     store.put("custom", current_bg=self.data.backgrounds[self.current_bg])
            #     print("Bought and active")
            #     Clock.schedule_once(self.update, -1)
            # else:
            #
            #     print('passing...')
            #     pass
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

class KaruHouse(Screen, BoxLayout):
    pass


class PopupMenu(Popup):
    pass


class PopupOutfit(Popup):
    # data = packData
    # wallet = store.get("wallet")["coins"]
    pass


class SettingsScreen(Screen, BoxLayout):
    pass


class WindowManager(ScreenManager):
    pass


class KaruApp(App):
    WindowManager = WindowManager()


    def build(self):
        self.icon = 'resources/icons/karuicon.png'
        return self.WindowManager


KaruApp().run()
