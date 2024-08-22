import numpy as np
from enum import Enum
from itertools import combinations

# Begin original code
# Number strategies in order to avoid errors in main
class Player(Enum):
    ALLC = 0
    ALLD = 1
    TFT = 2
    GRIM = 3
    PROTEGO = 4
    HYPOCRITE = 5
    SAVIOUR = 6

class Game:
    # This includes round 0 which is the non-playable endowment round
    total_rounds = 10
    group_size = 5
    endowment = 20
    # 0 = mean mode (no perfect information), 1 = median mode (perfect information)
    mode = 0
    # 2D-array
    fixture = np.array(list(combinations([Player.value for Player in Player], group_size)))
    
    # 3D-array
    payouts = np.tile(fixture, (total_rounds, 1, 1)).astype(float)
    # 2D-array
    payins = np.arange(total_rounds*fixture.shape[0]).reshape(total_rounds,fixture.shape[0]).astype(float)

    @classmethod
    def reset_accounts(cls):
        cls.payouts[:,:,:] = 0
        cls.payins[:,:] = 0
        cls.payins[0] = cls.endowment
        return

class Current:
    # Current.round must start from 1! Round 0 is not played
    round = 1
    group = 0

class Bank:
    # modes: 0 = multiply by banker, 1 = bowles2011, 2 = fehr2002
    mode = 0
    bankerx = 2
    
    # This gives sum after banking. Not yet divided and credited.
    @classmethod
    def pool(cls):
        if cls.mode == 0:
            if cls.bankerx < Game.group_size:
                return Game.payouts[Current.round, Current.group, :].sum() * cls.bankerx
            else:
                raise TypeError("bankerx must be less than the group size for this mode")
        elif cls.mode == 1:
            return Game.payouts[Current.round, Current.group, :].sum() * (1 + cls.bankerx)
        elif cls.mode == 2:
            if cls.bankerx < 1:
                return Game.payouts[Current.group, :, Current.round].sum() * cls.bankerx * Game.group_size
            else:
                raise TypeError("bankerx must be less than 1 for this mode")
        else:
            raise TypeError("Unrecognised operation")

    # This credits the correct amount into every pay-in account
    @classmethod
    def credits(cls):
        Game.payins[Current.round, Current.group] = Bank.pool() / Game.group_size
        return