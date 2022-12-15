from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property, lru_cache
from math import sin, pi, cos
from typing import List, Tuple, Set, Dict, Optional

from y2022.helpers import load_file
import re
import numpy as np


@dataclass(frozen=True)
class Coord:
    x: int
    y: int

    @property
    def value(self):
        return self.x, self.y

    def manhattan_distance(self, coord: Coord):
        return sum(abs(val1 - val2) for val1, val2 in zip((self.x, self.y), (coord.x, coord.y)))


@dataclass
class Beacon:
    coord: Coord

    @property
    def tunning_frequency(self):
        return self.coord.x * 4000000 + self.coord.y


@dataclass
class Sensor:
    coord: Coord
    closest_beacon: Beacon

    @cached_property
    def range(self):
        return self.coord.manhattan_distance(self.closest_beacon.coord)

    @cached_property
    def x_max(self):
        return self.coord.x + self.range

    @cached_property
    def x_min(self):
        return self.coord.x - self.range

    def is_coord_in_range(self, coord: Coord):
        return self.coord.manhattan_distance(coord) <= self.range

    def outside_edge_points(self, min_r, max_r):
        edge_points = set()
        edge_variants = [
            lambda i: (self.x_max-i+1, self.coord.y-i),
            lambda i: (self.x_max-i+1, self.coord.y+i),
            lambda i: (self.x_min+i-1, self.coord.y-i),
            lambda i: (self.x_min+i-1, self.coord.y+i),
        ]
        for i in range(self.range+2):
            for edge_variant in edge_variants:
                x, y = edge_variant(i)
                if min_r <= x <= max_r and min_r <= y <= max_r:
                    edge_points.add(Coord(x, y))

        return edge_points


def load_data(file_name):
    sensors = []
    xy_re = re.compile('x=(?P<x>.*), y=(?P<y>.*)')
    for line in load_file(file_name):
        sensor_coord, beacon_coord = [Coord(int(xy_re.findall(part)[0][0]), int(xy_re.findall(part)[0][1]))
                                      for part in line.split(':')]

        beacon = Beacon(beacon_coord)
        sensors.append(Sensor(sensor_coord, closest_beacon=beacon))
    return sensors


@dataclass
class Tunnels:
    sensors: List[Sensor]

    @cached_property
    def coords(self) -> Dict[Coord, str]:
        coords = {}
        for sensor in self.sensors:
            coords[sensor.coord] = 'S'
            coords[sensor.closest_beacon.coord] = 'B'
        return coords

    @cached_property
    def max_y(self):
        return max(coord.y for coord in self.coords.keys()) + self.biggest_range

    @cached_property
    def min_y(self):
        return min(coord.y for coord in self.coords.keys()) - self.biggest_range

    @cached_property
    def max_x(self):
        return max(coord.x for coord in self.coords.keys()) + self.biggest_range

    @cached_property
    def min_x(self):
        return min(coord.x for coord in self.coords.keys()) - self.biggest_range

    @cached_property
    def biggest_range(self):
        return max(sensor.range for sensor in self.sensors)

    def show(self, output_file, with_range=False, custom_limit: Optional[Tuple[int, int]] = None, only_edge=False):
        if custom_limit:
            min_l, max_l = custom_limit
            min_y, min_x = min_l, min_l
            max_y, max_x = max_l, max_l
        else:
            min_y = self.min_y
            max_y = self.max_y
            min_x = self.min_x
            max_x = self.max_x

        with open(output_file, 'w') as file:
            for y in range(min_y, max_y + 1):
                line = f'{y}: '.zfill(5)
                for x in range(min_x, max_x + 1):
                    added = False
                    point = Coord(x, y)

                    if letter := self.coords.get(point):
                        line += letter
                        added = True
                    elif with_range:
                        for sensor in self.sensors:
                            if only_edge:
                                if point in sensor.outside_edge_points(min_y, max_y):
                                    line += '#'
                                    added = True
                                    break

                            if not only_edge:
                                if sensor.is_coord_in_range(point):
                                    line += '#'
                                    added = True
                                    break

                    if not added:
                        line += '.'

                file.write(line + '\n')

    def check_row(self, y: int):
        points_in_range = 0
        for x in range(self.min_x, self.max_x+1):
            point = Coord(x, y)
            for sensor in self.sensors:

                if point in (sensor.coord, sensor.closest_beacon.coord):
                    continue

                if sensor.is_coord_in_range(point):
                    points_in_range += 1
                    break

        return points_in_range

    def print_row(self, y: int):
        row = f'{y}: '.zfill(5)
        for x in range(self.min_x, self.max_x + 1):
            added = False
            point = Coord(x, y)
            if letter := self.coords.get(point):
                row += letter
                added = True
            else:
                for sensor in self.sensors:
                    point = Coord(x, y)
                    if sensor.is_coord_in_range(point):
                        row += '#'
                        added = True
                        break

            if not added:
                row += '.'
        return row

    def sensor_with_range(self, coord: Coord) -> Optional[Sensor]:
        for sensor in self.sensors:
            if sensor.is_coord_in_range(coord):
                return sensor

    def find_on_edge(self, min_r, max_r):
        i = 1
        for sensor in self.sensors:
            print(f'\nChecking sensor: {i} of {len(self.sensors)}')
            length = len(sensor.outside_edge_points(min_r, max_r))
            j = 1
            for point in sensor.outside_edge_points(min_r, max_r):
                print(f'Checking points: {j} from {length}')
                if self.sensor_with_range(point):
                    j += 1
                    continue
                else:
                    return point
            i += 1


test_sensors = load_data('test.txt')
test_tunnels = Tunnels(test_sensors)

assert test_tunnels.check_row(10) == 26
assert test_tunnels.find_on_edge(0, 20) == Coord(14, 11)


if __name__ == '__main__':

    sensors = load_data('input.txt')
    tunnels = Tunnels(sensors)

    beacon = Beacon(tunnels.find_on_edge(0, 4000000))
