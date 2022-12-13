from collections import Counter
from dataclasses import dataclass, field
from itertools import chain
from typing import List


@dataclass(frozen=True)
class Item:
    name: str

    @property
    def points(self):
        if self.name.isupper():
            return ord(self.name) - 38
        else:
            return ord(self.name) - 96


assert Item('a').points == 1
assert Item('z').points == 26
assert Item('A').points == 27
assert Item('Z').points == 52


@dataclass
class Backpack:
    contents: str

    @property
    def size(self):
        return len(self.contents)

    @property
    def first_compartment(self):
        return self.contents[:self.size//2]

    @property
    def second_compartment(self):
        return self.contents[self.size//2:]

    @property
    def unique_items(self):
        return set(Item(letter) for letter in self.contents)

    @property
    def doubled_item(self):
        for letter in self.first_compartment:
            if letter in self.second_compartment:
                return Item(letter)


@dataclass
class ElvGroup:
    backpacks: List[Backpack] = field(default_factory=list)

    def is_full(self):
        return len(self.backpacks) == 3

    def get_backpack_unique_items(self):
        for backpack in self.backpacks:
            for item in backpack.unique_items:
                yield item

    @property
    def badge(self):
        counted_items = Counter(self.get_backpack_unique_items())
        return list(counted_items.keys())[list(counted_items.values()).index(3)]


test_1_group = ElvGroup([
        Backpack('vJrwpWtwJgWrhcsFMMfFFhFp'),
        Backpack('jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL'),
        Backpack('PmmdzqPrVvPwwTWBwg')
])
assert test_1_group.badge == Item('r')
assert test_1_group.badge.points == 18

test_2_group = ElvGroup([
        Backpack('wMqvLMZHhHMvwLHjbvcjnnSBnvTQFn'),
        Backpack('ttgJtRGJQctTZtZT'),
        Backpack('CrZsJsPPZsGzwwsLwLmpwMDw')
])
assert test_2_group.badge == Item('Z')
assert test_2_group.badge.points == 52

assert test_1_group.badge.points + test_2_group.badge.points == 70


with open('input.txt') as file:

    items_priority_sum = 0

    groups = []
    group = ElvGroup()

    for line in file.readlines():
        new_backpack = Backpack(line.rstrip('\n'))
        group.backpacks.append(new_backpack)

        if group.is_full():
            groups.append(group)
            items_priority_sum += group.badge.points
            group = ElvGroup()

assert len(groups) == 100


