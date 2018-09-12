#!/bin/python3

import pdb
import random
import re

class Game:
    def __init__(self,size):
        self.player1 = Player('P',size,True)
        self.player2 = Player('Q',size,False)
        self.size = size
    
    def __repr__(self):
        return "\n".join(["size:" + str(self.size),str(self.player1),str(self.player2)])

    def setup(self):
        self.player1.placeShips()
        self.player2.placeShips()

    def play(self):
        winner
        while True:
            # methods return true if that play results in a win
            if self.player1.playTurn():
                winner = self.player1
                break
            if self.player2.playTurn():
                winner = self.player2
                break

        print(winner.icon + " wins!")
        return

    def run(self):
        self.setup()
        self.play()

class Player:
    def __init__(self,icon,size,human):
        self.ships = [Carrier(), Battleship(), Cruiser(), Destroyer(), Destroyer(), Submarine(), Submarine()]
        self.icon = icon
        self.size = size
        self.nature = "" 
        self.primary = Primary(self)
        self.secondary = Secondary(self)
        if human:
            self.controller = Human(self)
            self.nature = "Human"
        else:
            self.controller = Computer(self)
            self.nature = "Computer"

    def __repr__(self):
        out = [self.nature + " " + self.icon + ':']
        out.append(" ".join([ship.name for ship in self.ships]))
        out.append(str(self.primary))
        out.append(str(self.secondary))
        return "\n".join(out)

    def placeShips(self):
        for ship in self.ships:
            x,y,facing = self.controller.getPlacement(self,ship)
            self.primary.placeShip(ship,x,y,facing)
        return

    def playTurn(self):
        x,y = self.controller.getShot(self)

class Controller:
    def __init__(self,player):
        self.player = player
        self.primary = player.primary
        self.secondary = player.secondary
        self.ships = player.ships

class Human(Controller):
    def getPlacement(self,player,ship):
        while True:
            print(player.primary)
            position = input("Position for " + ship.name + ": ")
            if not (re.match('[A-Za-z][0-9]+',position)):
                print("Invalid coordinates.")
                continue
            x,y = getXY(position)
            facing = input("Facing [right|down]: ")
            if (facing != "right" and facing != "down"):
                print("type \"right\" or \"down\"")
                continue
            if (player.primary.isValidPlacement(ship,x,y,facing)):
                return x,y,facing
            print("Invalid placement.")

    def getShot(self,player):
        #TODO
        return x,y

class Computer(Controller):
    def getPlacement(self,player,ship):
        x,y,facing = random.choice(self.validPlacements(player,ship))
        return x,y,facing
    
    def validPlacements(self,player,ship):
        placements = []
        for x in range(1,player.size):
            for y in range(1,player.size):
                for facing in ["down","right"]:
                    if player.primary.isValidPlacement(ship,x,y,facing):
                        placements.append((x,y,facing))
        return placements

    def getShot(self,player):
        #TODO
        return x,y

def getXY(position):
    x = ord(position[0].upper()) - ord('A') + 1
    y = int(position[1:])
    return x,y

class Board:
    def __init__(self,player):
        size = player.size
        self.board = [["." for i in range(size+1)] for i in range(size+1)]
        for i in range(size):
            self.board[0][0] = " "
            self.board[i+1][0] = chr(ord('A') + i)
            self.board[0][i+1] = str(i + 1)
        self.player = player
        self.size = size

    def __repr__(self):
        out = "\n".join([" ".join(self.board[i]) for i in range(self.size)])
        return out

class Primary(Board):
    def __init__(self,player):
        Board.__init__(self,player)
        self.board[0][0] = self.player.icon.upper()

    def placeShip(self,ship,x,y,facing):
        for i in range(ship.size):
            self.board[x][y] = ship.icon
            if (facing == "down"):
                x += 1
            else:
                y += 1
        return 1
    
    def isValidPlacement(self,ship,x,y,facing):
        for i in range(ship.size):
            if (x > self.size) or (y > self.size):
                return False
            elif (self.board[x][y] != '.'):
                return False

            if (facing == "down"):
                x += 1
            else:
                y += 1
        return True

class Secondary(Board):
    def __init__(self,player):
        Board.__init__(self,player)
        self.board[0][0] = self.player.icon.lower()

class Carrier:
    def __init__(self):
        self.name = "Carrier"
        self.size = 5
        self.icon = 'a'

class Battleship:
    def __init__(self):
        self.name = "Battleship"
        self.size = 4
        self.icon = 'b'

class Cruiser:
    def __init__(self):
        self.name = "Cruiser"
        self.size = 3
        self.icon = 'c'

class Submarine:
    def __init__(self):
        self.name = "Submarine"
        self.size = 3
        self.icon = 's'

class Destroyer:
    def __init__(self):
        self.name = "Destroyer"
        self.size = 2
        self.icon = 'd'

myGame = Game(10)
myGame.run()
