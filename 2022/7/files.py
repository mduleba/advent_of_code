from __future__ import annotations
import abc
from dataclasses import dataclass, field
from functools import cached_property
from typing import List, Set


class FileInterface:
    def __init__(self, name: str):
        self.name = name


class File(FileInterface):
    def __init__(self, size: int, *args):
        self.size = size
        super().__init__(*args)


class Folder(FileInterface):
    def __init__(self, master: Folder = None, *args):
        super().__init__(*args)
        self.master = master
        self.files: List[FileInterface] = []

    @property
    def size(self):
        return sum(file.size for file in self.files)

    def get_file_by_name(self, name: str):
        files_with_name = [file for file in self.files if file.name == name]
        if not files_with_name:
            raise ValueError(f'File with name: {name} not found')
        if len(files_with_name) > 1:
            raise ValueError(f'Multiple files found with name: {name}')
        return files_with_name[0]


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
    os: OS

    DEFINED_TYPES = {
        '$ cd': CD,
        '$ ls': LS,
        'dir': Folder
    }
    DEFAULT_TYPE = File

    def __new__(cls, os, line):
        cls.line = line
        cls.os = os
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
                if prefix == 'dir':
                   args = (cls.os.current_folder, *args)
                return type(*args)
        return cls.DEFAULT_TYPE(*cls.get_arguments())


class OS:

    def __init__(self, file_with_commands):
        self.input_file = file_with_commands
        self.current_folder = Folder(None, '/')

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
            commandline = CommandLine(self, line)

            if isinstance(commandline, CD):
                if commandline.destination == '..':
                    self.current_folder = self.current_folder.master
                else:
                    self.current_folder = self.current_folder.get_file_by_name(commandline.destination)

            if isinstance(commandline, LS):
                pass


os = OS('input.txt')
os.process()