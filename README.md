pandemaniac-modelsim
====================
Backend code for the Pandemaniac contest.


Script Usage
------------
This is what's going to be used for the practice and competition rounds. The graphs used for the
competition and the teams participating are all pre-set in the `run.py` script.

    run.py --day [day or competition round] --teams [teams competing]
    run.py --day 4 --teams a b c d

For example, for competition round 2:

    run.py --day c2 --teams a b c d

There must be at least 8 teams. If not, filler teams should be added:

    run.py --day3 --teams a b c d e f filler1 filler2


Simulation Usage
----------------

    main.py --teams [team names separated by spaces] --graph [graph name] --model [model name]
    main.py --teams foo bar baz --graph 2.1.1 --model weighted_random

Possible models include:
* `majority_all`
* `majority_colored`
* `most_common_colored`
* `random_p`
* `weighted_random`

Tools
-----
* Python 2.7 (32-bit)
* [pymongo 2.6.2](http://api.mongodb.org/python/current/installation.html)
  Install with `python setup.py install --user` 
* [MongoDB 2.4.6](http://www.mongodb.org/downloads)

