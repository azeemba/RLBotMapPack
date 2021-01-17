RLBot Map Pack
==============

Currently this is still in an investigation phase but the goal
is to provide some custom maps that RLBot users can download.
The goal is to make them available in Story mode.


## How to use

We will have some automation later but for now this is what you can do:

- Download and install RLBot
- Download this repo
    - Maps are not committed in the repo so for now manually copy over the 
      maps in the right directories. For example move Simplicity.upk in `Simplicity/`
- Run RLBot. Click "Add" -> "Load Bot Folder" and select the repo that you downloaded.
- In the botton go to the "match settings" section, the map drop down should
  show the custom maps now. When you select it and start a match, the custom
  map should be loaded and any helper scripts for that map should run as well.


## How to develop custom map scripts

Custom map scripts let you run a RLBot-based python script that can read
and manipulate things in the match. This can make some coding things easier.

An example script is `Simplicity/runner.py` which simply prints various
things about the game state. It can just as easily change things
like the position/velocity/rotation of any car or ball. 

This style of script
allows you to subscribe to all spectate events, all stat changes and all user inputs: https://github.com/RLBot/RLBot/blob/master/src/test/python/agents/script/socket_script.py


If you want to add custom script support, then you need a `.cfg` file for the 
custom script to be detected. The custom script should be named like this: `_mapname.cfg` where the mapname matches whats before the `.upk` for the map.

The .cfg file will direct RLBot to the location of the script. This script can be any python3.7 code. There are some helper classes that can be useful as shown
in the samples described above.
