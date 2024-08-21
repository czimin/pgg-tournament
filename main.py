import numpy as np
from publicgoodsgame import *
if __name__ == "__main__":

    game.Game.reset_accounts()
    
    game.Current.group = 0
    for g in np.arange(np.shape(game.Game.fixture)[0]):
        game.Current.round = 1
        print(f" In group {g}: {game.Game.fixture[g,:]}")
        for r in range(1, game.Game.total_rounds):
            print(f" In round {r}:")
            
            for p in game.Game.fixture[g,:]:
                eval(f"strategies.{game.Player(p).name}").gives()
                print(f"Player {game.Player(p).name} has made a move")
            
            game.Bank.credits()
            print(f"Banker has credited all acounts for this round")
            game.Current.round = game.Current.round + 1
            
        game.Current.group = game.Current.group + 1
        