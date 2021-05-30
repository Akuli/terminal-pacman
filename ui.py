from __future__ import annotations
import core
import curses


from walls import width, height, walls
pacman_width = 10
pacman_height = 5

# Account for walls of 1 character
x_spacing = pacman_width + 1
y_spacing = pacman_height + 1

_PICTURE_STRING = r"""
  .----.      .----.      .----.      .----.
 /   o  \    /   |  \    /  o   \    /      \
|    ----   | o      |   ----    |  |      o |
 \      /    \      /    \      /    \  |   /
  `----'      `----'      `----'      `----'

  .----.      .    .      .----.      .----.
 /   o .'    / \__/ \    `. o   \    /      \
|     ^     | o      |     ^     |  |   __ o |
 \    `-,    \      /    .-'    /    \ /  \ /
  `----'      `----'      `----'      `    '

  .----.                  .----.      .----.
 /   o/      /\    /\      \o   \    /      \
|    (      | o`--'  |      )    |  |  .--.o |
 \    \      \      /      /    /    \/    \/
  `----'      `----'      `----'

  .---                      ---.      .----.
 /   p                      q   \    /      \
|    |      ,-o------.      |    |  `------o-'
 \   |       \      /       |   /
  `---        `----'        ---'
"""


def load_player_pics():
    chunks = [
        [
            [
                line.ljust(pacman_width*4 + len("  ")*3)[offset:offset+pacman_width]
                for offset in (n*(pacman_width + 2) for n in (0, 1, 2, 3))
            ]
            for line in chunk.splitlines()
        ]
        for chunk in _PICTURE_STRING.strip("\n").split("\n\n")
    ]

    picture_lists = {
        "left": [],
        "right": [],
        "up": [],
        "down": [],
    }
    for chunk in chunks:
        for direction, *picture in zip(['right', 'up', 'left', 'down'], *chunk):
            picture_lists[direction].append(picture)

    # Repeat the same pictures in reverse to animate
    for picture_list in picture_lists.values():
        picture_list.extend(picture_list[1:-1][::-1])
    return picture_lists


def count_leading_spaces(string):
    return len(string) - len(string.lstrip(' '))


class UI:

    def __init__(self, stdscr):
        self.player_pics = load_player_pics()
        self.player = core.Player()
        self.stdscr = stdscr

    def draw_grid(self):
        for x in range(width):
            for y in range(height+1):
                if walls.has_wall_above((x, y % height)):
                    self.stdscr.addstr(y_spacing*y, x_spacing*x + 1, "-" * pacman_width)

        for x in range(width+1):
            for y in range(height):
                if walls.has_wall_to_left((x % width, y)):
                    for screen_y in range(y_spacing*y + 1, y_spacing*(y+1)):
                        self.stdscr.addstr(screen_y, x_spacing*x, "|")

    def draw_player(self):
        # Chosen so that 'player.x += width' does not affect what shows on screen
        first_x = round(self.player.x*x_spacing + 1) % (width*x_spacing)
        first_y = round(self.player.y*y_spacing + 1)

        for line_y, line in enumerate(self.player_pics[self.player.direction][0], start=first_y):
            # Handle wrapping around, line can show in two places
            line_y %= height*y_spacing
            y_list = [0, height*y_spacing] if line_y == 0 else [line_y]

            first_visible_x = first_x + count_leading_spaces(line)
            for char_x, char in enumerate(line.strip(' '), start=first_visible_x):
                char_x %= width*x_spacing
                x_list = [0, width*x_spacing] if char_x == 0 else [char_x]

                for x in x_list:
                    for y in y_list:
                        self.stdscr.addstr(y, x, char)

    def handle_key(self, key):
        if key == curses.KEY_RIGHT:
            self.player.direction = 'right'
            self.player.x += 2 / x_spacing
        if key == curses.KEY_LEFT:
            self.player.direction = 'left'
            self.player.x -= 2 / x_spacing
        if key == curses.KEY_UP:
            self.player.direction = 'up'
            self.player.y -= 1 / y_spacing
        if key == curses.KEY_DOWN:
            self.player.direction = 'down'
            self.player.y += 1 / y_spacing


def main(stdscr: curses._CursesWindow):
    curses.curs_set(0)
    ui = UI(stdscr)
    while True:
        stdscr.clear()
        ui.draw_grid()
        ui.draw_player()
        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('q'):
            break
        ui.handle_key(key)


if __name__ == '__main__':
    curses.wrapper(main)
