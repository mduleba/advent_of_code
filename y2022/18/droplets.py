import itertools
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import List, Tuple, Dict, Set

from y2022.helpers import load_file
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


@dataclass
class Coord:
    x: int
    y: int
    z: int

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z


@dataclass
class Cube(Coord):
    EDGE_SIZE = 1

    def create_edges(self) -> List[Coord]:
        return [
            Coord(self.x+self.EDGE_SIZE, self.y, self.z),
            Coord(self.x-self.EDGE_SIZE, self.y, self.z),
            Coord(self.x, self.y+self.EDGE_SIZE, self.z),
            Coord(self.x, self.y-self.EDGE_SIZE, self.z),
            Coord(self.x, self.y, self.z+self.EDGE_SIZE),
            Coord(self.x, self.y, self.z-self.EDGE_SIZE),
        ]

    def __post_init__(self):
        self.edges = self.create_edges()

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return super().__eq__(other)


def load_droplets(file_name):
    droplets = set()
    for line in load_file(file_name):
        x_str, y_str, z_str = line.split(',')
        droplets.add(Cube(int(x_str), int(y_str), int(z_str)))
    return droplets


@dataclass
class Obsidian:
    droplets: Set[Cube]

    @cached_property
    def size(self):
        return len(self.droplets)

    @cached_property
    def exposed_sides(self):
        exposed_sides = []
        for droplet in self.droplets:
            for edge in droplet.edges:
                if edge not in self.droplets:
                    exposed_sides.append(edge)
        return exposed_sides

    @cached_property
    def pockets(self):
        water = set()
        air = set()
        for side in self.exposed_sides:
            cube = Cube(side.x, side.y, side.z)

            if all(edge in self.droplets for edge in cube.edges):
                air.add(cube)
            else:
                water.add(cube)

        for cube in water:
            if all(edge in self.droplets or edge in water for edge in cube.edges):
                air.add(cube)

        return water, air

    @property
    def water(self):
        return self.pockets[0]

    @property
    def air(self):
        return self.pockets[1]

    def water_exposed_sides(self):
        return [side for side in self.exposed_sides if side in self.water]

    def inside_sides(self):
        return [side for side in self.exposed_sides if side in self.air]


if __name__ == '__main__':
    simple_droplets = {Cube(1, 1, 1), Cube(2, 1, 1)}
    test_droplets = load_droplets('test_input.txt')
    input_droplets = load_droplets('input.txt')

    obsidian = Obsidian(input_droplets)
    print(len(obsidian.exposed_sides) - len(obsidian.inside_sides()))

