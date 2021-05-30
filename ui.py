from __future__ import annotations

import curses
from fractions import Fraction

import core
from walls import Walls

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
pacman_width = 10
pacman_height = 5

# Account for walls of 1 character
x_spacing = pacman_width + 1
y_spacing = pacman_height + 1


def load_player_pics():
    chunks = [
        [
            [
                line.ljust(pacman_width * 4 + len("  ") * 3)[
                    offset : offset + pacman_width
                ]
                for offset in (n * (pacman_width + 2) for n in (0, 1, 2, 3))
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
        for direction, *picture in zip(["right", "up", "left", "down"], *chunk):
            picture_lists[direction].append(picture)

    # Repeat the same pictures in reverse to animate
    for picture_list in picture_lists.values():
        picture_list.extend(picture_list[1:-1][::-1])
    return picture_lists


def count_leading_spaces(string):
    return len(string) - len(string.lstrip(" "))


class UI:
    def __init__(self, stdscr):
        self.walls = Walls(7, 3)
        self.walls.remove_walls_until_connected()

        self.player_pics = load_player_pics()
        self.player = core.Player(
            self.walls, Fraction(2, x_spacing), Fraction(1, y_spacing)
        )
        self.stdscr = stdscr

    def draw_grid(self):
        for x in range(self.walls.width):
            for y in range(self.walls.height + 1):
                if self.walls.has_wall_above((x, y % self.walls.height)):
                    self.stdscr.addstr(
                        y_spacing * y, x_spacing * x + 1, "-" * pacman_width
                    )

        for x in range(self.walls.width + 1):
            for y in range(self.walls.height):
                if self.walls.has_wall_to_left((x % self.walls.width, y)):
                    for screen_y in range(y_spacing * y + 1, y_spacing * (y + 1)):
                        self.stdscr.addstr(screen_y, x_spacing * x, "|")

    def draw_player(self):
        # Chosen so that 'player.x += width' does not affect what shows on screen
        first_x = round(self.player.x * x_spacing + 1) % (self.walls.width * x_spacing)
        first_y = round(self.player.y * y_spacing + 1)

        picture_list = self.player_pics[self.player.direction]
        picture = picture_list[self.player.animation_counter % len(picture_list)]
        self.player.animation_counter += 1

        for line_y, line in enumerate(picture, start=first_y):
            # Handle wrapping around, line can show in two places
            line_y %= self.walls.height * y_spacing
            y_list = [0, self.walls.height * y_spacing] if line_y == 0 else [line_y]

            first_visible_x = first_x + count_leading_spaces(line)
            for char_x, char in enumerate(line.strip(" "), start=first_visible_x):
                char_x %= self.walls.width * x_spacing
                x_list = [0, self.walls.width * x_spacing] if char_x == 0 else [char_x]

                for x in x_list:
                    for y in y_list:
                        self.stdscr.addstr(y, x, char)

    def handle_key(self, key):
        if key == curses.KEY_RIGHT:
            self.player.next_direction = "right"
        if key == curses.KEY_LEFT:
            self.player.next_direction = "left"
        if key == curses.KEY_UP:
            self.player.next_direction = "up"
        if key == curses.KEY_DOWN:
            self.player.next_direction = "down"

        self.player.move()


def main(stdscr: curses._CursesWindow):
    curses.curs_set(0)
    ui = UI(stdscr)
    while True:
        stdscr.clear()
        ui.draw_grid()
        ui.draw_player()
        stdscr.refresh()

        key = stdscr.getch()
        if key == ord("q"):
            break
        ui.handle_key(key)


if __name__ == "__main__":
    curses.wrapper(main)
