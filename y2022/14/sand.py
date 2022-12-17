from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property, lru_cache
from typing import List, Tuple, Set, Dict, TypeAlias

from y2022.helpers import load_file


class CavernContents(Enum):
    air = 'air'
    rock = 'rock'
    sand = 'sand'

    @classmethod
    def display_characters(cls):
        return {
            cls.air: '.',
            cls.rock: '#',
            cls.sand: 'o'
        }

    @property
    def display(self):
        return self.display_characters()[self]


@dataclass(frozen=True)
class Coord:
    x: int
    y: int

    def down(self):
        return Coord(self.x, self.y+1)

    def left(self):
        return Coord(self.x-1, self.y)

    def right(self):
        return Coord(self.x+1, self.y)


@dataclass
class Tile:
    content: CavernContents

    @property
    def display(self):
        return self.content.display


@dataclass
class RockPath:
    route: str

    @property
    def cleaned(self) -> list[Coord]:
        return [Coord(int(point.split(',')[0]), int(point.split(',')[1])) for point in self.route.split(' -> ')]

    @property
    def length(self):
        return len(self.cleaned)

    @property
    def lines(self) -> List[Tuple]:
        return [(self.cleaned[i], self.cleaned[i+1]) for i in range(self.length) if i + 1 != self.length]

    @staticmethod
    def get_tiles_between(start: Coord, end: Coord):
        match end.x, end.y:
            case start.x, start.y:
                return []
            case start.x, _:
                range_y = range(start.y, end.y+1) if end.y > start.y else range(end.y, start.y+1)
                return [Coord(start.x, y) for y in range_y]
            case _, start.y:
                range_x = range(start.x, end.x+1) if end.x > start.x else range(end.x, start.x+1)
                return [Coord(x, start.y) for x in range_x]

    @property
    def tiles(self) -> dict:
        tiles = {}
        for start, end in self.lines:
            tiles[start] = Tile(CavernContents.rock)
            tiles[end] = Tile(CavernContents.rock)
            for tile in self.get_tiles_between(start, end):
                tiles[tile] = Tile(CavernContents.rock)
        return tiles


class FallenIntoEmptiness(Exception):
    pass


class SpaceFilled(Exception):
    pass


class Stopped(Exception):
    pass


class Cavern:
    sand_start_point = Coord(500, 0)
    x_axis = 800

    def __init__(self, rocks: Dict):
        self.rocks = rocks
        self.air = self.load_air()
        self.tiles = self.air | self.rocks
        self.build_rock_floor()

    def load_air(self) -> dict:
        air_tiles = {}
        for x in range(self.x_axis+1):
            for y in range(self.y_axis+1):
                air_coord = Coord(x, y)
                if air_coord not in self.rocks.keys():
                    air_tiles[air_coord] = Tile(CavernContents.air)
        return air_tiles

    def build_rock_floor(self):
        for x in range(self.x_axis+1):
            self.tiles[Coord(x, self.y_axis)].content = CavernContents.rock

    @property
    def y_axis(self):
        return max(rock.y for rock in self.rocks.keys())+2

    def show(self, file_name, with_prints=False):
        with open(file_name, 'w') as file:
            if with_prints:
                print(f'Created file {file_name}')
            for y in range(self.y_axis+1):
                if with_prints:
                    print(f'Writing line: {y}')
                line = ''
                for x in range(self.x_axis+1):
                    line += self.tiles[Coord(x, y)].display
                line += '\n'
                file.write(line)

    def get_avaible_coord(self, coord):
        tile_below = self.tiles.get(coord.down())
        if not tile_below:
            raise FallenIntoEmptiness()

        if self.tiles[coord.down()].content == CavernContents.air:
            return coord.down()

        if self.tiles[coord.down().left()].content == CavernContents.air:
            return coord.down().left()

        if self.tiles[coord.down().right()].content == CavernContents.air:
            return coord.down().right()

        raise Stopped()

    def move_sand(self, sand_coord) -> Coord:
        new_coord = self.get_avaible_coord(sand_coord)
        self.tiles[sand_coord].content = CavernContents.air
        self.tiles[new_coord].content = CavernContents.sand
        return new_coord

    def generate_single_sand(self):
        sand_coord = self.sand_start_point
        if self.tiles[sand_coord].content == CavernContents.sand:
            raise SpaceFilled()
        else:
            self.tiles[sand_coord].content = CavernContents.sand
        while True:
            try:
                sand_coord = self.move_sand(sand_coord)
            except Stopped:
                break

    def generate_all_the_sand(self):
        sand_units_generated = 0
        while True:
            try:
                self.generate_single_sand()
            except FallenIntoEmptiness:
                break
            except SpaceFilled:
                break
            else:
                sand_units_generated += 1
        return sand_units_generated


def load_rock_paths(file_name='input.txt'):
    rocks = dict()
    for line in load_file(file_name):
        path = RockPath(line)
        rocks.update(path.tiles)
    return rocks


# test_rocks = load_rock_paths('test_input.txt.txt')
# assert len(test_rocks) == 20
# test_cavern = Cavern(test_rocks)
#
# assert test_cavern.y_axis == 11
#
# test_cavern.show('test_cavern_empty.txt')
# test_generated_sand = test_cavern.generate_all_the_sand()
# test_cavern.show('test_cavern_with_sand.txt')
#
# assert test_generated_sand == 93


rocks = load_rock_paths()
cavern = Cavern(rocks)
cavern.show('without_sand.txt')
sand_generated = cavern.generate_all_the_sand()
cavern.show('with_all_sand.txt')
