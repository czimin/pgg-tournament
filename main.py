import numpy as np
import os
from publicgoodsgame import *
from scipy.stats import rankdata
if __name__ == "__main__":
    game.Game.reset_accounts()

    # For debugging purposes:
    # print(game.Game.fixture)
    print(game.Game.fixture.shape)
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
        game.Current.group = game.Current.group + 1

    # 1D-array
    payins_sum_along_rounds = np.sum(game.Game.payins, axis=0)
    # 2D-array
    payouts_sum_along_rounds = np.sum(game.Game.payouts, axis=0)
    balance_along_rounds = np.vstack(payins_sum_along_rounds) - payouts_sum_along_rounds

    # For debugging purposes (should be same as above):
    # print(game.Game.fixture)

    final_results = np.arange(len(game.Player)*2).reshape(2,len(game.Player)).astype(float)

    column = 0

    for p in game.Player:
        final_results[0,column] = p.value

        x,y = np.where(game.Game.fixture == p.value)
        mask = x,y
        # For debugging purposes (to check that coordinates given are correct):
        # print(mask)
        this_player_total = balance_along_rounds[mask].sum()
        print(f"Player {p.name}'s total score: {this_player_total}")
        final_results[1,column] = this_player_total
        column = column+1


tourn_ranking = np.arange(len(game.Player)*2).reshape(2,len(game.Player))
tourn_ranking[0,:] = final_results[0,:]
tourn_ranking[1,:] = rankdata(final_results[1,:],method='dense')
print("Tournament ranking (lowest score = 1):")
print(tourn_ranking)

# For output to LaTeX for term paper
# exp_players = 7
# tolatex_arr = np.zeros(exp_players).astype(int)
# for exp_p in range(exp_players):
#     if exp_p in final_results[0,:]:
#         p_score_column = np.where(final_results[0,:] == exp_p)[0][0]
#         tolatex_arr[exp_p] = tourn_ranking[1,p_score_column]

# tolatex_list = tolatex_arr.tolist()

# if 0 in tolatex_arr:
#     notplayed_index = np.where(tolatex_arr == 0)[0][0]
#     tolatex_list[notplayed_index] = "--"

# with open('output_s2.txt', 'rb') as f:
#     try:  # catch OSError in case of a one line file
#         f.seek(-2, os.SEEK_END)
#         while f.read(1) != b'\n':
#             f.seek(-2, os.SEEK_CUR)
#     except OSError:
#         f.seek(0)
#     last_line = f.readline().decode()

# with open('output_s2.txt','a') as f:
#     if "Rounds" in last_line or ",8," in last_line or ",16," in last_line or ",32," in last_line or ",40," in last_line:
#             f.write(f"{game.Game.total_rounds},{game.tourn_no},")
#     else:
#         f.write(f",{game.tourn_no},")

#     f.write(",".join(map(str, tolatex_list)) + "\n")
