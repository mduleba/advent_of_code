from __future__ import annotations

from dataclasses import dataclass
from ast import literal_eval
from typing import List, Tuple, Iterable, Optional


def load_file(file_name):
    lines = []
    with open(file_name) as file:
        for line in file.readlines():
            clean_line = line.rstrip('\n')
            lines.append(clean_line)
    return lines


def load_signals(file_name):
    pairs: List[Tuple] = []
    without_breaks = [line for line in load_file(file_name) if line]
    for pair_start in range(0, len(without_breaks), 2):
        packet_1 = without_breaks[pair_start]
        packet_2 = without_breaks[pair_start+1]
        pairs.append((literal_eval(packet_1), literal_eval(packet_2)))

    return pairs


assert len(load_signals('input.txt')) * 3 - 1 == 449


class Finish(Exception):
    def __init__(self, result: Optional[bool], *args):
        self.result = result
        super().__init__(*args)


class Packet:
    value: [int, list]

    def __init__(self, value: [int, list]):
        self.value = value

    def compare(self, left, right):
        match left, right:
            case int(), int():
                return left - right
            case int(), list():
                return self.compare([left], right)
            case list(), int():
                return self.compare(left, [right])
            case list(), list():
                for value, other_value in zip(left, right):
                    if diff := self.compare(value, other_value):
                        return diff
                return len(left) - len(right)

    def __lt__(self, other):
        if not isinstance(other, Packet):
            raise Exception('Comparing different types')

        return self.compare(self.value, other.value) < 0


assert Packet([1, 1, 3, 1, 1]) < Packet([1, 1, 5, 1, 1])
assert Packet([2, 3, 4]) < Packet(4)
assert Packet([[1], [2, 3, 4]]) < Packet([[1], 4])
assert not Packet([9]) < Packet([[8, 7, 6]])
assert Packet([[4, 4], 4, 4]) < Packet([[4, 4], 4, 4, 4])
assert not Packet([7, 7, 7, 7]) < Packet([7, 7, 7])
assert Packet([]) < Packet([3])
assert not Packet([[[]]]) < Packet([[]])
assert not Packet([1, [2, [3, [4, [5, 6, 7]]]], 8, 9]) < Packet([1, [2, [3, [4, [5, 6, 0]]]], 8, 9])

assert Packet([[1, 4], 8, 10, 6]) < Packet([8, 3, [0, 8, 4, 4]])
assert Packet([1]) < Packet([[1], 2])


@dataclass
class Pair:
    signal: Tuple

    @property
    def packet_1(self):
        return Packet(self.signal[0])

    @property
    def packet_2(self):
        return Packet(self.signal[1])

    def is_valid(self):
        return self.packet_1 < self.packet_2


def check_signal(signals: List[Tuple]):
    right_signal_indexes = []

    for index, signal in enumerate(signals, start=1):
        pair = Pair(signal)
        if pair.is_valid():
            right_signal_indexes.append(index)

    return right_signal_indexes


if __name__ == '__main__':
    signals = load_signals('input.txt')

    right_signal_indexes = check_signal(signals)
    print(f'Sum: {sum(right_signal_indexes)}')

    packets = []
    for s1, s2 in signals:
        packets.append(Packet(s1))
        packets.append(Packet(s2))

    two, six = [[2]], [[6]]
    packets += [Packet(two), Packet(six)]
    packets.sort()

    d1 = None
    d2 = None
    for i, packet in enumerate(packets, start=1):
        if packet.value == two:
            d1 = i
        if packet.value == six:
            d2 = i

    print(f'Key {d1*d2}')