pandemaniac-modelsim
====================
Backend code for the Pandemaniac contest.


Usage
-----

    main.py --teams [team names separated by spaces] --graph [graph name] --model [model name]
    main.py --teams foo bar baz --graph 2.1.1 --model weighted_random

Possible models include:
* `majority_all`
* `majority_colored`
* `random_p`
* `weighted_random`


Tools
-----
* [pymongo 2.6.2](http://api.mongodb.org/python/current/installation.html)
* [MongoDB 2.4.6](http://www.mongodb.org/downloads)
