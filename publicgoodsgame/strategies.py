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
        if np.isin(Game.contributions[1:Current.round, Current.group, cls.playerpos()], 0).any():
            return True
        else:
            return False

    @classmethod
    def acc_balance_player(cls):
        if cls.isingroup():
            _payin_sum = Game.winnings[:(Current.round), Current.group].sum()
            _payout_sum = Game.contributions[:(Current.round), Current.group, cls.playerpos()].sum()
            return _payin_sum - _payout_sum
        else:
            raise TypeError("Strategy is not in group")

    # Returns 1D-array of all players in the current round
    @classmethod
    def acc_balance_all(cls):
        _payin_1d = Game.winnings[:(Current.round + 1), Current.group]
        _payout_2d = Game.contributions[:(Current.round + 1), Current.group, :]
        _all_accounts = (np.vstack(_payin_1d) - _payout_2d).sum(axis=0)
        return _all_accounts

    # Returns 1D-array showing each player's account in round-2, excluding own player
    @classmethod
    def acc_balance_prev(cls):
        if cls.isingroup():
            if Current.round == 1:
                return np.full(Game.group_size - 1, Game.endowment)
            else:
                # Current.round-1 because at round r, players' spending in round-1 is based on their balance at round-2
                _payin_1d = Game.winnings[:(Current.round - 1), Current.group]
                _payout_2d = Game.contributions[:(Current.round - 1), Current.group, :]
                _all_accounts = (np.vstack(_payin_1d) - _payout_2d).sum(axis=0)
                _mask = np.ones_like(_all_accounts, dtype=bool)
                _mask[cls.playerpos()] = False
                return _all_accounts[_mask]
        else:
            raise TypeError("Strategy is not in group")

    @classmethod
    def acc_balance_current(cls):
        if cls.isingroup():
            if Current.round == 1:
                return np.full(Game.group_size - 1, Game.endowment)
            else:
                _payin_1d = Game.winnings[:(Current.round), Current.group]
                _payout_2d = Game.contributions[:(Current.round), Current.group, :]
                _all_accounts = (np.vstack(_payin_1d) - _payout_2d).sum(axis=0)
                _mask = np.ones_like(_all_accounts, dtype=bool)
                _mask[cls.playerpos()] = False
                return _all_accounts[_mask]
        else:
            raise TypeError("Strategy is not in group")

    @classmethod
    def avg_acc_balance_prev(cls):
        if cls.isingroup():
            if Game.stats_mode == 0:
                return np.mean(cls.acc_balance_prev())
            elif Game.stats_mode == 1:
                return np.median(cls.acc_balance_prev())
            else:
                raise TypeError("Unrecognised game stats_mode. Check class variables of Game.")


    # Returns single-valued sum of contributions, excluding own player
    @classmethod
    def sum_payouts_prev(cls):
        _prev_round_slice = Game.contributions[Current.round - 1, Current.group, :]
        _mask = np.ones_like(_prev_round_slice, dtype=bool)
        _mask[cls.playerpos()] = False
        _slice_excluding_player = _prev_round_slice[_mask]
        return _slice_excluding_player.sum()

    @classmethod
    def avg_contributions_prev(cls):
        if Game.stats_mode == 0:
            return np.mean(cls.sum_payouts_prev())
        elif Game.stats_mode == 1:
            return np.median(cls.sum_payouts_prev())
        else:
            raise TypeError("Unrecognised game stats_mode. Check class variables of Game.")

    # Returns array showing percentage of means given away
    @classmethod
    def payouts_vs_accounts(cls):
        # cls.isnotbroke() ensures no division by 0
        if cls.isingroup() and cls.isnotbroke():
            _payout_1d = Game.contributions[Current.round - 1, Current.group, :]
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

    @classmethod
    def gives(cls):
        if cls.isnotbroke():
            Game.contributions[
                Current.round, Current.group, cls.playerpos()] = cls.acc_balance_player()
            return
        else:
            pass


class ALLD(Strategy):
    # Always gives 0

    name = "ALLD"

    @classmethod
    def gives(cls):
        Game.contributions[Current.round, Current.group, cls.playerpos()] = 0
        return


class TFT(Strategy):
    # TFT gives whatever the average player gave in the previous round. If that's more than what it has, it gives everything it has.

    name = "TFT"
    # As a communist, TFT will take into account the means of other players.
    # What percentage of endowment to give in first round. Default is 100.
    first_coop = 1

    @classmethod
    def gives(cls):
        if cls.isnotbroke():
            if Current.round == 1:
                # Cooperates first
                Game.contributions[
                    Current.round, Current.group, cls.playerpos()] = cls.first_coop * Game.endowment
                return
            else:
                Game.contributions[
                    Current.round, Current.group, cls.playerpos()] = cls.avg_contributions_prev() / cls.avg_acc_balance_prev() * cls.acc_balance_player()
                return
        else:
            pass


class PROTEGO(Strategy):
    # PROTEGO is Latin for 'I protect' and a shield charm in the wizarding world. When other players' behaviour falls below a certain standard, it protects itself by giving nothing. Else it plays TFT.
    # If communist, standard is measured according to other players' means. Else measured against own player's contribution

    name = "PROTEGO"
    standard = 0.8
    first_coop = 1

    @classmethod
    def gives(cls):
        if cls.isnotbroke():
            if Current.round == 1:
                Game.contributions[
                    Current.round, Current.group, cls.playerpos()] = cls.first_coop * Game.endowment
                return
            elif cls.avg_contributions_prev() >= cls.standard * cls.avg_acc_balance_prev():
                Game.contributions[
                    Current.round, Current.group, cls.playerpos()] = cls.avg_contributions_prev() / cls.avg_acc_balance_prev() * cls.acc_balance_player()
                return
            else:
                Game.contributions[Current.round, Current.group, cls.playerpos()] = 0
                return


class GRIM(Strategy):
    # GRIM is like PROTEGO but defects forever following a first defection

    name = "GRIM"
    standard = 0.8
    first_coop = 1

    @classmethod
    def gives(cls):
        if cls.isnotbroke():
            if Current.round == 1:
                Game.contributions[
                    Current.round, Current.group, cls.playerpos()] = cls.first_coop * Game.endowment
                return
            elif cls.avg_contributions_prev() >= cls.standard * cls.avg_acc_balance_prev() and not cls.defectedbefore():
                Game.contributions[Current.round, Current.group, cls.playerpos()] = cls.avg_contributions_prev() / cls.avg_acc_balance_prev() * cls.acc_balance_player()
                return
            else:
                Game.contributions[Current.round, Current.group, cls.playerpos()] = 0
                return


class HYPOCRITE(Strategy):
    # Gives only when others meet a certain standard that it itself will not meet. This only makes sense if cls.own_coop is high enough to meet the standards of other strategies

    name = "HYPOCRITE"
    first_coop = 0.8
    standard = 0.9
    # How much more it expects of others than of itself
    buffer = 0.1

    @classmethod
    def gives(cls):
        if cls.isnotbroke():
            if Current.round == 1:
                # Cooperates first
                Game.contributions[
                    Current.round, Current.group, cls.playerpos()] = cls.first_coop * Game.endowment
                return
            elif cls.avg_contributions_prev() >= cls.standard * cls.avg_acc_balance_prev():
                Game.contributions[Current.round, Current.group, cls.playerpos()] = (cls.standard - cls.buffer) * cls.acc_balance_player()
                return
            else:
                Game.contributions[Current.round, Current.group, cls.playerpos()] = 0
                return
        else:
            pass


class SAVIOUR(Strategy):
    # Gives more if other players are broke until it itself is broke

    name = "SAVIOUR"
    # This has to be less than 100 to make sense
    own_coop = 0.5

    @classmethod
    def gives(cls):
        if cls.isnotbroke():
            if np.size(cls.acc_balance_prev()[cls.acc_balance_prev() < 0]) > 0:
                Game.contributions[Current.round, Current.group, cls.playerpos()] = cls.acc_balance_player()
                return
            else:
                Game.contributions[
                    Current.round, Current.group, cls.playerpos()] = cls.own_coop * cls.acc_balance_player()
                return
        else:
            pass


class INCENDIO(Strategy):
    # Targets one defector but punishes all. INCENDIO is the spell that sets fire to things. INCENDIO contributes according to its own standard
    # In the real world, INCENDIO at standard=100 is equivalent to checking for empty hands

    name = "INCENDIO"
    standard = 1
    first_coop = 1

    @classmethod
    def gives(cls):
        if cls.isnotbroke():
            if Current.round == 1:
                # Cooperates first
                Game.contributions[
                    Current.round, Current.group, cls.playerpos()] = cls.first_coop * Game.endowment
                return
            elif np.size(cls.payouts_vs_accounts()[cls.payouts_vs_accounts() < cls.standard]) == 0:
                Game.contributions[
                    Current.round, Current.group, cls.playerpos()] = cls.standard * cls.acc_balance_player()
                return
            else:
                Game.contributions[Current.round, Current.group, cls.playerpos()] = 0
                return
        else:
            pass


class RANDOM(Strategy):
    # Gives random float from own account
    name = "RANDOM"

    @classmethod
    def gives(cls):
        if cls.isnotbroke():
            Game.contributions[Current.round, Current.group, cls.playerpos()] = random.uniform(0,
                                                                                               cls.acc_balance_player())
            return
        else:
            pass