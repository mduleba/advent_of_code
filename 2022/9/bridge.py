from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Literal


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

    def difference(self, coords: Coords):
        return math.fabs(self.x - coords.x) + math.fabs(self.y - coords.y)

    def axis_with_bigger_difference(self, coords: Coords):
        x_diff = math.fabs(self.x - coords.x)
        y_diff = math.fabs(self.y - coords.y)
        if x_diff > y_diff:
            return 'x'
        elif y_diff > x_diff:
            return 'y'
        else:
            return None


@dataclass
class Move:
    direction: str


class Entity:
    def __init__(self, coords: Coords):
        self.coords: Coords = coords

    def move(self, movement: Move):
        self.coords += movement

    def same_x(self, entity: Entity):
        return self.coords.x == entity.coords.x

    def same_y(self, entity: Entity):
        return self.coords.y == entity.coords.y


class Tail(Entity):
    def update(self, head: Head):
        if self.coords != head.coords:

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

            elif self.coords.difference(head.coords) > 2:
                pass

            else:
                pass


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


actions = load_actions('input.txt')

tail = Tail(coords=Coords(0, 0))
head = Head(coords=Coords(1, 0), tail=tail)

for movement in actions:
    head.move(movement)
