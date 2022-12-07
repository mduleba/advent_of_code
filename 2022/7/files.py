import abc
from dataclasses import dataclass, field
from functools import cached_property
from typing import List


class FileInterface:
    def __init__(self, name: str):
        self.name = name


class File(FileInterface):
    def __init__(self, size: int, *args):
        self.size = size
        super().__init__(*args)


class Folder(FileInterface):
    def __init__(self, *args):
        super().__init__(*args)
        self.files: List[FileInterface] = []

    @property
    def size(self):
        return sum(file.size for file in self.files)


@dataclass
class Command:
    pass


@dataclass
class CD(Command):
    destination: str


@dataclass
class LS(Command):
    result: List[FileInterface] = field(default_factory=list)


class CommandLine:
    line: str

    DEFINED_TYPES = {
        '$ cd': CD,
        '$ ls': LS,
        'dir': Folder
    }
    DEFAULT_TYPE = File

    def __new__(cls, line):
        cls.line = line
        return cls.get_command()

    @classmethod
    def get_arguments(cls, prefix: str = None) -> List[str]:
        line = cls.line.lstrip(prefix)

        return [arg for arg in line.split(' ') if arg]

    @classmethod
    def get_command(cls):
        for prefix, type in cls.DEFINED_TYPES.items():
            if cls.line.startswith(prefix):
                args = cls.get_arguments(prefix)
                return type(*args)
        return cls.DEFAULT_TYPE(*cls.get_arguments())


class OS:

    def __init__(self, file_with_commands):
        self.input_file = file_with_commands
        self.current_folder = Folder('/')

    @cached_property
    def file(self):
        return open(self.input_file, 'r')

    @property
    def lines(self):
        for line in self.file.readlines():
            command = line.rstrip('\n')
            yield command

    def process(self):
        for line in self.lines:
            commandline = CommandLine(line)

            if isinstance(commandline, CD):
                pass

            if isinstance(commandline, LS):
                pass


os = OS('input.txt')
os.process()