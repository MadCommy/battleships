#!/bin/python3

import socket

class RemotePlayer:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 4000

        host = input("Enter host ip (default = 127.0.0.1): ")
        if len(host) > 0:
            self.host = host

        port = input("Enter port number (default=4000): ")
        if len(port) > 0:
            self.port = int(port)

        self.s = socket.socket()
        self.s.connect((self.host,self.port))
        self.listen()


    def listen(self):
        message = self.s.recv(1024).decode()
        while True:
            if message == "display":
                self.display()
            elif message == "input":
                self.input()
            elif message == "end":
                self.end()
            else:
                break
            message = self.s.recv(1024).decode()

        self.s.close()
        exit()

    def input(self):
        self.s.send("input go".encode())
        message = self.s.recv(1024).decode()
        reply = input(message)
        self.s.send(reply.encode())

    def display(self):
        self.s.send("display go".encode())
        message = self.s.recv(1024).decode()
        print(message)

    def end(self):
        self.s.close()
        exit()

remote = RemotePlayer()
