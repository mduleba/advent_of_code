from __future__ import annotations

import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Optional, List


class CommandType(Enum):
    NOOP = 'noop'
    ADDX = 'addx'

    @classmethod
    def cycles_needed(cls):
        return {
            cls.NOOP: 1,
            cls.ADDX: 2
        }

    @property
    def cycles(self):
        return self.cycles_needed()[self]


@dataclass
class Command:
    type: CommandType
    value: Optional[int] = field(default=None)
    start_cycle: int = field(default=None)

    unique: object = field(init=False)

    def __post_init__(self):
        self.unique = object()

    def execute(self, device: Device):
        if self.type == CommandType.NOOP:
            pass

        if self.type == CommandType.ADDX:
            device.register_X += self.value

    @property
    def execute_cycle(self):
        return self.start_cycle + self.type.cycles


def load_commands(file_name):
    commands = []

    with open(file_name) as file:
        for line in file.readlines():
            clean_line = line.rstrip('\n')
            splitted = clean_line.split(' ')
            ct = CommandType(splitted[0])
            if len(splitted) > 1:
                commands.append(Command(ct, int(splitted[1])))
            else:
                commands.append(Command(ct))
    return commands


class CRT:
    width: int = 40
    lines: int = 6

    def __init__(self):
        self.rows = [[] for i in range(self.lines)]

    @property
    def current_row(self):
        for row in self.rows:
            if len(row) < self.width:
                return row

    def receive_signal(self, lit: bool):
        if lit:
            self.current_row.append('#')
        else:
            self.current_row.append('.')

    def show(self):
        for row in self.rows:
            print(''.join(row))


class Device:
    cycles_to_log = [20, 60, 100, 140, 180, 220]

    def __init__(self, crt: CRT):
        self.crt = crt

        self.cycle: int = 1
        self.register_X: int = 1

        self.commands: List[Command] = []
        self.waiting_command: Optional[Command] = None

        self.logs: List[Device] = []

    @property
    def sprite(self):
        return self.register_X, self.register_X+1, self.register_X+2

    @property
    def signal_str(self):
        return self.cycle * self.register_X

    def load_commands(self, commands: List[Command]):
        self.commands += commands

    def execute(self):
        if self.waiting_command.execute_cycle == self.cycle:
            self.waiting_command.execute(self)
            self.waiting_command = None

    def send_signal(self):
        lit = self.cycle % 40 in list(self.sprite)
        self.crt.receive_signal(lit)

    def run(self):
        while True:
            self.log()
            self.send_signal()
            if not self.waiting_command:
                command = self.commands[0]
                command.start_cycle = self.cycle
                self.waiting_command = command
                self.commands.remove(command)

            self.cycle += 1
            self.execute()

            if not self.commands and not self.waiting_command:
                break

    def log(self):
        if self.cycle in self.cycles_to_log:
            self.logs.append(copy.deepcopy(self))

    def log_signal_str_sum(self):
        return sum(log.signal_str for log in self.logs)


crt = CRT()
device = Device(crt)
commands = load_commands('input.txt')

device.load_commands(commands)
device.run()

crt.show()
