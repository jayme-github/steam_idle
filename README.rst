.. image:: https://landscape.io/github/jayme-github/steam_idle/master/landscape.svg?style=flat
   :target: https://landscape.io/github/jayme-github/steam_idle/master
   :alt: Code Health

============
Steam Idle
============

This is mostly a rewrite of `Idle Master (Python branch) <https://github.com/jshackles/idle_master_py>`_.
It will idle all games with play time < 2 hours in parallel until they are out of the refund period (2+ hours).
After that, it will idle each game sequentially untill all cards have been dropped.

I did this rewrite because I don't wanted to poke around with cookies (and I thought idle_master_py is unmaintained).

Installation
============

.. code-block:: sh

    pip install steam_idle

Requirements
============

* `steamweb <https://github.com/jayme-github/steamweb>`_>=0.6
* pycrypto>=2.6.1
* requests>=2.7.0
* future>=0.14.3 (python 2.x)

Usage
=====

Just run *steam_idle_cli.py* and follow the instructions:

.. code-block:: sh

    steam_idle_cli.py



GUI (Qt) version
================

For a (Qt 4) GUI version please see `steam_idle_gui <https://github.com/jayme-github/steam_idle_gui>`_.

License
=======

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation.  A copy of the GNU General Public License can be found at http://www.gnu.org/licenses/.  For your convenience, a copy of this license is included.
