import numpy as np
from enum import Enum
from itertools import combinations


# To Do
# Make it possible for different players to play the same strategy


# tourn_no = 48
# Comment out player to exclude. Player values do not need to be in order
# Player.name = strategy, Player.value = player
# Players can change their strategy
# Model real human experiment regression
# In big groups with more cooperators with fewer hypocrites, the hypocrites can get away more easily
# Because the average becomes closer to the maximum average
# What is the percentage of hypocrites that can survive
# Frequency dependent selection
# Punishing according to different standards
# b < p.c If c is the death penalty, then it would tend to infinity. So however small the p, it would still be not worth

class Player(Enum):
    ALLC = 0
    ALLD = 1
    TFT = 2
    PROTEGO = 3
    GRIM = 4
    HYPOCRITE = 5
    SAVIOUR = 6
    INCENDIO = 7
    # RANDOM = 8


class Game:
    # This includes round 0 which is the non-playable endowment round
    total_rounds = 30
    group_size = 5
    endowment = 100
    # 0 = mean mode (no perfect information), 1 = median mode (perfect information)
    mode = 0
    # 2D-array (groups, group members)
    fixture = np.array(list(combinations([Player.value for Player in Player], group_size)))

    # 3D-array (rounds, groups, group members)
    contributions = np.tile(fixture, (total_rounds, 1, 1)).astype(float)
    # 2D-array (rounds, groups)
    winnings = np.arange(total_rounds * fixture.shape[0]).reshape(total_rounds, fixture.shape[0]).astype(float)

    @classmethod
    def reset_accounts(cls):
        cls.contributions[:, :, :] = 0
        cls.winnings[:, :] = 0
        cls.winnings[0] = cls.endowment
        return


class Current:
    # Current.round must start from 1! Round 0 is not played
    round = 1
    group = 0


class Bank:
    bankerx = 2

    # This gives sum after banking. Not yet divided and credited.
    @classmethod
    def pool(cls):
        return Game.contributions[Current.round, Current.group, :].sum() * cls.bankerx

    # This credits the correct amount into every pay-in account
    @classmethod
    def credits(cls):
        Game.winnings[Current.round, Current.group] = Bank.pool() / Game.group_size
        return