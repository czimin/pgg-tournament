import numpy as np
import matplotlib.pyplot as plt
# import os
from publicgoodsgame import *

# from scipy.stats import rankdata
if __name__ == "__main__":
    game.Game.reset_accounts()

    game.Current.group = 0
    for g in np.arange(np.shape(game.Game.fixture)[0]):
        # print(f" In group {g}: {game.Game.fixture[g,:]}")
        # print(f"Payins at round 0: {game.Game.winnings[0,game.Current.group]}")
        # print(f"Payouts at round 0: {game.Game.contributions[0,game.Current.group,:]}")
        game.Current.round = 1

        for r in range(1, game.Game.total_rounds):
            # print(f" In round {r}:")

            for p in game.Game.fixture[g, :]:
                eval(f"strategies.{game.Player(p).name}").gives()
                # print(f"Player {game.Player(p).name} has made a move")

            game.Bank.credits()
            # print(f"Banker has credited all accounts for this round")
            # print(f"Payins for this round: {game.Game.winnings[game.Current.round,game.Current.group]}")
            # print(f"Payouts for this round: {game.Game.contributions[game.Current.round,game.Current.group,:]}")
            # print(f"Accounts for this round: {strategies.Strategy.acc_balance_all()}")
            game.Current.round = game.Current.round + 1
        # print(f"The total scores for this group are {strategies.Strategy.acc_balance_all()}.")
        game.Current.group = game.Current.group + 1

    all_accounts = game.Game.winnings[:, :, np.newaxis] - game.Game.contributions
    # print(all_accounts[0,:,:])

    # print(game.Game.fixture.shape, game.Game.winnings.shape, game.Game.contributions[0, :, :].shape)
    player_t_history_dict = {}
    for p in game.Player:
        g, m = np.where(game.Game.fixture == p.value)
        player_tournament_history = np.zeros((game.Game.total_rounds,), dtype=np.float64)
        player_tournament_history[0] = all_accounts[0, g, m].sum()
        for r in range(1, game.Game.total_rounds):
            player_tournament_history[r] = all_accounts[r, g, m].sum() + player_tournament_history[r - 1]
        player_t_history_dict[p.name] = player_tournament_history

for player, rounds in player_t_history_dict.items():
    plt.plot(rounds, label=player)

# Add labels and title
plt.xlabel('Round')
plt.ylabel('Account Balance')
plt.yscale('log')
plt.title('Balance per Round for Each Player')
plt.legend()

# Make the x-axis finer
# plt.xticks(np.arange(0, 31, 1))  # Adjust the range and step as needed

# Show the plot
plt.show()

