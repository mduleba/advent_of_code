from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass
class Section:
    id: int


@dataclass
class Assignment:
    sections_range: str

    @property
    def start(self):
        return int(self.sections_range.split('-')[0])

    @property
    def end(self):
        return int(self.sections_range.split('-')[1])

    @property
    def sections(self):
        return [Section(section) for section in range(self.start, self.end+1)]

    def contains_another_assignment(self, other: Assignment):
        return all(section in self.sections for section in other.sections)

    def overlap_another_assignment(self, other: Assignment):
        return any(section in self.sections for section in other.sections)


assert Assignment('1-3').sections == [Section(1), Section(2), Section(3)]
assert Assignment('1-3').contains_another_assignment(Assignment('2-2'))
assert not Assignment('7-91').overlap_another_assignment(Assignment('1-6'))


@dataclass
class Pair:
    assigments: str

    @property
    def cleaned_assigments(self):
        first, second = self.assigments.split(',')
        return first, second.rstrip('\n')

    @property
    def first_elv_assignment(self):
        return Assignment(self.cleaned_assigments[0])

    @property
    def second_elv_assignment(self):
        return Assignment(self.cleaned_assigments[1])

    def overlap(self):
        return self.first_elv_assignment.overlap_another_assignment(self.second_elv_assignment)\
               or self.second_elv_assignment.overlap_another_assignment(self.first_elv_assignment)


test_pair = Pair('2-8,3-7')
assert test_pair.first_elv_assignment.sections == [Section(i) for i in range(2, 9)]


with open('input.txt') as file:

    counter = 0
    for line in file.readlines():
        pair = Pair(line)
        if pair.overlap():
            counter += 1
