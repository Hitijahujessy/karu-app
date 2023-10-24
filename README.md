<h1 align="center">Karu</h1>
<p align="center">
  <img src="resources/karulogo.png" width="200" height="200">
</p>

<p align="center">
  Karu is an app that tries to help people with learning vocabulary of another language, in a gamified way. 
  The app is currently more aimed for children, but there are plans to make Karu enjoyable for all ages. 
</p>

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- 12 languages: Ambonese, Chinese, Dutch, English, French, German, Indonesian, Italian, Japanese, Korean, Russian and Spanish
- Two word list categories: Animals, Home
- Choose to translate from your first language to another language, or vice versa
- Listen to how a word is pronounced
- Improve your highscore by improving your vocabulary
- Earn coins for each correct answer and use them to unlock new outfits for Karu, new themes, and new categories

## Installation

Karu uses Python 3.11.5, Kivy, and Pandas.

### Install Kivy

* These installation instsructions are copied from the  [Kivy docs](https://kivy.org/doc/stable/gettingstarted/installation.html). If anything goes wrong or is
* not clear, please refer to the [Kivy docs](https://kivy.org/doc/stable/gettingstarted/installation.html).

#### Create virtual environment

1. Create the virtual environment named kivy_venv in your current directory:
```
python -m virtualenv kivy_venv
```

2. Activate the virtual environment. You will have to do this step from the current directory every time you start a new terminal. This sets up the environment so the new kivy_venv Python is used.

For Windows default CMD, in the command line do:
```
kivy_venv\Scripts\activate
```

If you are in a bash terminal on Windows, instead do:
```
source kivy_venv/Scripts/activate
```
If you are in linux or macOS, instead do:
```
source kivy_venv/bin/activate
```
Your terminal should now preface the path with something like (kivy_venv), indicating that the kivy_venv environment is active. If it doesn’t say that, the virtual environment is not active and the following won’t work.

#### Using PIP

```
python -m pip install "kivy[base]"
```

### Installing Pandas

```
pip install pandas
```
or
```
python -m pip install pandas
```
