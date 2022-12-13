from __future__ import annotations
from dataclasses import dataclass, field
from functools import cached_property
from typing import List, Iterable


@dataclass
class Tree:
    height: int
    unique_object: object
    _scenic_score: int = 1

    @property
    def scenic_score(self):
        return self._scenic_score

    @scenic_score.setter
    def scenic_score(self, value):
        self._scenic_score = self._scenic_score * value

    def __str__(self):
        return f'T{self.height}'

    def __lt__(self, other):
        return self.height < other.height

    def __gt__(self, other: Tree):
        return self.height > other.height

    @classmethod
    def create_unique_tree(cls, height: int):
        return cls(height, object())

    def __eq__(self, other: Tree):
        return self.unique_object == other.unique_object


@dataclass
class TreeSequence:
    index: int
    trees: List[Tree] = field(default_factory=list)

    @cached_property
    def number(self):
        return len(self.trees)

    def tree_scenic_score(self, tree: Tree):
        tree_index = self.trees.index(tree)
        l_score = 0
        for i in reversed(range(tree_index)):
            l_score += 1
            if tree > self.trees[i]:
                continue
            else:
                break

        r_score = 0
        for j in range(tree_index+1, self.number):
            r_score += 1
            if tree > self.trees[j]:
                continue
            else:
                break

        l_score = 1 if l_score == 0 else l_score
        r_score = 1 if r_score == 0 else r_score
        return l_score * r_score

    def visible_trees(self, trees: Iterable[Tree]):
        biggest_height = -1
        visible = []
        for tree in trees:
            if tree.height > biggest_height:
                biggest_height = tree.height
                visible.append(tree)

        return visible

    def visible_from_left(self):
        return self.visible_trees(self.trees)

    def visible_from_right(self):
        return self.visible_trees(reversed(self.trees))

    def visible_from_outside(self):
        unique = []

        for tree in self.visible_from_left():
            if tree not in unique:
                unique.append(tree)

        for tree in self.visible_from_right():
            if not tree in unique:
                unique.append(tree)

        return unique

    def __eq__(self, other):
        return self.index == other.index and self.__class__ == other.__class__


@dataclass
class Col(TreeSequence):
    pass


@dataclass
class Row(TreeSequence):
    pass


@dataclass
class TreeSchool:
    cols: List[Col] = field(default_factory=list)
    rows: List[Row] = field(default_factory=list)
    trees: List[Tree] = field(default_factory=list)

    def visible_from_outside(self):
        visible_from_outside = []
        for col in self.cols:
            visible_from_outside += col.visible_from_outside()

        for row in self.rows:
            visible_from_outside += row.visible_from_outside()

        unique = []
        for tree in visible_from_outside:
            if tree not in unique:
                unique.append(tree)

        return unique

    def compute_trees_scenic_scores(self):
        for col in self.cols:
            for tree in col.trees:
                tree.scenic_score = col.tree_scenic_score(tree)

        for row in self.rows:
            for tree in row.trees:
                tree.scenic_score = row.tree_scenic_score(tree)


def load_trees(file_name):
    tree_school = TreeSchool()
    with open(file_name) as file:

        row_i = 0
        for line in file.readlines():
            row_i += 1

            clean_line = line.rstrip('\n')

            row = Row(row_i)

            tree_school.rows.append(row)
            if not tree_school.cols:
                tree_school.cols = [Col(i) for i in range(1, len(clean_line)+1)]

            for i in range(len(clean_line)):
                height = int(clean_line[i])
                tree = Tree.create_unique_tree(height)

                tree_school.trees.append(tree)
                row.trees.append(tree)
                col = tree_school.cols[i]
                col.trees.append(tree)

    return tree_school


tree_school = load_trees('input.txt')
tree_school.compute_trees_scenic_scores()

print(max(tree.scenic_score for tree in tree_school.trees))



