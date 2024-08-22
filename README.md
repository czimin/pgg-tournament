# pgg-tournament
An Axelrod-styled tournament among different strategies playing the public goods game. The tournament comprises all possible group combinations given a chosen group size, each group playing over a chosen number of rounds. The implementation can only run one tournament at a time.

## Results
On default settings, the champion of the tournament is `HYPOCRITE`. Perhaps surprisingly, the sucker of the tournament is `ALLD`.

## Banking modes
Banking modes can be specified under the `Bank` class in `game.py` in the `publicgoodsgame` module. Currently, 3 modes are supported but more can be added.
- `mode=0` multiplies the total contribution by `bankerx`, a chosen amount that must be less than the number of participants for this mode
- `mode=1` takes after Bowles & Gintis (2011), p.22, where contributions are first multiplied by `bankerx`, usually less than 1, and then added to the original contributions
- `mode=2` takes after Fehr & Gachter (2002), p.137, where each player receives a fraction of every dollar contributed to the common pool. This fraction is again specified by `bankerx` which must be less than 1

## Strategies
Update 22/08/24: Previously, TFT ended up with negative accounts because other players' average contribution from the previous round is greater than what it currently has. This has now been fixed. TFT and its cousins now give everything they have, should they have less than what they feel they *should* contribute.

Strategies are stored in `strategies.py` in the `publicgoodsgame` module. More strategies can and will be added.
Strategies that calculate their next move based on other players' histories have an optional communist mode. When `iscommunist` is set to true, such a strategy will judge other players by comparing what they contributed against what they can afford, rather than against what it itself had paid out. Additionally, if `game.mode` in `game.py` is set to 1, the 'average opponent' will be interpreted as the median player, rather than the mean player. 

Conceptually, both `game.mode=1` and `iscommunist` require a world with perfect information, where each player knows the detailed accounts of every other player, rather than just the sum of all contributions. Currently, one strategy, `INCENDIO`, which punishes all for the perceived selfishness of one, would theoretically only be able to play in such a world, but no restriction is made in this implementation.

## Output
At any point in the tournament, a 3D-array of payouts (rounds, groups, players) and a 2D-array of payins (rounds, groups) can be accessed. Payins and payouts at the end of each round and the winner for each group are also printed. When the tournament ends, the total balances for each player and the champion is printed.

## Warning
If something looks wrong, it probably is. This is my first go at Python.
