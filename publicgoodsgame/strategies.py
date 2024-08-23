import random

import numpy as np
from publicgoodsgame.game import Player
from publicgoodsgame.game import Game
from publicgoodsgame.game import Current

class Strategy:

    @classmethod
    def isingame(cls):
        if cls.name in [s.name for s in Player]:
            return True
        else:
            return False

    @classmethod
    def isingroup(cls):
        if cls.isingame():
            if Player[cls.name].value in Game.fixture[Current.group, :]:
                return True
            else:
                return False
        else:
            raise TypeError("Strategy is not in game")

    @classmethod
    def playerpos(cls):
        if cls.isingroup():
            return np.where(Game.fixture[Current.group] == Player[cls.name].value)[0][0]
        else:
            raise TypeError("Strategy is not in group")

    @classmethod
    def isnotbroke(cls):
        if cls.acc_balance_player() > 0:
            return True
        else:
            return False

    @classmethod
    def defectedbefore(cls):
        # Checks if own player has given nothing before in Current.group
        if np.isin(Game.payouts[1:Current.round, Current.group, cls.playerpos()], 0).any():
            return True
        else:
            return False

    @classmethod
    def acc_balance_player(cls):
        if cls.isingroup():
            _payin_sum = Game.payins[:(Current.round), Current.group].sum()
            _payout_sum = Game.payouts[:(Current.round), Current.group, cls.playerpos()].sum()
            return _payin_sum - _payout_sum
        else:
            raise TypeError("Strategy is not in group")

    # Returns 1D-array of all players in the current round
    @classmethod
    def acc_balance_all(cls):
        _payin_1d = Game.payins[:(Current.round+1), Current.group]
        _payout_2d = Game.payouts[:(Current.round+1), Current.group, :]
        _all_accounts = (np.vstack(_payin_1d) - _payout_2d).sum(axis=0)
        return _all_accounts

    # Returns 1D-array showing each player's account in round-2, excluding own player
    @classmethod
    def acc_balance_prev(cls):
        if cls.isingroup():
            if Current.round == 1:
                return np.full(Game.group_size-1, Game.endowment)
            else:
                # Current.round-1 because at round r, players' spending in round-1 is based on their balance at the round-2
                _payin_1d = Game.payins[:(Current.round - 1), Current.group]
                _payout_2d = Game.payouts[:(Current.round - 1), Current.group, :]
                _all_accounts = (np.vstack(_payin_1d) - _payout_2d).sum(axis=0)
                _mask = np.ones_like(_all_accounts, dtype=bool)
                _mask[cls.playerpos()] = False
                return _all_accounts[_mask]
        else:
            raise TypeError("Strategy is not in group")

    @classmethod
    def avg_acc_balance_prev(cls):
        if cls.isingroup():
            if Game.mode == 0:
                return np.mean(cls.acc_balance_prev())
            elif Game.mode == 1:
                return np.median(cls.acc_balance_prev())
            else:
                raise TypeError("Unrecognised game mode. Check class variables of Game.")

    # Returns single-valued sum of payouts, excluding own player
    @classmethod
    def sum_payouts_prev(cls):
        _prev_round_slice = Game.payouts[Current.round - 1, Current.group, :]
        _mask = np.ones_like(_prev_round_slice, dtype=bool)
        _mask[cls.playerpos()] = False
        _slice_excluding_player = _prev_round_slice[_mask]
        return _slice_excluding_player.sum()

    @classmethod
    def avg_payouts_prev(cls):
        if Game.mode == 0:
            return np.mean(cls.sum_payouts_prev())
        elif Game.mode == 1:
            return np.median(cls.sum_payouts_prev())
        else:
            raise TypeError("Unrecognised game mode. Check class variables of Game.")

    # Returns array showing percentage of means given away
    @classmethod
    def payouts_vs_accounts(cls):
        # cls.isnotbroke() ensures no division by 0
        if cls.isingroup() and cls.isnotbroke():
            _payout_1d = Game.payouts[Current.round - 1, Current.group, :]
            _mask = np.ones_like(_payout_1d, dtype=bool)
            _mask[cls.playerpos()] = False
            _payout_1d_noself = _payout_1d[_mask]
            return _payout_1d_noself / cls.acc_balance_prev() * 100
        else:
            raise TypeError("Strategy is not in group or player is broke")

class ALLC(Strategy):

    # "Always cooperate" is interpreted as always giving a fixed amount at every round, regardless of others' actions.
    # percentage = percentage of own means to give away
    
    name = "ALLC"
    percentage = 100

    @classmethod
    def gives(cls):
        if cls.isnotbroke():
            Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.percentage / 100 * cls.acc_balance_player()
            return
        else:
            pass

class ALLD(Strategy):

    # Always gives 0

    name = "ALLD"
    
    @classmethod
    def gives(cls):
        Game.payouts[Current.round, Current.group, cls.playerpos()] = 0
        return

class TFT(Strategy):

    # TFT gives whatever the average player gave in the previous round. If that's more than what it has, it gives everything it has.

    name = "TFT"
    # As a communist, TFT will take into account the means of other players.
    iscommunist = False
    # What percentage of endowment to give in first round. Default is 100.
    first_coop = 100
    
    @classmethod
    def gives(cls):
        if cls.isnotbroke():
            if Current.round == 1:
                # Cooperates first
                Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.first_coop / 100 * Game.endowment
                return
            elif cls.iscommunist:
                Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.avg_payouts_prev() / cls.avg_acc_balance_prev() * cls.acc_balance_player()
                return
            elif cls.avg_payouts_prev() > cls.acc_balance_player():
                Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.acc_balance_player()
                return
            else:
                Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.avg_payouts_prev()
                return
        else:
            pass

class PROTEGO(Strategy):
    
    # PROTEGO is Latin for 'I protect' and a shield charm in the wizarding world. When other players' behaviour falls below a certain standard, it protects itself by giving nothing. Else it plays TFT.
    # If communist, standard is measured according to other players' means. Else measured against own player's contribution

    name = "PROTEGO"
    iscommunist = False
    standard = 80
    first_coop = 100

    @classmethod
    def gives(cls):
        if cls.isnotbroke():
            if Current.round == 1:
                Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.first_coop / 100 * Game.endowment
                return
            elif cls.iscommunist and cls.avg_payouts_prev() >= cls.standard / 100 * cls.avg_acc_balance_prev():
                Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.avg_payouts_prev() / cls.avg_acc_balance_prev() * cls.acc_balance_player()
                return
            elif not cls.iscommunist and cls.avg_acc_balance_prev() >= cls.standard / 100 * Game.payouts[Current.round -1, Current.group, cls.playerpos()]:
                if cls.avg_payouts_prev() > cls.acc_balance_player():
                    Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.acc_balance_player()
                    return
                else:
                    Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.avg_payouts_prev()
                    return
            else:
                Game.payouts[Current.round, Current.group, cls.playerpos()] = 0
                return

class GRIM(Strategy):
    
    # GRIM is like PROTEGO but defects forever following a first defection

    name = "GRIM"
    iscommunist = False
    standard = 80
    first_coop = 100
    
    @classmethod
    def gives(cls):
        if cls.isnotbroke():
            if Current.round == 1:
                Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.first_coop / 100 * Game.endowment
                return
            elif cls.iscommunist and cls.avg_payouts_prev() >= cls.standard / 100 * cls.avg_acc_balance_prev() and not cls.defectedbefore():
                Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.avg_payouts_prev() / cls.avg_acc_balance_prev() * cls.acc_balance_player()
                return
            elif not cls.iscommunist and cls.avg_acc_balance_prev() >= cls.standard / 100 * Game.payouts[Current.round -1, Current.group, cls.playerpos()] and not cls.defectedbefore():
                if cls.avg_payouts_prev() > cls.acc_balance_player():
                    Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.acc_balance_player()
                    return
                else:
                    Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.avg_payouts_prev()
                    return
            else:
                Game.payouts[Current.round, Current.group, cls.playerpos()] = 0
                return

class HYPOCRITE(Strategy):
    
    # Gives only when others meet a certain standard that it itself will not meet. This only makes sense if cls.own_coop is high enough to meet the standards of other strategies

    name = "HYPOCRITE"
    iscommunist = False
    first_coop = 80
    sub_coop = 80
    # How much more it expects of others than of itself
    buffer = 5

    @classmethod
    def gives(cls):
        if cls.isnotbroke():
            if Current.round == 1:
                # Cooperates first
                Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.first_coop / 100 * Game.endowment
                return
            elif cls.iscommunist and cls.avg_payouts_prev() >= (cls.sub_coop + cls.buffer) / 100 * cls.avg_acc_balance_prev():
                Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.sub_coop / 100 * cls.acc_balance_player()
                return
            elif not cls.iscommunist and cls.avg_payouts_prev() >= (cls.sub_coop + cls.buffer) / 100 * Game.payouts[Current.round -1, Current.group, cls.playerpos()]:
                Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.sub_coop / 100 * cls.acc_balance_player()
                return
            else:
                Game.payouts[Current.round, Current.group, cls.playerpos()] = 0
                return
        else:
            pass

class SAVIOUR(Strategy):

    # Gives more if other players are broke until it itself is broke
    
    name = "SAVIOUR"
    # This has to be less than 100 to make sense
    own_coop = 80

    @classmethod
    def gives(cls):
        if cls.isnotbroke():
            if np.size(cls.acc_balance_prev()[cls.acc_balance_prev()<0]) > 0:
                Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.acc_balance_player()
                return
            else:
                Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.own_coop / 100 * cls.acc_balance_player()
                return
        else:
            pass

class INCENDIO(Strategy):
    
    # Targets one defector but punishes all. INCENDIO is the spell that sets fire to things. INCENDIO contributes according to its own standard
    # INCENDIO requires perfect information
    
    name = "INCENDIO"
    standard = 100
    first_coop = 100

    @classmethod
    def gives(cls):
        if cls.isnotbroke():
            if Current.round == 1:
                # Cooperates first
                Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.first_coop / 100 * Game.endowment
                return
            elif np.size(cls.payouts_vs_accounts()[cls.payouts_vs_accounts() < cls.standard]) == 0:
                Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.standard / 100 * cls.acc_balance_player()
                return
            else:
                Game.payouts[Current.round, Current.group, cls.playerpos()] = cls.standard / 100 * cls.acc_balance_player()
                return
        else:
            pass

class RANDOM(Strategy):
    # Gives random float from own account
    name = "RANDOM"
    @classmethod
    def gives(cls):
        if cls.isnotbroke():
            Game.payouts[Current.round, Current.group, cls.playerpos()] = random.uniform(0,cls.acc_balance_player())
            return
        else:
            pass