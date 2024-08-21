# pgg-tournament
An Axelrod-styled tournament among different strategies playing the public goods game. The game is iterated over all possible group combinations given a chosen group size. For each group, the game is iterated over a chosen number of rounds.
## Banking modes
Banking modes can be specified under the `Bank` class in `game.py` in the `publicgoodsgame` module. Currently, 3 modes are supported but more can be added.
- `mode=0` multiplies the total contribution by `bankerx`, a chosen amount that must be less than the number of participants for this mode
- `mode=1` takes after Bowles & Gintis (2011), p.22, where contributions are first multiplied by `bankerx`, usually less than 1, and then added to the original contributions
- `mode=2` takes after Fehr & Gachter (2002), p.137, where each player receives a fraction of every dollar contributed to the common pool. This fraction is again specified by `bankerx` which must be less than 1
## Strategies
Strategies are stored in `strategies.py` in the `publicgoodsgame` module. More strategies can and will be added.
Strategies that calculate their next move based on other players' histories have an optional communist mode. When `iscommunist` is set to true, such a strategy will judge other players by comparing what they paid out against what they afford, rather than against what it itself had paid out. Additionally, if `game.mode` in `game.py` is set to 1, the 'average opponent' will be interpreted as the median player, rather than the mean player. 

Conceptually, both `game.mode=1` and `iscommunist` require a world with perfect information, where each player knows the detailed accounts of every other player, rather than just the sum of all contributions. Currently, one strategy, `INCENDIO`, which punishes all for the perceived selfishness of one, would theoretically only be able to play in such a world, but no restriction is made in this implementation.
## Output
Currently, only a 3D-array of payouts (rounds, groups, players) and 2D-array of payins are generated, although existing functionality in `strategies.py` can calculate final account balances for each player.
