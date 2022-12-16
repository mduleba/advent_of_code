from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

from typing import List, Tuple, Set, Dict

from y2022.helpers import load_file
import re


@dataclass
class Valve:
    name: str
    flow_rate: int
    leads_to: List[str]


def load_simple_valves(file_name):
    valves = {}
    for line in load_file(file_name):
        valve_name = line[6:8]
        line = line[23:]
        rate_str, leads = line.split(';')
        leads = leads.lstrip(' tunnels lead to valves ').split(', ')
        valves[valve_name] = Valve(valve_name, int(rate_str), leads)
    return valves


class Tunnels:
    TIME_LIMIT = 30

    def __init__(self, valves: Dict[Valve]):
        self.valves = valves
        self.flow_rate = 0
        self.time = 0
        self.preassure = 0

    @cached_property
    def max_flow_rate(self):
        return sum(valve.flow_rate for valve in self.valves.values())

    @cached_property
    def max_preassure(self):
        return self.max_flow_rate * self.TIME_LIMIT

    def run_time(self):
        self.time += 1
        self.preassure += self.flow_rate


valves = load_simple_valves('input.txt')
tunnel = Tunnels(valves)





# routes = set()
#
#
# def traverse_tunnels(i: int, valve: Valve, valves: Dict[str, Valve], path: str):
#     i += 1
#     path += f'{valve.name}, '
#     for tunnel in valve.leads_to:
#         if i <= 30:
#             traverse_tunnels(i, valves[tunnel], valves, path)
#         else:
#             routes.add(path)
#
#
# for valve in valves.values():
#     traverse_tunnels(0, valve, valves, '')


