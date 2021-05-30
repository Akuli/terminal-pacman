from math import floor, ceil
from fractions import Fraction
from walls import width, height


def get_point(x, y):
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

    def _get_move_info(self):
        if self.direction == 'right':
            boundary = ceil(self.x)
            hits_wall = self.x <= boundary < self.x + self.x_move_amount and self.walls.has_wall_to_right(get_point(boundary, self.y))
            import q; q/("Hits wall:", hits_wall)
            new_place = ((boundary if hits_wall else self.x + self.x_move_amount), self.y)
        elif self.direction == 'left':
            boundary = floor(self.x)
            hits_wall = self.x - self.x_move_amount < boundary <= self.x and self.walls.has_wall_to_left(get_point(boundary, self.y))
            new_place = ((boundary if hits_wall else self.x - self.x_move_amount), self.y)
        elif self.direction == 'down':
            boundary = ceil(self.y)
            hits_wall = self.y <= boundary < self.y + self.y_move_amount and self.walls.has_wall_below(get_point(self.x, boundary))
            new_place = (self.x, (boundary if hits_wall else self.y + self.y_move_amount))
        elif self.direction == 'up':
            boundary = floor(self.y)
            hits_wall = self.y - self.y_move_amount < boundary <= self.y and self.walls.has_wall_above(get_point(self.x, boundary))
            new_place = (self.x, (boundary if hits_wall else self.y - self.y_move_amount))
        else:
            raise ValueError(self.direction)

        return (hits_wall, new_place)

    def move(self):
        if self.moving:
            hits_wall, new_place = self._get_move_info()
            self.x, self.y = new_place
            if hits_wall:
                self.direction = self.next_direction
