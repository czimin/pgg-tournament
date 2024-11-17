# pgg-tournament
An Axelrod-inspired tournament among different strategies playing the public goods game. The tournament comprises all possible group combinations given a chosen group size, each group playing over a chosen number of rounds. The implementation can only run one tournament at a time.

## Strategies
Strategies are stored in `strategies.py` in the `publicgoodsgame` module. Most strategies are original, including PD strategies re-interpreted for this game.

## Output
Contributions and winnings are stored in NumPy arrays and can be viewed at any time. `main.py` generates a logarithmic graph of each player's balance over the course of the tournament.

## To-Do
- Different players can play the same strategy
- Players can change their strategy
- In big groups with more cooperators with fewer `HYPOCRITEs`, the `HYPOCRITEs` can get away more easily, since the average becomes closer to the maximum average. Find the highest ratio of `HYPOCRITEs` over cooperators before `HYPOCRITEs` die. (This is a form of frequency dependent selection.)
