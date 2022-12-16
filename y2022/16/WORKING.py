from __future__ import annotations

import random
from collections import OrderedDict
from dataclasses import dataclass
from functools import cached_property

from typing import List, Tuple, Set, Dict
import heapq
import re
import sys

from y2022.helpers import load_file
import re


@dataclass(frozen=True)
class Valve:
    name: str
    flow_rate: int

    def __lt__(self, other):
        return False

    def __repr__(self):
        return self.name


def find_routes(leads, goal):
    q = [(0, goal)]
    path_lengths = {goal: 0}
    while q:
        cost, current = heapq.heappop(q)
        for point, point_cost in leads[current].items():
            if point not in path_lengths or cost + point_cost < path_lengths[point]:
                path_lengths[point] = cost + point_cost
                heapq.heappush(q, (cost + point_cost, point))
    return path_lengths


def find_all_routes(leads, start_valve: Valve):
    costs = {valve: find_routes(leads, valve) for valve in leads
             if valve is start_valve or valve.flow_rate}
    for valve, valve_costs in costs.items():
        costs[valve] = {x: c for x, c in valve_costs.items() if x.flow_rate}
    return costs


def run_route(costs, start_valve, valves, t):
    release = 0
    current = start_valve
    for valve in valves:
        cost = costs[current][valve] + 1
        t -= cost
        assert t > 0
        release += t * valve.flow_rate
        current = valve
    return release


def all_orders(distances, valve, todo, done, time):
    for next_valve in todo:
        cost = distances[valve][next_valve] + 1
        if cost < time:
            yield from all_orders(distances, next_valve, todo - {next_valve},
                                  done + [next_valve], time - cost)
    yield done


def load_valves(file_name):
    valves = {}
    leads = {}
    for line in load_file(file_name):
        valve_name = line[6:8]
        line = line[23:]
        rate_str, lead_to = line.split(';')
        valves[valve_name] = Valve(valve_name, int(rate_str))
        leads[valve_name] = lead_to.lstrip(' tunnels lead to valves ').split(', ')

    for valve_name, neighbours in list(leads.items()):
        del leads[valve_name]
        leads[valves[valve_name]] = {valves[neighbour]: 1 for neighbour in neighbours}

    start_valve = valves['AA']
    return start_valve, find_all_routes(leads, start_valve)


if __name__ == '__main__':
    start_valve, distances = load_valves('input.txt')
    working_valves = {valve for valve in distances if valve.flow_rate}

    p1_orders = all_orders(distances, start_valve, working_valves, [], 30)
    best_value = max(run_route(distances, start_valve, order, 30) for order in p1_orders)
    print("Part 1:", best_value)

    p2_orders = all_orders(distances, start_valve, working_valves, [], 26)
    p2_scores = [(run_route(distances, start_valve, order, 26), set(order))
                 for order in p2_orders]
    p2_scores.sort(key=lambda x: -x[0])                                                   

    best = 0
    for i, (sa, oa) in enumerate(p2_scores):
        if sa * 2 < best:
            break
        for sb, ob in p2_scores[i+1:]:
            if not oa & ob:
                score = sa + sb
                if score > best:
                    best = score
    print("Part 2:", best)