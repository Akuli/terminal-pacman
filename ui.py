from __future__ import annotations

import curses
import time
from fractions import Fraction

import core
from walls import Walls

_PICTURE_STRING = r"""
 .--. : .--. : .--. : .--. :
/  o \:/o | \:/ o  \:/    \:
\  --/:\    /:\--  /:\ | o/:
 '--' : '--' : '--' : '--' :

 .--. : .  . : .--. : .--. :
/  o' :/o`' \: `o  \:/    \:
\  '-,:\    /:.-'  /:\ ,.o/:
 '--' : '--' : '--' : '  ' :

 .--. :      : .--. : .--. :
/  o/ :/o\,/\: \o  \:/    \:
\  \  :\    /:  /  /:\/^\o/:
 '--' : '--' : '--' :      :

 .-.  :      :  ,-. : .--. :
/  p  :-o----:  q  \:/    \:
\  |  :\    /:  |  /:----o-:
 '-'  : '--' :  `-' :      :
"""

player_width = 6
player_height = 4

# Account for walls of 1 character
x_spacing = player_width + 1
y_spacing = player_height + 1

PLAYER = 1
WALL = 2


def load_player_pics() -> dict[str, list[list[str]]]:
    chunks = [
        [line.rstrip(":").split(":") for line in chunk.splitlines()]
        for chunk in _PICTURE_STRING.strip("\n").split("\n\n")
    ]

    picture_lists: dict[str, list[list[str]]] = {
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


def count_leading_spaces(string: str) -> int:
    return len(string) - len(string.lstrip(" "))


class UI:
    def __init__(self, stdscr: curses._CursesWindow):
        screen_height, screen_width = stdscr.getmaxyx()
        self.walls = Walls(
            (screen_width - 1) // x_spacing, (screen_height - 1) // y_spacing
        )

        self.player_pics = load_player_pics()
        self.player = core.Player(
            self.walls, Fraction(2, x_spacing), Fraction(1, y_spacing)
        )
        self.stdscr = stdscr

    def draw_grid(self) -> None:
        attrs = curses.color_pair(WALL)

        for x in range(self.walls.width):
            for y in range(self.walls.height + 1):
                if self.walls.has_wall_above((x, y % self.walls.height)):
                    self.stdscr.addstr(
                        y_spacing * y, x_spacing * x + 1, "-" * player_width, attrs
                    )

        for x in range(self.walls.width + 1):
            for y in range(self.walls.height):
                if self.walls.has_wall_to_left((x % self.walls.width, y)):
                    for screen_y in range(y_spacing * y + 1, y_spacing * (y + 1)):
                        self.stdscr.addstr(screen_y, x_spacing * x, "|", attrs)

    def draw_player(self) -> None:
        # Chosen so that 'player.x += width' does not affect what shows on screen
        first_x = round(self.player.x * x_spacing + 1) % (self.walls.width * x_spacing)
        first_y = round(self.player.y * y_spacing + 1)

        picture_list = self.player_pics[self.player.direction]
        picture = picture_list[self.player.animation_counter % len(picture_list)]
        if self.player.moving or self.player.animation_counter % len(picture_list) != 0:
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
                        self.stdscr.addstr(y, x, char, curses.color_pair(1))

    def handle_key(self, key: int | str) -> None:
        if key == curses.KEY_RIGHT:
            self.player.next_direction = "right"
            self.player.moving = True
        if key == curses.KEY_LEFT:
            self.player.next_direction = "left"
            self.player.moving = True
        if key == curses.KEY_UP:
            self.player.next_direction = "up"
            self.player.moving = True
        if key == curses.KEY_DOWN:
            self.player.next_direction = "down"
            self.player.moving = True


def main(stdscr: curses._CursesWindow) -> None:
    curses.init_pair(PLAYER, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(WALL, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.curs_set(0)
    stdscr.timeout(1)  # 0 is special
    ui = UI(stdscr)
    next_timeout = time.time()

    while True:
        ui.player.move()
        stdscr.clear()
        ui.draw_grid()
        ui.draw_player()
        stdscr.refresh()

        while True:
            key = stdscr.getch()
            if key == ord("q"):
                return
            ui.handle_key(key)

            if key == curses.ERR:  # timed out
                next_timeout += 0.080

            remaining_ms = round((next_timeout - time.time()) * 1000)
            stdscr.timeout(max(1, remaining_ms))

            if key == curses.ERR:  # timed out
                break


if __name__ == "__main__":
    curses.wrapper(main)
