from __future__ import annotations
import itertools
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import List, Tuple, Dict, Set, Optional
import re
from y2022.helpers import load_file


class Mineral(Enum):
    ore = 'ore'
    clay = 'clay'
    obsidian = 'obsidian'
    geode = 'geode'


def load_blueprints(file_name):
    blueprints = []
    blueprint_pattern = r'Blueprint (?P<index>\d*): ' \
                        r'Each ore robot costs (?P<ore_ore_cost>\d*) ore. ' \
                        r'Each clay robot costs (?P<clay_ore_cost>\d*) ore. ' \
                        r'Each obsidian robot costs (?P<obsidian_ore_cost>\d*) ore and (?P<obsidian_clay_cost>\d*) clay. ' \
                        r'Each geode robot costs (?P<geode_ore_cost>\d*) ore and (?P<geode_obsidian_cost>\d*) obsidian.'

    for line in load_file(file_name):
        if match := re.match(blueprint_pattern, line):
            # index = int(match.group('index'))
            ore_robot = {Mineral.ore: int(match.group('ore_ore_cost'))}
            clay_robot = {Mineral.ore: int(match.group('clay_ore_cost'))}
            obsidian_robot = {
                Mineral.ore: int(match.group('obsidian_ore_cost')),
                Mineral.clay: int(match.group('obsidian_clay_cost'))
            }
            geode_robot = {
                Mineral.ore: int(match.group('geode_ore_cost')),
                Mineral.obsidian: int(match.group('geode_obsidian_cost'))
            }
            blueprint = {Mineral.ore: ore_robot, Mineral.clay: clay_robot, Mineral.obsidian: obsidian_robot, Mineral.geode: geode_robot}
            blueprints.append(blueprint)
    return blueprints
