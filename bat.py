#!/bin/python3

import pdb

def getCoords(position):
    x = int(s[1:])
    y = ord(s[0]) - ord('A') + 1
    return (x,y)

class Player:
    def __init__(self):
        self.boats = [Carrier(), Battleship(), Cruiser(), Submarine(), Destroyer]

    def reportDestroyed(self):
        out = []
        for boat in self.boats():
            if not boat.healthy:
                out.append(boat.name)
        return out

class Boat:
    def __init__(self):
        self.healthy = True

    def setCoords(self,position):
        (self.x,self.y) = getCoords(position)

class Carrier(Boat):
    def __init__(self):
        Boat.__init__(self)
        self.name = "Carrier"
        self.size = 5
        self.icon = 'a'

class Battleship(Boat):
    def __init__(self):
        Boat.__init__(self)
        self.name = "Battleship"
        self.size = 4
        self.icon = 'b'

class Cruiser(Boat):
    def __init__(self):
        Boat.__init__(self)
        self.name = "Cruiser"
        self.size = 3
        self.icon = 'c'

class Submarine(Boat):
    def __init__(self):
        Boat.__init__(self)
        self.name = "Submarine"
        self.size = 3
        self.icon = 's'

class Destroyer(Boat):
    def __init__(self):
        Boat.__init__(self)
        self.name = "Destroyer"
        self.size = 2
        self.icon = 'd'

class Board:
    def __init__(self,size,player):
        self.board = [["." for i in range(size+1)] for i in range(size+1)]
        for i in range(size):
            self.board[0][0] = " "
            self.board[i+1][0] = chr(ord('A') + i)
            self.board[0][i+1] = str(i + 1)
        self.player = player
        self.size = size

    def display(self):
        for i in range(self.size):
            print(" ".join(self.board[i]))

class Primary(Board):
    def __init__(self,size,player):
        Board.__init__(self,size,player)

    def addBoat(self,boat,position,orientation):
        (x,y) = getCoords(position)
        for i in range(boat.size):
            self.board[x][y] = boat.icon
            if orientation == 1:
                y += 1
            else:
                x += 1

# testing
b = Primary(10,",")
b.display()
b.addBoat(Cruiser(),"D4",1)
b.display()
