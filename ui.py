from __future__ import annotations

import curses


from walls import width, height, walls
pacman_width = 10
pacman_height = 5


def draw_grid(stdscr):
    x_spacing = pacman_width + 1
    y_spacing = pacman_height + 1

    for x in range(width):
        for y in range(height+1):
            if walls.has_wall_above((x, y % height)):
                stdscr.addstr(y_spacing*y, x_spacing*x + 1, "-" * pacman_width)

    for x in range(width+1):
        for y in range(height):
            if walls.has_wall_to_left((x % width, y)):
                for screen_y in range(y_spacing*y + 1, y_spacing*(y+1)):
                    stdscr.addstr(screen_y, x_spacing*x, "|")


def main(stdscr: curses._CursesWindow):
    curses.curs_set(0)
    draw_grid(stdscr)
    stdscr.refresh()
    stdscr.getch()


if __name__ == '__main__':
    curses.wrapper(main)
