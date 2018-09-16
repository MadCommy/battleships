#!/bin/python3

import pdb
import random
import re
import os
import socket

# to get local ip adress, run:
# hostname --ip-address

class Game:
    def __init__(self):
        self.size = 10

        self.multiplayer = False
        # self.host = '127.0.0.1'
        self.host = os.popen("hostname --ip-address").readlines()[0].rstrip()
        self.port = 4000

        self.autosetup = self.getAutoSetup()

        self.player1 = Player(self,"Player 1",self.size,"human")
        self.player2 = Player(self,"Player 2",self.size,self.getOpponent())

    def __repr__(self):
        return "\n".join(["size:" + str(self.size),str(self.player1),str(self.player2)])

    def getSize(self):
        while True:
            size = int(input("Board size? (min. 10): "))
            if (size >= 10):
                return size

    def getAutoSetup(self):
        while True:
            i = input("Auto-setup ships? (y/n): ") 
            if len(i) == 0:
                return True
            elif i == 'y':
                return True
            elif i == 'n':
                return False
            print("Type y/n")

    def getOpponent(self):
            while True:
                i = input("Play against Human or Computer? (human|computer): ") 
                if i == "human" or i == "h":
                    self.multiplayer = True
                    port = input("Enter port number (default 4000): ")
                    if len(port) > 0:
                        self.port = int(port)
                    # host = input("Enter host ip (default 127.0.0.1): ")
                    # if len(host) > 0:
                    #     self.host = host
                    return "remote"
                elif i == "computer" or i == "c":
                    while True:
                        ai = input("AI type? (dumb|fair|lucky): ")
                        if ai in ["dumb","fair","lucky"]:
                            return ai

    def placeShips(self):
        self.player1.placeShips()
        self.player2.placeShips()

    def play(self):
        winner = ""
        while True:
            if self.player1.playTurn() == "game over":
                winner = self.player1
                break
            if self.player2.playTurn() == "game over":
                winner = self.player2
                break

        self.display(winner.name + " wins!")
        return

    def run(self):
        self.placeShips()
        self.play()

    def display(s):
        self.player1.controller.display(s)
        self.player2.controller.display(s)
        
    def end(self):
        if self.multiplayer:
            self.player2.controller.prep("end")
            self.player2.controller.connection.close()
        exit()

class Player:
    def __init__(self,game,name,size,control):
        self.ships = [Carrier(), Battleship(), Cruiser(), Destroyer(), Destroyer(), Submarine(), Submarine()]
        self.game = game
        self.name = name
        self.size = size
        self.shots = []
        self.nature = "" 
        self.primary = Primary(self)
        self.secondary = Secondary(self)

        if control == "human":
            self.controller = Human(self)
        if control == "remote":
            self.controller = Remote(self)
        elif control == "dumb":
            self.controller = Dumb(self)
        elif control == "fair":
            self.controller = Fair(self)
        elif control == "lucky":
            self.controller = Lucky(self)
        else:
            self.controller == Fair(self)

    def __repr__(self):
        out = ["\n"]
        out.append("**********************")
        out.append("=====BATTLESHIPS======")
        out.append("----------------------")
        out.append("You are: " + self.name)
        out.append("----------------------")
        out.append("\n".join([str(ship) for ship in self.ships]))
        out.append("========Fleet=========")
        out.append("----------------------")
        out.append(str(self.secondary))
        out.append("=======Tracker========")
        out.append("----------------------")
        out.append(str(self.primary))
        out.append("=======Primary========")
        out.append("----------------------")
        return "\n".join(out)

    def placeShips(self):
        for ship in self.ships:
            x,y,facing = self.controller.getPlacement(ship)
            self.primary.placeShip(ship,x,y,facing)
            ship.recordPlacement(x,y,facing)
        return

    def playTurn(self):
        x,y = self.controller.getShot()
        shot = self.fireShot(x,y)
        if (shot[0] == "miss"):
            self.secondary.shotMiss(x,y)
            self.controller.display(str(self))
        elif (shot[0] == "hit"):
            self.secondary.shotHit(x,y)
            self.controller.display(str(self))
        elif (shot[0] == "sunk"):
            self.secondary.shotSunk(shot[1])
            self.controller.display(str(self))
        elif (shot[0] == "game over"):
            self.secondary.shotSunk(shot[1])
            self.controller.display(str(self))
            return "game over"
        else:
            return "error"

    def fireShot(self,x,y):
        if self == self.game.player1:
            shot = self.game.player2.receiveShot(x,y)
            return shot
        else:
            shot = self.game.player1.receiveShot(x,y)
            return shot

    def receiveShot(self,x,y):
        for ship in self.ships:
            if (x,y) in ship.cells:
                if (ship.takeHit(x,y) == "sunk"):
                    self.ships.remove(ship)
                    if self.ships == []:
                        return ("game over",ship)
                    self.primary.shotSunk(ship)
                    return ("sunk",ship)
                self.primary.shotHit(x,y)
                return ("hit",ship)
        self.primary.shotMiss(x,y)
        return ("miss",0)

    def recordShot(self,x,y,ship):
        self.shots.append(Shot(x,y,ship))

class Controller:
    def __init__(self,player):
        self.player = player
        self.primary = player.primary
        self.secondary = player.secondary
        self.ships = player.ships

    def validPlacements(self,ship):
        placements = []
        for x in range(1,self.player.size):
            for y in range(1,self.player.size):
                for facing in ["down","right"]:
                    if self.player.primary.isValidPlacement(ship,x,y,facing):
                        placements.append((x,y,facing))
        return placements

    def validShots(self):
        cells = []
        for x in range(1,self.player.size):
            for y in range(1,self.player.size):
                if (self.secondary.isValidShot(x,y)):
                    cells.append((x,y))
        return cells

class Human(Controller):
    def getPlacement(self,ship):
        if self.player.game.autosetup:
            return self.getPlacementAuto(ship)
        else:
            return self.getPlacementManual(ship)

    def display(self,s):
        print(s)

    def getPlacementManual(self,ship):
        while True:
            self.display(str(self.player.primary))
            position = input("Position for " + ship.name + ": ")
            if not (re.match('[A-Za-z][0-9]+',position)):
                self.display("Invalid coordinates.")
                continue
            x,y = getXY(position)
            facing = input("Facing [right|down]: ")
            if (facing != "right" and facing != "down"):
                self.display("type \"right\" or \"down\"")
                continue
            if (self.player.primary.isValidPlacement(ship,x,y,facing)):
                return x,y,facing
            self.display("Invalid placement.")

    def getPlacementAuto(self,ship):
        return random.choice(self.validPlacements(ship))

    def getShot(self):
        while True:
            self.display(str(self.player))
            position = input("Enter shot coordinates: ")
            if position == 'r':
                return random.choice(self.validShots())
            elif position == 'q':
                self.player.game.end()
            elif not (re.match('[A-Za-z][0-9]+',position)):
                self.display("Invalid coordinates.")
                continue
            x,y = getXY(position)
            if self.secondary.isValidShot(x,y):
                return x,y
            self.display("Invalid shot.")

class Remote(Human):
    def __init__(self,player):
        Human.__init__(self,player)
        self.host = self.player.game.host
        self.port = self.player.game.port
        self.socket = socket.socket()
        self.socket.bind((self.host,self.port))
        self.socket.listen(1)
        print("IP address is " + self.player.game.host)
        print("Waiting for player 2 to connect...")
        self.connection, self.addr = self.socket.accept()
        self.display(str(self.player))

    def prep(self,command):
        # commands are: display|input
        self.connection.send(command.encode())
        check = self.connection.recv(1024)

    def display(self,s):
        self.prep("display")
        self.connection.send(s.encode())

    def input(self,s):
        self.prep("input")
        self.connection.send(s.encode())
        message = self.connection.recv(1024).decode()
        return message

    def getShot(self):
        while True:
            self.display(str(self.player))
            position = self.input("Enter shot coordinates: ")
            if position == 'q':
                self.player.game.end()
            elif position == 'r':
                return random.choice(self.validShots())
            elif not (re.match('[A-Za-z][0-9]+',position)):
                self.display("Invalid coordinates.")
                continue
            x,y = getXY(position)
            if self.secondary.isValidShot(x,y):
                return x,y
            self.display("Invalid shot.")

class AI(Controller):
    def display(self,s):
        return

    def getPlacement(self,ship):
        return random.choice(self.validPlacements(ship))

    def randomShot(self):
        return random.choice(self.validShots())

    def getShipCells(self):
        cells = []
        opponent = ""
        if self.player.name == "player1":
            opponent = self.player.game.player2
        else:
            opponent = self.player.game.player1
        for x in range(1,self.player.size):
            for y in range(1,self.player.size):
                if opponent.primary.board[x][y] in ['a','b','c','d','s']:
                    cells.append((x,y))
        return cells

    def semiRandomShot(self,luck):
        if luck/100 < 1/len(self.validShots()):
            return self.randomShot()
        r = random.randint(1,100)
        if r <= luck:
            return random.choice(self.getShipCells())
        else:
            return self.randomShot()

    def getHits(self):
        out = []
        for i in range(1,self.player.size):
            for j in range(1,self.player.size):
                if self.player.secondary.board[i][j] == '#':
                    out.append((i,j))
        return out

    def getLines(self):
        hits = self.hits
        if len(hits) < 2:
            return []
        lines = []
        for hit in hits:

            i = 0
            while True:
                if (hit[0] + 1 + i,hit[1]) in hits:
                    i += 1
                else:
                    break
            if i > 0:
                lines.append((hit,"down",i))

            j = 0
            while True:
                if (hit[0],hit[1] + 1 + j) in hits:
                    j += 1
                else:
                    break
            if j > 0:
                lines.append((hit,"right",j))

        return lines

    def getAdjacent(self,cell):
        (x,y) = cell
        return [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]

    def targetLines(self):
        for line in self.lines:
            (x,y) = line[0]
            direction = line[1]
            distance = line[2]

            if direction == "down":
                if self.secondary.isValidShot(x-1,y):
                    return x-1,y
                elif self.secondary.isValidShot(x+distance+1,y):
                    return x + distance + 1,y
            elif direction == "right":
                if self.secondary.isValidShot(x,y-1):
                    return x,y-1
                elif self.secondary.isValidShot(x,y+distance+1):
                    return x,y+distance+1

        return 0

    def targetHits(self):
        for cell in self.hits:
            cells = self.getAdjacent(cell)
            for (x,y) in cells:
                if self.secondary.isValidShot(x,y):
                    return (x,y)
        return 0

class Dumb(AI):
    def getShot(self):
        x,y = self.randomShot()
        return x,y

class Fair(AI):
    def __init__(self,player):
        AI.__init__(self,player)
        i = - max(4,len(self.player.shots))
        self.lines = []
        self.hits = []

    def getShot(self):
        self.hits = self.getHits()
        self.lines = self.getLines()
        if len(self.lines) > 0:
            shot = self.targetLines()
            if shot != 0:
                return shot
        if len(self.hits) > 0:
            shot = self.targetHits()
            if shot != 0:
                return shot
        else:
            return self.randomShot()

class Lucky(AI):
    def __init__(self,player):
        AI.__init__(self,player)
        i = - max(4,len(self.player.shots))
        self.lines = []
        self.hits = []

    def getShot(self):
        self.hits = self.getHits()
        self.lines = self.getLines()
        if len(self.lines) > 0:
            shot = self.targetLines()
            if shot != 0:
                return shot
        if len(self.hits) > 0:
            shot = self.targetHits()
            if shot != 0:
                return shot
        else:
            return self.semiRandomShot(25)
    
class Perfect(AI):
    def __init__(self,player):
        AI.__init__(self,player)
        i = - max(4,len(self.player.shots))
        self.lines = []
        self.hits = []

    def getShot(self):
        self.hits = self.getHits()
        self.lines = self.getLines()
        if len(self.lines) > 0:
            shot = self.targetLines()
            if shot != 0:
                return shot
        if len(self.hits) > 0:
            shot = self.targetHits()
            if shot != 0:
                return shot
        else:
            return self.semiRandomShot(100)
    
def getXY(position):
    x = ord(position[0].upper()) - ord('A') + 1
    y = int(position[1:])
    return x,y

class Board:
    def __init__(self,player):
        self.player = player
        self.size = player.size
        self.board = [["." for i in range(self.size+1)] for i in range(self.size+1)]
        self.board[0][0] = " "
        for i in range(self.size):
            self.board[i+1][0] = chr(ord('A') + i)
            self.board[0][i+1] = str(i + 1)

    def __repr__(self):
        out = "\n".join([" ".join(self.board[i]) for i in range(self.size + 1)])
        return out

class Primary(Board):
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
    
    def shotHit(self,x,y):
        self.board[x][y] = '#'

    def shotSunk(self,ship):
        for (x,y) in ship.initialCells:
            self.board[x][y] = '%'

    def shotMiss(self,x,y):
        self.board[x][y] = '+'

class Secondary(Board):
    def shotHit(self,x,y):
        self.board[x][y] = '#'

    def shotSunk(self,ship):
        for (x,y) in ship.initialCells:
            self.board[x][y] = ship.icon

    def shotMiss(self,x,y):
        self.board[x][y] = '+'

    def isValidShot(self,x,y):
        if (x > self.size) or (y > self.size):
            return False
        elif (self.board[x][y] == '.'):
            return True
        else:
            return False

class Ship:
    def __init__(self):
        self.cells = []
        self.initialCells = []
        self.health = ""
        self.healthIcon = "*"

    def __repr__(self):
        padding = " "*(len("Battleship") - len(self.name))
        out = [self.name + padding]
        # for cell in self.cells:
        #     out.append(str(cell))
        out.append(self.health)
        return " ".join(out)

    def recordPlacement(self,x,y,facing):
        for i in range(self.size):
            self.cells.append((x,y))
            self.initialCells.append((x,y))
            if (facing == "down"):
                x += 1
            else:
                y += 1

    def takeHit(self,x,y):
        self.cells.remove((x,y))
        i = 0
        for cell in self.initialCells:
            if cell == (x,y):
                break
            i += 1
        temp = list(self.health)
        temp[i] = '#'
        self.health = "".join(temp)
        if self.cells == []:
            return "sunk"

class Carrier(Ship):
    def __init__(self):
        Ship.__init__(self)
        self.name = "Carrier"
        self.size = 5
        self.icon = 'a'
        for i in range(self.size):
            self.health += self.healthIcon

class Battleship(Ship):
    def __init__(self):
        Ship.__init__(self)
        self.name = "Battleship"
        self.size = 4
        self.icon = 'b'
        for i in range(self.size):
            self.health += self.healthIcon

class Cruiser(Ship):
    def __init__(self):
        Ship.__init__(self)
        self.name = "Cruiser"
        self.size = 3
        self.icon = 'c'
        for i in range(self.size):
            self.health += self.healthIcon

class Submarine(Ship):
    def __init__(self):
        Ship.__init__(self)
        self.name = "Submarine"
        self.size = 1
        self.icon = 's'
        for i in range(self.size):
            self.health += self.healthIcon

class Destroyer(Ship):
    def __init__(self):
        Ship.__init__(self)
        self.name = "Destroyer"
        self.size = 2
        self.icon = 'd'
        for i in range(self.size):
            self.health += self.healthIcon

myGame = Game()
myGame.run()
