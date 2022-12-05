import re
from dataclasses import dataclass, field
from functools import cached_property
from typing import List, Dict, Tuple, Optional


@dataclass
class Crate:
    name: str


@dataclass
class Stack:
    crates: List[Crate]

    @property
    def size(self):
        return len(self.crates)

    def top_stack_indexes(self, number_of_crates):
        if number_of_crates > self.size:
            number_of_crates = self.size
        return [i for i in range(self.size-number_of_crates, self.size)]

    def move_from_stack(self, number_of_crates) -> List[Crate]:
        indexes = self.top_stack_indexes(number_of_crates)
        crates = self.crates[min(indexes):max(indexes)+1]
        del self.crates[min(indexes):max(indexes)+1]

        return crates

    def add_to_stack(self, crates_list: List[Crate]):
        for crate in crates_list:
            self.crates.append(crate)

    def top_element_name(self):
        return self.crates[-1].name


class Cargo:
    CRATE_SIZE = 4

    def __init__(self, ship_name: str):
        self.ship_name = ship_name
        self.stacks: Optional[Dict[int, Stack]] = None

    @cached_property
    def rows(self) -> List[str]:
        rows = []
        max_size = 0
        with open(self.ship_name) as file:
            for line in reversed(file.readlines()):
                clean_line = line.rstrip('\n')
                if max_size < len(clean_line):
                    max_size = len(clean_line)

                clean_line = clean_line.ljust(max_size)
                rows.append(clean_line)
        return rows

    def init_stacks(self):
        stacks = {}
        for i in range(1, len(self.rows[0]) // 4 + 2):
            stacks[i] = Stack([])
        self.stacks = stacks

    def stack_value_index(self, column) -> int:
        column_index = column*self.CRATE_SIZE
        return column_index-3

    def load_crates(self):
        self.init_stacks()
        for row in self.rows:
            for col, stack in self.stacks.items():
                crate_name = row[self.stack_value_index(col)]
                if crate_name.strip():
                    self.stacks[col].crates.append(Crate(crate_name))

    def top_elements_name(self):
        name = ''
        for stack in self.stacks.values():
            name += stack.top_element_name()
        return name


@dataclass
class Operations:
    number_of_crates: int
    from_stack_index: int
    to_stack_index: int

    def perform_on_cargo(self, cargo: Cargo):
        crates = cargo.stacks[self.from_stack_index].move_from_stack(self.number_of_crates)
        cargo.stacks[self.to_stack_index].add_to_stack(crates)


initial_cargo = Cargo('cargo.txt')
initial_cargo.load_crates()


def load_operations(file_name: str) -> List[Operations]:
    operations = []
    with open(file_name) as file:
        for line in file.readlines():
            z = re.match(r'move (?P<count>\d*) from (?P<from>\d*) to (?P<to>\d*)', line)
            operations.append(Operations(*[int(group) for group in z.groups()]))
    return operations


operations = load_operations('movement.txt')

for operation in operations:
    operation.perform_on_cargo(initial_cargo)

print(initial_cargo.top_elements_name())

