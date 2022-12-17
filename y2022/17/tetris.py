import itertools
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import List, Tuple

from y2022.helpers import load_file


@dataclass
class Coord:
    x: int
    y: int

    def __lt__(self, other):
        return self.y < other.y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class RockShape:

    def __init__(self, left: int, bottom: int):
        self.bottom = bottom
        self.left = left
        self.tiles = self.get_tiles()

    @property
    def top_tile(self):
        return max(self.tiles)

    @property
    def bottom_tile(self):
        return min(self.tiles)

    # @cached_property
    # def tiles(self) -> List[Coord]:
    #     return self.get_tiles()

    def get_tiles(self) -> List[Coord]:
        raise NotImplementedError()


class RockLine(RockShape):
    """
        ####
    """
    def get_tiles(self):
        return [Coord(self.left+i, self.bottom) for i in range(4)]


class RockPlus(RockShape):
    """
        .#.
        ###
        .#.
    """
    def get_tiles(self):
        return [Coord(self.left+1, self.bottom+2)] + \
               [Coord(self.left+i, self.bottom+1) for i in range(3)] + \
               [Coord(self.left+1, self.bottom)]


class RockAngle(RockShape):
    """
        ..#
        ..#
        ###
    """
    def get_tiles(self):
        return [Coord(self.left+2, self.bottom+1+i) for i in range(2)] + \
               [Coord(self.left+i, self.bottom) for i in range(3)]


class RockPipe(RockShape):
    """
        #
        #
        #
        #
    """
    def get_tiles(self):
        return [Coord(self.left, self.bottom+i) for i in range(4)]


class RockSquare(RockShape):
    """
        ##
        ##
    """
    def get_tiles(self):
        return [Coord(self.left+i, self.bottom) for i in range(2)] + \
               [Coord(self.left+i, self.bottom+1) for i in range(2)]


class RockGenerator:

    def __init__(self):
        self.cycle = itertools.cycle([RockLine, RockPlus, RockAngle, RockPipe, RockSquare])

    def next(self, left: int, bottom: int) -> RockShape:
        shape = next(self.cycle)
        return shape(left, bottom)


class Blocked(Exception):
    pass


class Chamber:
    chamber_width = 7

    def __init__(self, streams, limit=2022):
        self.streams = streams
        self.limit = limit
        self.rock_generator = RockGenerator()
        self.top = 0
        self.tiles: List[Coord] = []
        self.rocks = 0

    def show(self, rock: RockShape = None):
        print('\n')
        for y in range(self.top+5, 0, -1):
            row = '|'
            for x in range(self.chamber_width):
                coord = Coord(x, y)
                if rock and coord in rock.tiles:
                    row += '@'
                elif coord in self.tiles:
                    row += '#'
                else:
                    row += '.'
            row += '|'
            print(row)
        print('+-------+')

    def create_new_rock(self) -> RockShape:
        return self.rock_generator.next(2, self.top+4)

    def move_tiles(self, rock, vector: Tuple[int, int]):
        x, y = vector
        return [Coord(tile.x+x, tile.y+y) for tile in rock.tiles]

    def move_rock_right(self, rock: RockShape):
        new_tiles = self.move_tiles(rock, (1, 0))
        for tile in new_tiles:
            if tile in self.tiles or tile.x > self.chamber_width-1:
                raise Blocked()
        rock.tiles = new_tiles

    def move_rock_left(self, rock: RockShape):
        new_tiles = self.move_tiles(rock, (-1, 0))
        for tile in new_tiles:
            if tile in self.tiles or tile.x < 0:
                raise Blocked()
        rock.tiles = new_tiles

    def move_rock_down(self, rock: RockShape):
        new_tiles = self.move_tiles(rock, (0, -1))
        for tile in new_tiles:
            if tile in self.tiles or tile.y == 0:
                raise Blocked()
        rock.tiles = new_tiles

    def shower(self, show_progress=False, show_starts=False):
        rock = None
        stream_iter = itertools.cycle(self.streams)
        while self.rocks < self.limit:
            stream = next(stream_iter)

            if show_progress:
                print(stream)
            if not rock:
                rock = self.create_new_rock()
                if show_progress or show_starts:
                    self.show(rock)

            if stream == '>':
                try:
                    self.move_rock_right(rock)
                    if show_progress:
                        self.show(rock)
                except Blocked:
                    pass

            elif stream == '<':
                try:
                    self.move_rock_left(rock)
                    if show_progress:
                        self.show(rock)
                except Blocked:
                    pass

            try:
                self.move_rock_down(rock)
                if show_progress:
                    self.show(rock)
            except Blocked:
                self.tiles += rock.tiles
                self.top = max(rock.tiles).y if max(rock.tiles).y > self.top else self.top
                self.rocks += 1
                print(f'{self.rocks}/{self.limit}')
                rock = None


def load_jets(file_name):
    jets = load_file(file_name)[0]
    return list(jets)


if __name__ == '__main__':
    jets = load_jets('input.txt')
    test_jets = load_jets('test_input.txt')
    single_rock_stream = ['>', '>', '>', '<']
    two_rocks_stream = ['>', '>', '>', '<', '<', '>', '<', '>']
    three_rocks_stream = list('>>><<><>><<<>')

    chamber = Chamber(jets)
    chamber.shower(False, False)

    print(chamber.top)
    print(chamber.rocks)
