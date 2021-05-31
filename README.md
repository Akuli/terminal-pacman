# terminal-pacman
This PacMan game clone runs entirely on a terminal or command prompt.

![Screenshot](screenshot.png)


## Running the game

Windows:

```
git clone https://github.com/Akuli/terminal-pacman
cd terminal-pacman
py -m venv env
env\Scripts\activate
pip install -r requirements.txt
py -m pacman
```

Other operating systems:

```
git clone https://github.com/Akuli/terminal-pacman
cd terminal-pacman
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python3 -m pacman
```

## Developing

In `terminal-pacman` folder, cloned as above, with venv active:

```
pip install -r requirements-dev.txt
```

Run `./lint` to run all linters at once (doesn't work on Windows).
