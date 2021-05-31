from __future__ import annotations

import random
from fractions import Fraction
from math import ceil, floor
from typing import Tuple

from .walls import Walls


def _opposite(direction: str) -> str:
    if direction == "left":
        return "right"
    if direction == "right":
        return "left"
    if direction == "up":
        return "down"
    if direction == "down":
        return "up"
    raise ValueError(direction)


class GameObject:
    def __init__(self, walls: Walls, x_move_amount: Fraction, y_move_amount: Fraction):
        self.walls = walls
        self.x = Fraction(0)
        self.y = Fraction(0)
        self.x_move_amount = x_move_amount
        self.y_move_amount = y_move_amount
        self.direction = "right"
        self.animation_counter = 0

    def _get_integer_point(
        self, x: Fraction | int, y: Fraction | int
    ) -> Tuple[int, int]:
        if isinstance(x, Fraction):
            assert x.denominator == 1
            x = x.numerator
        if isinstance(y, Fraction):
            assert y.denominator == 1
            y = y.numerator

        return (x % self.walls.width, y % self.walls.height)

    def _get_move_info(
        self, direction: str
    ) -> Tuple[bool, bool, Tuple[int, int], Tuple[Fraction, Fraction]]:
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


class Player(GameObject):
    def __init__(self, walls: Walls, x_move_amount: Fraction, y_move_amount: Fraction):
        super().__init__(walls, x_move_amount, y_move_amount)
        self.next_direction: str | None = None
        self.moving = False

    def move(self) -> None:
        if self.moving:
            # Opposite direction is always possible
            if self.next_direction == _opposite(self.direction):
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
                    self.next_direction is not None
                    and self.direction != self.next_direction
                    and not self._get_move_info(self.next_direction)[0]
                ):
                    self.direction = self.next_direction
                    return

                if has_wall:
                    # stuck
                    self.moving = False
                    return

            self.x, self.y = crossed_point


class Enemy(GameObject):
    def __init__(self, walls: Walls, x_move_amount: Fraction, y_move_amount: Fraction):
        super().__init__(walls, x_move_amount, y_move_amount)
        self.x = Fraction(walls.width // 2)
        self.y = Fraction(walls.height // 2)
        self._just_turned = False

    def move(self) -> None:
        (
            has_wall,
            crosses_boundary,
            boundary_point,
            crossed_point,
        ) = self._get_move_info(self.direction)

        if crosses_boundary and not self._just_turned:
            self.x, self.y = map(Fraction, boundary_point)
            next_direction = random.choice(
                [
                    direction
                    for direction in ["left", "right", "up", "down"]
                    if not self._get_move_info(direction)[0]  # not hit wall
                ]
            )
            if self.direction == next_direction:
                self.x, self.y = crossed_point
                self._just_turned = False
            else:
                self.direction = next_direction
                self._just_turned = True
        else:
            self.x, self.y = crossed_point
            self._just_turned = False


def _manhattan_distance(
    x1: Fraction, y1: Fraction, x2: Fraction, y2: Fraction
) -> Fraction:
    return abs(x1 - x2) + abs(y1 - y2)


def collision_check(player: Player, enemy: Enemy) -> bool:
    return _manhattan_distance(player.x, player.y, enemy.x, enemy.y) < 0.95
