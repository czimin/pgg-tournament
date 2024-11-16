import numpy as np
import matplotlib.pyplot as plt
# import os
from publicgoodsgame import *

if __name__ == "__main__":
    game.Game.reset_accounts()

    game.Current.group = 0
    for g in np.arange(np.shape(game.Game.fixture)[0]):
        game.Current.round = 1

        for r in range(1, game.Game.total_rounds):
            # print(f" In round {r}:")

            for p in game.Game.fixture[g, :]:
                eval(f"strategies.{game.Player(p).name}").gives()

            game.Bank.credits()

            game.Current.round = game.Current.round + 1

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

plt.show()

