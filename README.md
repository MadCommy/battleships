# Battleships Game

## Overview

Simple CLI battleships game.
Singleplayer with three levels of AI:
* Dumb: AI targets squares randomly.
* Fair: AI targets squares intelligently when there are recent hits, randomly otherwise.
* Lucky: Like Fair AI, but hits with higher probability with no information.

Multiplayer over TCP with one other player on the same network.
Other player must run the client program on their computer, and enter the host's IP address as displayed on the host's computer.

## Gameplay

1. Run the main file, and follow the instructions to setup the game.
2. While playing, type the coordinates of each shot to fire a shot (e.g. D3).
3. Take turns until the all of your (or your opponent's) ships are sunk.
