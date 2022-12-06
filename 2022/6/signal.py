from dataclasses import dataclass, field
from functools import cached_property
from typing import Optional, List


@dataclass
class Group:
    index: int
    stream: str

    def is_start_marker(self):
        return len(list(self.stream)) == len(set(self.stream))

    def __lt__(self, other):
        return self.index < other.index


@dataclass
class Signal:
    stream: str

    @cached_property
    def packet_groups(self):
        groups = []
        for group in self.packet_groups_generator():
            groups.append(group)
        return groups

    @cached_property
    def message_groups(self):
        groups = []
        for group in self.message_groups_generator():
            groups.append(group)
        return groups

    @property
    def packet_starting_group(self):
        groups_with_markers = list(filter(lambda group: group.is_start_marker(), self.packet_groups))
        return min(groups_with_markers)

    @property
    def message_starting_group(self):
        groups_with_markers = list(filter(lambda group: group.is_start_marker(), self.message_groups))
        return min(groups_with_markers)

    def packet_groups_generator(self):
        for i in range(len(self.stream)):
            group_stream = self.stream[i-4:i]
            if group_stream:
                yield Group(i, group_stream)

    def message_groups_generator(self):
        for i in range(len(self.stream)):
            group_stream = self.stream[i-14:i]
            if group_stream:
                yield Group(i, group_stream)


def load_stream(file_name: str) -> str:
    stream = ''
    with open(file_name) as file:
        for line in file.readlines():
            stream += line.rstrip('\n')
    return stream


stream = load_stream('input.txt')




signal = Signal(stream)
print(signal.packet_starting_group)
print(signal.message_starting_group)