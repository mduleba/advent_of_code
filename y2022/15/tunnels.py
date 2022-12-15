from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property, lru_cache
from typing import List, Tuple, Set, Dict, TypeAlias

from y2022.helpers import load_file
import re


@dataclass(frozen=True)
class Coord:
    _x: str
    _y: str

    @cached_property
    def x(self):
        return int(self._x)

    @cached_property
    def y(self):
        return int(self._y)

    @property
    def value(self):
        return self.x, self.y

    def manhattan_distance(self, coord: Coord):
        return sum(abs(val1 - val2) for val1, val2 in zip((self.x, self.y), (coord.x, coord.y)))


@dataclass
class Beacon:
    coord: Coord


@dataclass
class Sensor:
    coord: Coord
    closest_beacon: Beacon

    @cached_property
    def range(self):
        return self.coord.manhattan_distance(self.closest_beacon.coord)

    def coord_in_range(self, coord: Coord):
        return self.coord.manhattan_distance(coord) <= self.range


def load_data(file_name):
    sensors = []
    xy_re = re.compile('x=(?P<x>.*), y=(?P<y>.*)')
    for line in load_file(file_name):
        sensor_coord, beacon_coord = [Coord(*xy_re.findall(part)[0]) for part in line.split(':')]
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

    def show(self, output_file, with_range=False):
        with open(output_file, 'w') as file:
            for y in range(self.min_y, self.max_y + 1):
                line = f'{y}: '.zfill(5)
                for x in range(self.min_x, self.max_x + 1):
                    added = False
                    point = Coord(str(x), str(y))

                    if letter := self.coords.get(point):
                        line += letter
                        added = True
                    elif with_range:
                        for sensor in self.sensors:
                            if sensor.coord_in_range(point):
                                line += '#'
                                added = True
                                break

                    if not added:
                        line += '.'

                file.write(line + '\n')

    def check_row(self, y: int):
        print(f'Checking row: {y}')
        row = str(y)
        points_in_range = 0
        for x in range(self.min_x, self.max_x+1):
            print(f'\nChecking column: {x} in range {self.min_x} - {self.max_x}')
            point = Coord(str(x), row)
            for sensor in self.sensors:

                # eeeemmm something fcked
                if point in (sensor.coord, sensor.closest_beacon.coord):
                    continue

                if sensor.coord_in_range(point):
                    points_in_range += 1
                    break

        return points_in_range

    def print_row(self, y: int):
        row = f'{y}: '.zfill(5)
        for x in range(self.min_x, self.max_x + 1):
            added = False
            point = Coord(str(x), str(y))
            if letter := self.coords.get(point):
                row += letter
                added = True
            else:
                for sensor in self.sensors:
                    point = Coord(str(x), str(y))
                    if sensor.coord_in_range(point):
                        row += '#'
                        added = True
                        break

            if not added:
                row += '.'

        return row


test_sensors = load_data('test.txt')
test_tunnels = Tunnels(test_sensors)
assert test_tunnels.check_row(10) == 26


sensors = load_data('input.txt')
tunnels = Tunnels(sensors)

# r2000000 = tunnels.check_row(2000000)