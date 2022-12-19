from __future__ import annotations

import copy
import itertools
import random
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import List, Tuple, Dict, Set, Optional
import re
from y2022.helpers import load_file


class Action(Enum):
    wait = 'wait'
    build_ore_robot = 'ore'
    build_clay_robot = 'clay'
    build_obsidian_robot = 'obsidian'
    build_geode_robot = 'geode'

    @classmethod
    def choices(cls):
        return [cls.wait, cls.build_geode_robot, cls.build_obsidian_robot, cls.build_clay_robot, cls.build_ore_robot]


class Mineral(Enum):
    ore = 'ore'
    clay = 'clay'
    obsidian = 'obsidian'
    geode = 'geode'

    @classmethod
    def scores(cls):
        return {
            cls.ore: 0,
            cls.clay: 0,
            cls.obsidian: 0,
            cls.geode: 1
        }

    @property
    def score(self):
        return self.scores()[self]


class Robot:
    produces: Mineral

    def __init__(self, cost: Optional[Dict[Mineral, int]]):
        self.cost = cost


class OreRobot(Robot):
    produces = Mineral.ore

    @classmethod
    def get_default(cls):
        return cls(None)


class ClayRobot(Robot):
    produces = Mineral.clay


class ObsidianRobot(Robot):
    produces = Mineral.obsidian


class GeodeRobot(Robot):
    produces = Mineral.geode


class Blueprint:

    def __init__(self, index: int, robots: Dict[Mineral, Robot]):
        self.index = index
        self.robots = robots

    def robot(self, mineral: Mineral):
        return self.robots[mineral]


def load_blueprints(file_name):
    blueprints = []
    blueprint_pattern = r'Blueprint (?P<index>\d*): ' \
                        r'Each ore robot costs (?P<ore_ore_cost>\d*) ore. ' \
                        r'Each clay robot costs (?P<clay_ore_cost>\d*) ore. ' \
                        r'Each obsidian robot costs (?P<obsidian_ore_cost>\d*) ore and (?P<obsidian_clay_cost>\d*) clay. ' \
                        r'Each geode robot costs (?P<geode_ore_cost>\d*) ore and (?P<geode_obsidian_cost>\d*) obsidian.'

    for line in load_file(file_name):
        if match := re.match(blueprint_pattern, line):
            index = int(match.group('index'))
            ore_robot = OreRobot(cost={Mineral.ore: int(match.group('ore_ore_cost'))})
            clay_robot = ClayRobot(cost={Mineral.ore: int(match.group('clay_ore_cost'))})
            obsidian_robot = ObsidianRobot(cost={
                Mineral.ore: int(match.group('obsidian_ore_cost')),
                Mineral.clay: int(match.group('obsidian_clay_cost'))
            })
            geode_robot = GeodeRobot(cost={
                Mineral.ore: int(match.group('geode_ore_cost')),
                Mineral.obsidian: int(match.group('geode_obsidian_cost'))
            })
            blueprint = Blueprint(
                index=index,
                robots={Mineral.ore: ore_robot, Mineral.clay: clay_robot, Mineral.obsidian: obsidian_robot, Mineral.geode: geode_robot}
            )
            blueprints.append(blueprint)

    return blueprints


class BuildOrder:
    time_limit = 24

    @classmethod
    def create_and_generate(cls, blueprint: Blueprint):
        instance = cls(blueprint)
        instance.generate_random()
        return instance

    def __init__(self, blueprint: Blueprint, actions: Optional[List[Action]] = None):
        self.blueprint = blueprint
        self.robots: List[Robot] = [OreRobot.get_default()]
        self.resources: Dict[Mineral, int] = {mineral: 0 for mineral in Mineral.__members__.values()}
        self.queque: Optional[Robot] = None
        self.actions = actions if actions else []

    def reset(self):
        self.robots: List[Robot] = [OreRobot.get_default()]
        self.resources: Dict[Mineral, int] = {mineral: 0 for mineral in Mineral.__members__.values()}
        self.queque: Optional[Robot] = None

    def generate_random(self):
        i = 1
        while i <= self.time_limit:
            action = random.choice(self.avaible_actions)
            self.actions.append(action)
            self.perform(action)
            self.collect()
            if self.queque:
                self.robots.append(self.queque)
                self.queque = None
            i += 1

    @property
    def fitness(self):
        return sum(mineral.score*count for mineral, count in self.resources.items())

    @cached_property
    def avaible_actions(self):
        return [action for action in Action.__members__.values()]

    def collect(self):
        for robot in self.robots:
            self.resources[robot.produces] += 1

    def can_afford(self, cost: Dict[Mineral, int]):
        return all(self.resources[mineral] >= price for mineral, price in cost.items())

    def create_robot(self, robot: Robot):
        self.resources = {mineral: self.resources[mineral] - robot.cost.get(mineral, 0) for mineral in self.resources.keys()}
        return robot

    def perform(self, action: Action):
        if action == Action.wait:
            return None
        else:
            robot = self.blueprint.robot(Mineral(action.value))
            if self.can_afford(robot.cost):
                self.queque = self.create_robot(robot)

    def play(self):
        i = 1
        action_iter = iter(self.actions)
        while i <= self.time_limit:
            action = next(action_iter)
            self.perform(action)
            self.collect()
            if self.queque:
                self.robots.append(self.queque)
                self.queque = None
            i += 1

    def __lt__(self, other):
        return self.fitness > other.fitness


class GeneticBuildOrder:
    population_size = 1000
    mating_occurances = 10
    generations_count = 1000

    mutation_chance = 5

    def __init__(self, blueprint: Blueprint):
        self.blueprint = blueprint
        self.population: List[BuildOrder] = []

    def populate(self):
        self.population = [BuildOrder.create_and_generate(self.blueprint) for i in range(self.population_size)]
        self.population.sort()

    def crossover(self, father, mother) -> BuildOrder:
        i = random.randint(1, BuildOrder.time_limit)
        new_actions = father.actions[0:i] + mother.actions[i:BuildOrder.time_limit]
        return BuildOrder(self.blueprint, new_actions)

    def sex(self):
        for occurance in range(self.mating_occurances):
            point = random.randint(1, BuildOrder.time_limit)
            father = self.population[occurance]
            mother = random.choice(self.population[0:point-1] + self.population[point:self.population_size])
            self.population[self.population_size-1-occurance] = self.crossover(father, mother)

    def mutate(self):
        instance = random.choice(self.population)
        i = random.randint(0, BuildOrder.time_limit-1)
        instance.actions[i] = random.choice(Action.choices())

    def reset(self):
        for order in self.population:
            order.reset()

    def generate(self):
        self.populate()
        self.sex()
        self.population.sort()

        for i in range(self.generations_count):
            print(f'{i+1}/{self.generations_count}')
            self.reset()
            for instance in self.population:
                instance.play()
            self.population.sort()
            self.sex()

            if random.randint(0, 100) < self.mutation_chance:
                self.mutate()


if __name__ == '__main__':
    test_blueprints = load_blueprints('test_input.txt')

    genetic = GeneticBuildOrder(test_blueprints[0])
    genetic.generate()
