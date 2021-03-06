from __future__ import annotations

import random
from typing import Tuple


class Walls:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self._all_walls = set(
            random.sample(
                {
                    (direction, (x, y))
                    for direction in {"right", "down"}
                    for x in range(width)
                    for y in range(height)
                },
                width * height // 2,
            )
        )
        self._remove_walls_until_connected()

    def _normalize(self, x: int, y: int) -> Tuple[int, int]:
        return (x % self.width, y % self.height)

    def has_wall_to_right(self, point: Tuple[int, int]) -> bool:
        return ("right", point) in self._all_walls

    def has_wall_to_left(self, point: Tuple[int, int]) -> bool:
        x, y = point
        return self.has_wall_to_right(self._normalize(x - 1, y))

    def has_wall_below(self, point: Tuple[int, int]) -> bool:
        return ("down", point) in self._all_walls

    def has_wall_above(self, point: Tuple[int, int]) -> bool:
        x, y = point
        return self.has_wall_below(self._normalize(x, y - 1))

    def _get_second_point(self, wall: Tuple[str, Tuple[int, int]]) -> Tuple[int, int]:
        direction, (x, y) = wall
        if direction == "right":
            return self._normalize(x + 1, y)
        if direction == "down":
            return self._normalize(x, y + 1)
        raise ValueError(direction)

    def debug_print(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                if self.has_wall_below(self._normalize(x, y)):
                    print("_", end="")
                else:
                    print(" ", end="")
                if self.has_wall_to_right(self._normalize(x, y)):
                    print("|", end="")
                else:
                    print(" ", end="")
            print("")

    def _get_containing_area(
        self, starting_point: Tuple[int, int]
    ) -> set[Tuple[int, int]]:
        points_to_visit = {starting_point}
        seen = {starting_point}

        while points_to_visit:
            x, y = points_to_visit.pop()
            left = self._normalize(x - 1, y)
            right = self._normalize(x + 1, y)
            up = self._normalize(x, y - 1)
            down = self._normalize(x, y + 1)

            if left not in seen and not self.has_wall_to_left((x, y)):
                seen.add(left)
                points_to_visit.add(left)

            if right not in seen and not self.has_wall_to_right((x, y)):
                seen.add(right)
                points_to_visit.add(right)

            if up not in seen and not self.has_wall_above((x, y)):
                seen.add(up)
                points_to_visit.add(up)

            if down not in seen and not self.has_wall_below((x, y)):
                seen.add(down)
                points_to_visit.add(down)

        return seen

    def _remove_walls_until_connected(self) -> None:
        while True:
            point_to_area_id = {}
            missing = {(x, y) for x in range(self.width) for y in range(self.height)}
            id_counter = 0

            while missing:
                missing_point = next(iter(missing))
                new_id = id_counter
                id_counter += 1
                for point in self._get_containing_area(missing_point):
                    point_to_area_id[point] = new_id
                    missing.remove(point)

            if id_counter == 1:
                break

            wall2remove = random.choice(
                [
                    wall
                    for wall in self._all_walls
                    if point_to_area_id[wall[1]]
                    != point_to_area_id[self._get_second_point(wall)]
                ]
            )
            self._all_walls.remove(wall2remove)
