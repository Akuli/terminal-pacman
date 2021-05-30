from math import floor, ceil
from fractions import Fraction
from walls import width, height


def get_integer_point(x, y):
    if isinstance(x, Fraction):
        assert x.denominator == 1
        x = x.numerator
    if isinstance(y, Fraction):
        assert y.denominator == 1
        y = y.numerator

    return (x % width, y % height)


class Player:

    def __init__(self, walls, x_move_amount: Fraction, y_move_amount: Fraction):
        self.walls = walls
        self.x = 0
        self.y = 0
        self.x_move_amount = x_move_amount
        self.y_move_amount = y_move_amount
        self.direction = "right"
        self.next_direction = None
        self.moving = True

    def _get_move_info(self, direction):
        if direction == 'right':
            boundary = ceil(self.x)
            boundary_point = get_integer_point(boundary, self.y)
            crosses_boundary = self.x <= boundary < self.x + self.x_move_amount
            crossed_point = (self.x + self.x_move_amount, self.y)
            has_wall = self.walls.has_wall_to_right(boundary_point)
        elif direction == 'left':
            boundary = floor(self.x)
            boundary_point = get_integer_point(boundary, self.y)
            crosses_boundary = self.x - self.x_move_amount < boundary <= self.x
            crossed_point = (self.x - self.x_move_amount, self.y)
            has_wall = self.walls.has_wall_to_left(boundary_point)
        elif direction == 'down':
            boundary = ceil(self.y)
            boundary_point = get_integer_point(self.x, boundary)
            crosses_boundary = self.y <= boundary < self.y + self.y_move_amount
            crossed_point = (self.x, self.y + self.y_move_amount)
            has_wall = self.walls.has_wall_below(boundary_point)
        elif direction == 'up':
            boundary = floor(self.y)
            boundary_point = get_integer_point(self.x, boundary)
            crosses_boundary = self.y - self.y_move_amount < boundary <= self.y
            crossed_point = (self.x, self.y - self.y_move_amount)
            has_wall = self.walls.has_wall_above(boundary_point)
        else:
            raise ValueError(self.direction)

        return (crosses_boundary, has_wall, boundary_point, crossed_point)

    def move(self):
        if self.moving:
            # Opposite direction is always possible
            if (self.direction, self.next_direction) in {
                ('left', 'right'),
                ('right', 'left'),
                ('up', 'down'),
                ('down', 'up'),
            }:
                self.direction = self.next_direction

            crosses_boundary, has_wall, boundary_point, crossed_point = self._get_move_info(self.direction)

            import q
            q/("Crosses boundary?",crosses_boundary)

            if crosses_boundary:
                # Switch direction if a wall isn't in the way
                self.x, self.y = map(Fraction, boundary_point)
                if self.direction != self.next_direction and not self._get_move_info(self.next_direction)[1]:
                    q/"Wall not in the way for switching direction"
                    self.direction = self.next_direction
                    return

                # Keep going in this direction if a wall isn't in the way
                if has_wall:
                    return

            self.x, self.y = crossed_point
