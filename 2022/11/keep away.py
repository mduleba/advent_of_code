from dataclasses import dataclass, field
from enum import Enum
from math import floor
from typing import List, Dict, Tuple
from math import prod

@dataclass
class Item:
    worry_lvl: int

    unique: object = field(init=False)

    def __post_init__(self):
        self.unique = object()

    def check_for_damage(self, mod=None):
        if mod:
            self.worry_lvl %= mod
        else:
            self.worry_lvl = int(floor(self.worry_lvl / 3))

class OperationType(Enum):
    add = '+'
    sub = '-'
    mul = '*'
    pow = '^'

    @classmethod
    def actions(cls):
        return {
            cls.add: lambda val_1, val_2: val_1 + val_2,
            cls.sub: lambda val_1, val_2: val_1 - val_2,
            cls.mul: lambda val_1, val_2: val_1 * val_2,
            cls.pow: lambda val_1, val_2: val_1 ** 2,
        }

    @property
    def action(self):
        return self.actions()[self]


class Operation:
    def __init__(self, ot: OperationType, value: int = None):
        self.ot = ot
        self.value = value

    def compute(self, worry_lvl):
        return self.ot.action(worry_lvl, self.value)


@dataclass
class Monke:
    index: int
    items: List[Item]
    operation: Operation

    divisible_by: int
    monkey_to_throw_on_true: int
    monkey_to_throw_on_false: int

    inspected_items: int = 0

    def receive(self, item: Item):
        self.items.append(item)

    def throw(self, item: Item):
        self.items.remove(item)
        return item

    def inspect(self, item: Item):
        self.inspected_items += 1
        item.worry_lvl = self.operation.compute(item.worry_lvl)

    def turn(self, divisible: int) -> List[Tuple[int, Item]]:
        thrown_items = []
        while self.items:
            item = self.items[0]
            self.inspect(item)
            item.check_for_damage(divisible)
            target_monkey_index = self.where_to_throw(item)
            thrown_items.append((target_monkey_index, item))
            del self.items[0]

        return thrown_items

    def where_to_throw(self, item: Item):
        if item.worry_lvl % self.divisible_by == 0:
            return self.monkey_to_throw_on_true
        else:
            return self.monkey_to_throw_on_false


def load_initial_monkeys(file_name):
    monkeys = {}
    with open(file_name) as file:
        monkey_props = {}
        for line in file.readlines():
            clean_line = line.rstrip('\n').lstrip()
            if not clean_line:
                monkey_props = {}

            if clean_line.startswith('Monkey'):
                _, index = clean_line.split(' ')
                monkey_props['index'] = int(index.rstrip(':'))

            if clean_line.startswith('Starting items:'):
                items = clean_line.lstrip('Starting items: ').split(', ')
                monkey_props['items'] = [Item(int(worry_lvl)) for worry_lvl in items]

            if clean_line.startswith('Operation:'):
                operation_str = clean_line.lstrip('Operation: new =')
                if operation_str == 'ld * old':
                    monkey_props['operation'] = Operation(OperationType.pow)
                else:
                    old, ot, value = operation_str.split(' ')
                    monkey_props['operation'] = Operation(OperationType(ot), int(value))

            if clean_line.startswith('Test:'):
                divisible_by = clean_line.lstrip('Test: divisible by ')
                monkey_props['divisible_by'] = int(divisible_by)

            if clean_line.startswith('If true:'):
                monkey_props['monkey_to_throw_on_true'] = int(clean_line.lstrip('If true: throw to monkey '))

            if clean_line.startswith('If false:'):
                monkey_props['monkey_to_throw_on_false'] = int(clean_line.lstrip('If false: throw to monkey '))

            if all(field in monkey_props for field in Monke.__dataclass_fields__.keys() if field != 'inspected_items'):
                new_monke = Monke(**monkey_props)
                monkeys[new_monke.index] = new_monke

        return monkeys


class KeepAway:
    def __init__(self, monkeys: Dict[int, Monke], divisible: int):
        self.divisible = divisible
        self.monkeys = monkeys

    def round(self):
        for index, monke in self.monkeys.items():
            items_thrown = monke.turn(divisible)

            for monkey_index, item in items_thrown:
                self.monkeys[monkey_index].receive(item)

    def play(self, rounds: int):
        for i in range(1, rounds+1):
            print(f'Round: {i} of {rounds}')
            self.round()


if __name__ == "__main__":

    monkeys = load_initial_monkeys('input.txt')

    divisible = prod(monke.divisible_by for monke in monkeys.values())

    game = KeepAway(monkeys, divisible)
    game.play(10000)

    inspected_by_monke = [monke.inspected_items for index, monke in monkeys.items()]
    inspected_by_monke.sort()
    monke_business = inspected_by_monke[-1] * inspected_by_monke[-2]
    print(f'Monke Busssiness is {monke_business}')