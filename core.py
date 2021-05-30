from fractions import Fraction
from math import ceil, floor


class Player:
    def __init__(self, walls, x_move_amount: Fraction, y_move_amount: Fraction):
        self.walls = walls
        self.x = 0
        self.y = 0
        self.x_move_amount = x_move_amount
        self.y_move_amount = y_move_amount
        self.direction = "right"
        self.next_direction = None
        self.moving = False
        self.animation_counter = 0

    def _get_integer_point(self, x, y):
        if isinstance(x, Fraction):
            assert x.denominator == 1
            x = x.numerator
        if isinstance(y, Fraction):
            assert y.denominator == 1
            y = y.numerator

        return (x % self.walls.width, y % self.walls.height)

    def _get_move_info(self, direction):
        if direction == "right":
            boundary = ceil(self.x)
            boundary_point = self._get_integer_point(boundary, self.y)
            has_wall = self.walls.has_wall_to_right(boundary_point)
            crosses_boundary = self.x <= boundary < self.x + self.x_move_amount
            crossed_point = (self.x + self.x_move_amount, self.y)
        elif direction == "left":
            boundary = floor(self.x)
            boundary_point = self._get_integer_point(boundary, self.y)
            has_wall = self.walls.has_wall_to_left(boundary_point)
            crosses_boundary = self.x - self.x_move_amount < boundary <= self.x
            crossed_point = (self.x - self.x_move_amount, self.y)
        elif direction == "down":
            boundary = ceil(self.y)
            boundary_point = self._get_integer_point(self.x, boundary)
            has_wall = self.walls.has_wall_below(boundary_point)
            crosses_boundary = self.y <= boundary < self.y + self.y_move_amount
            crossed_point = (self.x, self.y + self.y_move_amount)
        elif direction == "up":
            boundary = floor(self.y)
            boundary_point = self._get_integer_point(self.x, boundary)
            has_wall = self.walls.has_wall_above(boundary_point)
            crosses_boundary = self.y - self.y_move_amount < boundary <= self.y
            crossed_point = (self.x, self.y - self.y_move_amount)
        else:
            raise ValueError(repr(direction))

        return (has_wall, crosses_boundary, boundary_point, crossed_point)

    def move(self):
        if self.moving:
            # Opposite direction is always possible
            if (self.direction, self.next_direction) in {
                ("left", "right"),
                ("right", "left"),
                ("up", "down"),
                ("down", "up"),
            }:
                self.direction = self.next_direction

            (
                has_wall,
                crosses_boundary,
                boundary_point,
                crossed_point,
            ) = self._get_move_info(self.direction)

            if crosses_boundary:
                # Switch direction if a wall isn't in the way
                self.x, self.y = map(Fraction, boundary_point)
                if (
                    self.next_direction is not None and 
                    self.direction != self.next_direction
                    and not self._get_move_info(self.next_direction)[0]
                ):
                    self.direction = self.next_direction
                    return

                if has_wall:
                    # stuck
                    self.moving = False
                    return

            self.x, self.y = crossed_point
