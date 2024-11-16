import numpy as np
from enum import Enum
from itertools import combinations

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
    # 0 = mean stats_mode (no perfect information), 1 = median stats_mode (perfect information)
    stats_mode = 0
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