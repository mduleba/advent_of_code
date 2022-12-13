from enum import Enum


class Choices(Enum):
    rock = 'A'
    papper = 'B'
    scissors = 'C'

    @classmethod
    def points_by_choice(cls):
        return {
            cls.rock: 1,
            cls.papper: 2,
            cls.scissors: 3
        }

    @property
    def points(self):
        return self.points_by_choice()[self]

    def moves_to_win(self):
        return {
            'X': self.beats[self],
            'Y': self,
            'Z': self.loses[self]
        }

    def move_to_win(self, move):
        return self.moves_to_win()[move]

    @property
    def beats(self):
        return {
            self.rock: self.scissors,
            self.scissors: self.papper,
            self.papper: self.rock
        }

    @property
    def loses(self):
        return {
            self.scissors: self.rock,
            self.papper: self.scissors,
            self.rock: self.papper
        }

    def __gt__(self, other):
        return self.beats[self] == other

    def __lt__(self, other):
        return self.beats[other] == self


def points_counter(player_1_move: str, player_2_move: str):
    player_2_choice = Choices(player_2_move)
    player_1_choice = player_2_choice.move_to_win(player_1_move)

    if player_1_choice > player_2_choice:
        points_for_battle = 6
    elif player_1_choice == player_2_choice:
        points_for_battle = 3
    else:
        points_for_battle = 0

    return player_1_choice.points + points_for_battle


assert points_counter('Y', 'A') == 4
assert points_counter('X', 'B') == 1
assert points_counter('Z', 'C') == 7

assert points_counter('Y', 'A') + points_counter('X', 'B') + points_counter('Z', 'C') == 12


with open('input.txt') as file, open('output.txt', 'w') as file2:
    points_sum = 0
    round = 1
    for line in file.readlines():
        theirmove, mymove = line.split(' ')
        mymove = mymove.rstrip('\n')

        file2.writelines(f'{points_counter(mymove, theirmove)}\n')
        points_sum += points_counter(mymove, theirmove)

        round += 1



