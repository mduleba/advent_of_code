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
                return Coords(int(coords.x - (x_diff // 2)), coords.y)
            elif y_diff > x_diff:
                return Coords(coords.x, int(coords.y - (y_diff // 2)))


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


class Tail(Entity):
    def update(self, head: Head):
        if self.coords.difference(head.coords) > 1:
            if self.same_x(head):
                if head.coords.y > self.coords.y:
                    self.move(Move('U'))
                else:
                    self.move(Move('D'))
            elif self.same_y(head):
                if head.coords.x > self.coords.x:
                    self.move(Move('R'))
                else:
                    self.move(Move('L'))

            elif point_between := self.coords.find_point_between_coords(head.coords):
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


class Head(Entity):

    def __init__(self, tail: Tail, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tail = tail

    def notify(self):
        self.tail.update(self)

    def move(self, movement: Move):
        super().move(movement)
        self.notify()


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
        self.tail = Tail(coords=Coords(1, 1))
        self.head = Head(coords=Coords(1, 1), tail=self.tail)

    def run(self):
        assert len(self.actions) == 24
        for movement in self.actions:
            self.head.move(movement)
        assert self.head.coords == Coords(3, 3)
        assert self.tail.coords == Coords(2, 3)
        assert len(set(self.tail.logs)) == 13


test_case = Test('test_input.txt')
test_case.run()


actions = load_actions('input.txt')

tail = Tail(coords=Coords(1, 1))
head = Head(coords=Coords(1, 1), tail=tail)

for movement in actions:
    head.move(movement)

print(len(set(tail.logs)))