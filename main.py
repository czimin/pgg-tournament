import numpy as np
from publicgoodsgame import *
if __name__ == "__main__":

    game.Game.reset_accounts()

    # For debugging purposes:
    # print(game.Game.fixture)
    # print(game.Game.fixture.shape)
    # This should be the same as the fixture
    # print(game.Game.payins.shape)
    
    game.Current.group = 0
    for g in np.arange(np.shape(game.Game.fixture)[0]):
        print(f" In group {g}: {game.Game.fixture[g,:]}")
        print(f"Payins at round 0: {game.Game.payins[0,game.Current.group]}")
        print(f"Payouts at round 0: {game.Game.payouts[0,game.Current.group,:]}")
        game.Current.round = 1

        for r in range(1, game.Game.total_rounds):
            print(f" In round {r}:")
            
            for p in game.Game.fixture[g,:]:
                eval(f"strategies.{game.Player(p).name}").gives()
                print(f"Player {game.Player(p).name} has made a move")
            
            game.Bank.credits()
            print(f"Banker has credited all accounts for this round")
            print(f"Payins for this round: {game.Game.payins[game.Current.round,game.Current.group]}")
            print(f"Payouts for this round: {game.Game.payouts[game.Current.round,game.Current.group,:]}")
            print(f"Accounts for this round: {strategies.Strategy.acc_balance_all()}")
            game.Current.round = game.Current.round + 1
        print(f"The total scores for this group are {strategies.Strategy.acc_balance_all()}.")
        group_winner_val = strategies.Strategy.acc_balance_all().argmax()
        group_winner = game.Game.fixture[g,group_winner_val]
        print(f"The winner for this group is {game.Player(group_winner).name}")
        game.Current.group = game.Current.group + 1

    # 1D-array
    payins_sum_along_rounds = np.sum(game.Game.payins, axis=0)
    # 2D-array
    payouts_sum_along_rounds = np.sum(game.Game.payouts, axis=0)
    balance_along_rounds = np.vstack(payins_sum_along_rounds) - payouts_sum_along_rounds

    # For debugging purposes (should be same as above):
    # print(game.Game.fixture)

    # Players' indices
    final_scores_players = []
    # Players' scores
    _final_scores_values = []

    for p in game.Player:
        final_scores_players.append(p.value)
        x,y = np.where(game.Game.fixture == p.value)
        mask = x,y
        # For debugging purposes (to check that coordinates given are correct):
        # print(mask)
        this_player_total = balance_along_rounds[mask].sum()
        print(f"Player {p.name}'s total score: {this_player_total}")
        _final_scores_values.append(this_player_total)

    # Prevents overflow error
    final_scores_values = np.array(_final_scores_values).astype(np.int64)
    final_scores = np.arange(len(final_scores_players)*2).reshape(2,len(final_scores_players))
    final_scores[0,:] = final_scores_players
    final_scores[1,:] = final_scores_values

    champion = game.Player(final_scores[0,final_scores[1,:].argmax()]).name
    sucker = game.Player(final_scores[0,final_scores[1,:].argmin()]).name
    print(f"The champion is {champion} and the sucker is {sucker}")

    stand = np.argsort(final_scores[1])[::-1]
    ranked_stand_by_value = final_scores[0][stand]
    ranked_stand_by_name = []
    for v in ranked_stand_by_value:
        ranked_stand_by_name.append(game.Player(v).name)

    print(f"Ranking: {ranked_stand_by_name}")
