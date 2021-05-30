import random

width = 7
height = 3


def normalize(x, y):
    return (x % width, y % height)


class Walls:

    def __init__(self):
        self._all_walls = {
            (direction, (x, y))
            for direction in {'right', 'down'}
            for x in range(width)
            for y in range(height)
        }

    def has_wall_to_right(self, point):
        return ('right', point) in self._all_walls

    def has_wall_to_left(self, point):
        x, y = point
        return self.has_wall_to_right(normalize(x-1, y))

    def has_wall_below(self, point):
        return ('down', point) in self._all_walls

    def has_wall_above(self, point):
        x, y = point
        return self.has_wall_below(normalize(x, y-1))

    def get_all_walls(self):
        return list(self._all_walls)

    def get_points(self, wall):
        direction, (x, y) = wall
        if direction == 'right':
            return ((x, y), normalize(x+1, y))
        elif direction == 'down':
            return ((x, y), normalize(x, y+1))
        else:
            raise ValueError(direction)

    def remove(self, wall):
        self._all_walls.remove(wall)

    def debug_print(self):
        for y in range(height):
            for x in range(width):
                if self.has_wall_below(normalize(x, y)):
                    print('_', end='')
                else:
                    print(' ', end='')
                if self.has_wall_to_right(normalize(x, y)):
                    print('|', end='')
                else:
                    print(' ', end='')
            print('')


def get_containing_area(walls, starting_point):
    points_to_visit = {starting_point}
    seen = {starting_point}

    while points_to_visit:
        x, y = points_to_visit.pop()
        left = normalize(x-1, y)
        right = normalize(x+1, y)
        up = normalize(x, y-1)
        down = normalize(x, y+1)

        if left not in seen and not walls.has_wall_to_left((x, y)):
            seen.add(left)
            points_to_visit.add(left)

        if right not in seen and not walls.has_wall_to_right((x, y)):
            seen.add(right)
            points_to_visit.add(right)

        if up not in seen and not walls.has_wall_above((x, y)):
            seen.add(up)
            points_to_visit.add(up)

        if down not in seen and not walls.has_wall_below((x, y)):
            seen.add(down)
            points_to_visit.add(down)

    return seen


def make_connected(walls: Walls):
    while True:
        point_to_area_id = {}
        missing = {(x, y) for x in range(width) for y in range(height)}
        id_counter = 0

        while missing:
            missing_point = next(iter(missing))
            new_id = id_counter
            id_counter += 1
            for point in get_containing_area(walls, missing_point):
                point_to_area_id[point] = new_id
                missing.remove(point)

        if id_counter == 1:
            break

        wall2remove = random.choice([
            wall
            for wall in walls.get_all_walls()
            if point_to_area_id[walls.get_points(wall)[0]] != point_to_area_id[walls.get_points(wall)[1]]
        ])
        walls.remove(wall2remove)


random.seed(1)
walls = Walls()
make_connected(walls)
