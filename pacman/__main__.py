from __future__ import annotations

import curses
import sys
import time
from fractions import Fraction
from typing import Sequence, Tuple

from . import core
from .walls import Walls

image_width = 6
image_height = 4

_PLAYER_ASCII_ART = r"""
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

_ENEMY_STRING = r"""
  __
 /oo\
 |--|
/    \
"""
_ENEMY_PIC = [
    line.ljust(image_width) for line in _ENEMY_STRING.strip("\n").splitlines()
]

# Account for walls of 1 character
x_spacing = image_width + 1
y_spacing = image_height + 1

PLAYER = 1
WALL = 2
ENEMY = 3


def get_player_pics(direction: str) -> list[Tuple[str, ...]]:
    chunks = [
        [line.rstrip(":").split(":") for line in chunk.splitlines()]
        for chunk in _PLAYER_ASCII_ART.strip("\n").split("\n\n")
    ]

    result = []
    for chunk in chunks:
        index = ["right", "up", "left", "down"].index(direction)
        picture = list(zip(*chunk))[index]
        result.append(picture)

    # Repeat the same pictures in reverse to animate
    result.extend(result[1:-1][::-1])
    return result


def count_leading_spaces(string: str) -> int:
    return len(string) - len(string.lstrip(" "))


class UI:
    def __init__(self, stdscr: curses._CursesWindow):
        screen_height, screen_width = stdscr.getmaxyx()
        self.walls = Walls(
            (screen_width - 1) // x_spacing, (screen_height - 1) // y_spacing
        )

        self.player = core.Player(
            self.walls, Fraction(2, x_spacing), Fraction(1, y_spacing)
        )
        self.enemy = core.Enemy(
            self.walls, Fraction(2, x_spacing), Fraction(1, y_spacing)
        )
        self.stdscr = stdscr

    def draw_grid(self) -> None:
        attrs = curses.color_pair(WALL)

        for x in range(self.walls.width):
            for y in range(self.walls.height + 1):
                if self.walls.has_wall_above((x, y % self.walls.height)):
                    self.stdscr.addstr(
                        y_spacing * y, x_spacing * x + 1, "-" * image_width, attrs
                    )

        for x in range(self.walls.width + 1):
            for y in range(self.walls.height):
                if self.walls.has_wall_to_left((x % self.walls.width, y)):
                    for screen_y in range(y_spacing * y + 1, y_spacing * (y + 1)):
                        self.stdscr.addstr(screen_y, x_spacing * x, "|", attrs)

    def _draw_game_object(
        self,
        obj: core.GameObject,
        picture_list: Sequence[Sequence[str]],
        color_pair_num: int,
    ) -> None:
        # Chosen so that 'player.x += width' does not affect what shows on screen
        first_x = round(obj.x * x_spacing + 1) % (self.walls.width * x_spacing)
        first_y = round(obj.y * y_spacing + 1)

        picture = picture_list[obj.animation_counter % len(picture_list)]
        if self.player.moving or obj.animation_counter % len(picture_list) != 0:
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
                        self.stdscr.addstr(
                            y, x, char, curses.color_pair(color_pair_num)
                        )

    def draw_game_objects(self) -> None:
        self._draw_game_object(
            self.player, get_player_pics(self.player.direction), PLAYER
        )
        self._draw_game_object(self.enemy, [_ENEMY_PIC], ENEMY)

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
    curses.init_pair(ENEMY, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.curs_set(0)
    stdscr.timeout(1)  # 0 is special
    ui = UI(stdscr)
    next_timeout = time.time()

    while True:
        ui.player.move()
        ui.enemy.move()
        stdscr.clear()
        ui.draw_grid()
        ui.draw_game_objects()
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

        if core.collision_check(ui.player, ui.enemy):
            sys.exit("You died :(")


if __name__ == "__main__":
    curses.wrapper(main)
