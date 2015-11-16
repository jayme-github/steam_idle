[![Code Health](https://landscape.io/github/jayme-github/steam_idle/master/landscape.svg?style=flat)](https://landscape.io/github/jayme-github/steam_idle/master)

Steam Idle
===========

This is mostly a rewrite of [Idle Master (Python branch)](https://github.com/jshackles/idle_master_py).
It will idle all games with play time < 2 hours in parallel until they are out of the refund period (2+ hours).
After that, it will idle each game sequentially untill all cards have been dropped.

I did this rewrite because I don't wanted to poke around with cookies (and I thought idle_master_py is unmaintained).

Usage
-------

* Install [steamweb](https://github.com/jayme-github/steamweb)
* Lauch Steam (and login)
* Start `steam_idle_cli.py` for a command line interface

GUI Usage
-------
* Install [steamweb](https://github.com/jayme-github/steamweb)
* Install PyQt4
* Start `steam_idle_gui.py` for a Qt4 GUI

I've only tested this with 64bit Linux so please report problems/bugs.

License
-------

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation.  A copy of the GNU General Public License can be found at http://www.gnu.org/licenses/.  For your convenience, a copy of this license is included.
