from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Literal, Optional
import matplotlib.pyplot as plt


@dataclass
class Coords:
    x: int
    y: int

    def __add__(self, other: Move):
        if other.direction == 'R':
            self.x += 1

        if other.direction == 'L':
            self.x -= 1

        if other.direction == 'U':
            self.y += 1

        if other.direction == 'D':
            self.y -= 1

        return self

    def __eq__(self, other: Coords):
        return self.x == other.x and self.y == other.y

    def get_simple(self):
        return self.x, self.y

    def difference(self, coords: Coords):
        return math.fabs(self.x - coords.x) + math.fabs(self.y - coords.y)

    def find_point_between_coords(self, coords: Coords) -> Optional[Coords]:
        if self == coords or self.difference(coords) <= 2:
            return None
        else:
            x_diff = math.fabs(self.x - coords.x)
            y_diff = math.fabs(self.y - coords.y)

            if x_diff > y_diff:
                new_x = int(coords.x - (x_diff // 2)) if coords.x > self.x else int(coords.x + (x_diff // 2))
                return Coords(new_x, coords.y)
            elif y_diff > x_diff:
                new_y = int(coords.y - (y_diff // 2)) if coords.y > self.y else int(coords.y + (y_diff // 2))
                return Coords(coords.x, new_y)


@dataclass
class Move:
    direction: str


class Entity:
    def __init__(self, coords: Coords):
        self.coords: Coords = coords
        self.logs: List[Tuple[int, int]] = []

    def move(self, movement: Move):
        self.coords += movement

    def same_x(self, entity: Entity):
        return self.coords.x == entity.coords.x

    def same_y(self, entity: Entity):
        return self.coords.y == entity.coords.y


class RopeSegment(Entity):
    def __init__(self, next_segment: RopeSegment = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_segment = next_segment

    def notify(self):
        if self.next_segment:
            self.next_segment.update(self)

    def move(self, movement: Move):
        super().move(movement)
        self.notify()

    def update(self, previous_segment: RopeSegment):
        if self.coords.difference(previous_segment.coords) > 1:
            if self.same_x(previous_segment):
                if previous_segment.coords.y > self.coords.y:
                    self.move(Move('U'))
                else:
                    self.move(Move('D'))
            elif self.same_y(previous_segment):
                if previous_segment.coords.x > self.coords.x:
                    self.move(Move('R'))
                else:
                    self.move(Move('L'))

            elif point_between := self.coords.find_point_between_coords(previous_segment.coords):
                self.coords = point_between

        self.logs.append(self.coords.get_simple())

    def show_plot(self):
        xx = []
        yy = []
        for x, y in self.logs:
            xx.append(x)
            yy.append(y)

        plt.scatter(xx, yy, s=100)
        plt.show()


def load_actions(file_name):
    actions = []
    with open(file_name) as file:
        for line in file.readlines():
            clean_line = line.rstrip('\n')
            name, number = clean_line.split(' ')
            action = Move(name)
            for i in range(int(number)):
                actions.append(action)
    return actions


class Test:

    def __init__(self, file_name):
        self.actions = load_actions(file_name)
        self.s10 = RopeSegment(coords=Coords(1, 1))
        self.s9 = RopeSegment(coords=Coords(1, 1), next_segment=self.s10)
        self.s8 = RopeSegment(coords=Coords(1, 1), next_segment=self.s9)
        self.s7 = RopeSegment(coords=Coords(1, 1), next_segment=self.s8)
        self.s6 = RopeSegment(coords=Coords(1, 1), next_segment=self.s7)
        self.s5 = RopeSegment(coords=Coords(1, 1), next_segment=self.s6)
        self.s4 = RopeSegment(coords=Coords(1, 1), next_segment=self.s5)
        self.s3 = RopeSegment(coords=Coords(1, 1), next_segment=self.s4)
        self.s2 = RopeSegment(coords=Coords(1, 1), next_segment=self.s3)
        self.s1 = RopeSegment(coords=Coords(1, 1), next_segment=self.s2)

    def run(self):
        for movement in self.actions:
            self.s1.move(movement)
        assert len(set(self.s9.logs)) == 36


# test_case = Test('test_input.txt')
# test_case.run()


actions = load_actions('input.txt')

s10 = RopeSegment(coords=Coords(1, 1))
s9 = RopeSegment(coords=Coords(1, 1), next_segment=s10)
s8 = RopeSegment(coords=Coords(1, 1), next_segment=s9)
s7 = RopeSegment(coords=Coords(1, 1), next_segment=s8)
s6 = RopeSegment(coords=Coords(1, 1), next_segment=s7)
s5 = RopeSegment(coords=Coords(1, 1), next_segment=s6)
s4 = RopeSegment(coords=Coords(1, 1), next_segment=s5)
s3 = RopeSegment(coords=Coords(1, 1), next_segment=s4)
s2 = RopeSegment(coords=Coords(1, 1), next_segment=s3)
s1 = RopeSegment(coords=Coords(1, 1), next_segment=s2)


for movement in actions:
    s1.move(movement)


print(len(set(s9.logs)))