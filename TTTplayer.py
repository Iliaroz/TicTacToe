# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 16:03:27 2022

@author: kasia
"""
import numpy as np
import random
from AppCommon import VideoMode, BoardState
from DobotClass import Dobot

class Player:
    def __init__(self, sign, game):
        self.game = game
        self.empty = BoardState.Empty # 0
        self.P1sign = BoardState.Blue # 1
        self.P2sign = BoardState.Red #-1
        self.playerSign = sign
        
    def getNextMove(self, board):
        """
        return next player move to Game
        """
        pass
    
    def MoveApproved(self):
        """
        Called by Game when last move gotten by getNextMove is accepted by Game
        """
        pass
    
    def Winner(self):
        """
        Call by Game when player won the game
        """
        pass

    def Loser(self):
        """
        Call by Game when player lose game
        """
        pass

    def startOfGame(self):
        pass

    def endOfGame(self):
        pass
    




class HumanPlayer(Player):
    def __init__(self, sign, game):
        Player.__init__(**locals())
    def getNextMove(self, board):
        board = self.game.getBoardState()
        return board
    def startOfGame(self):
        pass





class ComputerPlayer(Player):
    def __init__(self,sign, game):
        self.offeredMove = None # last move passed to Game
        self.dobot = Dobot(sign)
        self.dobot.connect()
        self.dobot.HomeCalibration()
        Player.__init__(**locals())

         
    def isWinner(self, matrix, playerSign):
        m = matrix
        diag = m.diagonal()
        diagFlip = np.fliplr(m).diagonal()
        #first check the diagonal if any win
        #print("cheking for winner")
        #print("matrix",matrix)
        if np.all(diag == playerSign) or np.all(diagFlip == playerSign):
            print("opportunity for diagonal win")
            status = True
        #then check all the rows and columns
        else:
            status = False
            #print("false win")
            for i in range(self.boardSize):
                col = m[i]
                row = m[:,i]
                #if all signs in the row/col are the same =win
                if np.all(col==playerSign) or np.all(row== playerSign):
                    #print("win for col rows")
                    status = True
        return status

        

    def selectRandom(self, arrayMoves):
        import random
        choice = random.choice(range(len(arrayMoves)))
        move = np.array(arrayMoves[choice])
        move = [move[0], move[1]]
        return move    

    
    def getNextMove(self, board):
        self.boardSize = np.shape(board)[0]
        #print("board size", self.boardSize)
        matrix = board.copy()
        #print("passed board", matrix)
        self.possibleMoves = np.argwhere(matrix == self.empty)
        possibleMoves = np.argwhere(matrix == self.empty)
        
        corners = [[0,0],
                   [0,self.boardSize-1],
                   [self.boardSize-1, self.boardSize-1],
                   [self.boardSize-1,0]]
        edges=[]
        for i in [0,self.boardSize-1]:
            for k in range(1,self.boardSize-1):
                point1 = [i,k]
                point2 = [k,i]
                edges.append(point1)
                edges.append(point2)
                
        cornersOpen = []
        middlePoint = []
        edgesOpen = []
        
        #check for middle point
        if (self.boardSize%2)==0:
            pass
        else:
            #get the middle point
            middle = int((self.boardSize/2)-0.5)
            middlePoint = [middle, middle]
            if (middlePoint == possibleMoves).all(-1).any(-1):
                self.move = middlePoint
                cornersOpen.append(self.move)
               
                #dont make move, just pass it to cornersOpen^^^
                #matrix[self.move[0]][self.move[1]] = self.playerSign
                #print("matrix1\n", matrix)
                #self.offeredMove = self.move
                #return matrix
        
        for k in range(len(possibleMoves)):
            position = possibleMoves[k]
            if (position==corners).all(-1).any(-1):
                cornersOpen.append(position)
            if (position==edges).all(-1).any(-1):
                edgesOpen.append(position)
                
         
        for player in [self.game.currenPlayer.playerSign, self.game.oppositePlayer.playerSign]:
            for k in range(len(possibleMoves)):
                #print("possible moves:",len(possibleMoves))
                boardCopy = matrix.copy()
                position = possibleMoves[k]
                i = position[0]
                j = position[1]
                move = [i,j]
                
                boardCopy[i,j] = player
                #print("move",move)
                #if self.spaceIsFree(move):
                #print("cheking for free space")
                if self.isWinner(boardCopy, player):
                    #print("can win in one move")
                    self.move = move
                    matrix[self.move[0]][self.move[1]] = self.playerSign
                    print("matrix2\n", matrix)
                    self.offeredMove = self.move
                    return matrix
                else:
                    pass
                
        cornersOpen = np.array(cornersOpen)       
        #print("corners open:", cornersOpen)
        edgesOpen = np.array(edgesOpen)
        #print("openedges", edgesOpen)
        
        #if not(self.isWinner(self.matrix, self.P1sign)):
        
        #go for edges
        if len(edgesOpen)>0:
            self.move = self.selectRandom(edgesOpen)
            #return self.move
        
        #go for corners
        if len(cornersOpen)>0:
            self.move = self.selectRandom(cornersOpen)
            #return self.move
            
        matrix[self.move[0]][self.move[1]] = self.playerSign
        
        print("matrix3\n", matrix)
        self.offeredMove = self.move
        return matrix

    
    def MoveApproved(self):
        if self.offeredMove != None:
            self.dobot.PlaceCupToBoard(self.offeredMove)
            self.offeredMove = None

    def requestMove(self):
        return self.move
    
    def startOfGame(self):
        pass

    def endOfGame(self):
        self.dobot.close()

