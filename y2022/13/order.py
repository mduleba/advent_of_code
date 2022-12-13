from __future__ import annotations

from dataclasses import dataclass
from ast import literal_eval
from typing import List, Tuple, Iterable

from y2022.helpers import load_file


def load_signals(get_array_method=literal_eval):
    pairs: List[Tuple] = []
    without_breaks = [line for line in load_file() if line]
    for pair_start in range(0, len(without_breaks), 2):
        packet_1 = without_breaks[pair_start]
        packet_2 = without_breaks[pair_start+1]
        pairs.append((get_array_method(packet_1), get_array_method(packet_2)))

    return pairs


assert len(load_signals()) * 3 - 1 == 449


class Packet:
    value: [int, list]

    def __init__(self, value: [int, list]):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        if not isinstance(other, Packet):
            raise Exception('Comparing different types')

        match self.value, other.value:
            case int(), int():
                return self.value < other.value
            case int(), list():
                return Packet([self.value]) < other
            case list(), int():
                return self < Packet([other.value])
            case list(), list():
                other_iter = iter(other.value)
                for element in self.value:
                    try:
                        other_item = Packet(next(other_iter))
                    except StopIteration:
                        return False

                    item = Packet(element)
                    if item == other_item:
                        continue
                    else:
                        return item < other_item

                return len(self.value) < len(other.value)


assert Packet([1, 1, 3, 1, 1]) < Packet([1, 1, 5, 1, 1])
assert Packet([[1], [2, 3, 4]]) < Packet([[1], 4])
assert not Packet([9]) < Packet([[8, 7, 6]])
assert Packet([[4, 4], 4, 4]) < Packet([[4, 4], 4, 4, 4])
assert not Packet([7, 7, 7, 7]) < Packet([7, 7, 7])
assert Packet([]) < Packet([3])
assert not Packet([[[]]]) < Packet([[]])
assert not Packet([1, [2, [3, [4, [5, 6, 7]]]], 8, 9]) < Packet([1, [2, [3, [4, [5, 6, 0]]]], 8, 9])

assert Packet([[1, 4], 8, 10, 6]) < Packet([8, 3, [0, 8, 4, 4]])
assert not Packet([8, [[2, 6, 0, 9], [4, 9, 5, 5, 3], [8], 8, 3], [1]]) < Packet([[[8], 1, [1, 1, 3, 5, 1], [0, 3]], [], 4, 0, 5])


def check_signal(signals: List[Tuple]):
    right_signal_indexes = []

    for index, signals in enumerate(signals, start=1):
        packet_1 = Packet(signals[0])
        packet_2 = Packet(signals[1])
        if packet_1 < packet_2:
            right_signal_indexes.append(index)

    return right_signal_indexes


if __name__ == '__main__':
    signals = load_signals()

    right_signal_indexes = check_signal(signals)
    print(f'Sum: {sum(right_signal_indexes)}')
