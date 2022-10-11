#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np


# In[2]:


#Tic Tac Toe game in python
### hold the board, check the move possibilities
class startGame:
    def __init__(self, boardSize):
        self.empty = 0
        self.boardSize = boardSize
        self.P1 = HumanPlayer(boardSize = self.boardSize)
        self.P2 = CompPlayer(boardSize = self.boardSize)
        self.matrix = np.array([[self.empty]*self.boardSize]*self.boardSize)
        self.P1sign = int(-1)
        self.P2sign = int(1)
        
    def printBoard(self):
        print(self.matrix)
        
    def insertSign(self, playerSign, position):
        col,row=position[0],position[1]
        self.matrix[col][row] = playerSign

    def spaceIsFree(self, position):
        col,row=position[0],position[1]
        return self.matrix[col][row] == self.empty

    def isWinner(self, matrix, playerSign):
        m = matrix
        diag = m.diagonal()
        diagFlip = np.fliplr(m).diagonal()
        #first check the diagonal if any win
        if (np.all(diag==playerSign) or np.all(diagFlip==playerSign)):
            status = True
        #then check all the rows and columns
        else:
            status = False
            for i in range(self.boardSize):
                col = m[i]
                row = m[:,i]
                #if all signs in the row/col are the same =win
                if (np.all(col==playerSign) or np.all(row==playerSign)):
                    status = True

        return status
               
    def isBoardFull(self, matrix):
        if np.all(matrix==[self.P1sign,self.P2sign]):
            return True
        else:
            return False
        
    def isMatrixFull(self):
        if self.matrix.count('0') > 1:
            print("not full matrix")
            return False
        else:
            print("not full")
            return True
        self.isMatrixFull(self)

    def main(self):
        print('Welcome to Tic Tac Toe!')

        while not(self.isBoardFull(self.matrix)):
            if not(self.isWinner(self.matrix, self.P2sign)):
                try:
                    self.P1move = self.P1.makeMove()
                except ValueError or EOFError as e:
                    print(e)
                    continue
                else:
                    self.insertSign(self.P1sign, self.P1move)
                    
                    self.P2.getMove(self.P1sign,self.P1move)
                    self.P1.insertSign(self.P1sign, self.P1move)
                    self.printBoard()
               
            else:
                print('Sorry, O\'s won this time!')
                break

            if not(self.isWinner(self.matrix, self.P1sign)):
                self.P2move = self.P2.makeMove()
                if self.P2move ==[-1,-1]:
                    print('Tie Game!')
                else:
                    self.P1.getMove(self.P2sign,self.P2move)
                    self.insertSign(self.P2sign, self.P2move)
                    print('Computer placed an \'O\' in position', self.P2move , ':')
                    self.P2.insertSign(self.P2sign, self.P2move)
            else:
                print('X\'s won this time! Good Job!')
                break

        if self.isBoardFull(self.matrix):
            print('Tie Game!')


# In[3]:


## instance of player
class Player:
    def __init__(self, boardSize):
        self.board = [' ' for x in range(10)]
        self.boardSize = boardSize
        self.matrix = np.array([[0]*self.boardSize]*self.boardSize)
        self.empty = 0
        self.P1sign = int(-1)
        self.P2sign = int(1)
            
    def isWinner(self, matrix, playerSign):
        m = matrix
        diag = m.diagonal()
        diagFlip = np.fliplr(m).diagonal()
        #first check the diagonal if any win
        #print("cheking for winner")
        #print("matrix",matrix)
        if np.all(diag== playerSign) or np.all(diagFlip==playerSign):
            print("win almost diag")
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
    
    def insertSign(self, playerSign, position):
        col,row=position[0],position[1]
        self.matrix[col][row] = playerSign
               
    def spaceIsFree(self, position):
        col,row=position[0],position[1]
        return self.matrix[col][row] == self.empty 
    
    def makeMove(self):
        pass
    
    def getMove(self, playerSign, getmove):
        self.insertSign(playerSign, getmove)
        
    def selectRandom(self, arrayMoves):
        import random
        choice = random.choice(range(len(arrayMoves)))
        move = np.array(arrayMoves[choice])
        move = [move[0], move[1]]
        return move


# In[4]:


class HumanPlayer(Player):
    def __init__(self,boardSize):
        super().__init__(boardSize)
    def makeMove(self):
        print("HumanPlayerBoard: \n",self.matrix)
        try:
            self.move = humanMakeMove().move()
            self.move = [int(self.move[0]), int(self.move[1])]
            print("move typed:",self.move, type(self.move))
            
            if self.spaceIsFree(self.move):
                run = False
            else:
                print('Sorry, this space is occupied!')
                pass
        except:
            print('Please type a number!')
            pass
            
        return self.move


# In[5]:


class CompPlayer123(Player):
    def __init__(self,boardSize):
        super().__init__(boardSize) 
    def makeMove(self):
        #print("CompPlayerBoard: ",self.matrix)
        board = self.matrix
        possibleMoves =  np.argwhere(self.matrix == self.empty)
        corners = [[0,0],[0,self.boardSize-1],
                   [self.boardSize-1, self.boardSize-1],
                  [self.boardSize-1,0]]
        edges=[]
        
        for i in [0,self.boardSize-1]:
            for k in range(1,self.boardSize-1):
                point1 = [i,k]
                point2 = [k,i]
                edges.append(point1)
                edges.append(point2)
            
        #print("edges:",edges)
        cornersOpen = []
        middlePoint = [0,0]
        edgesOpen = []
        
        #check for middle point
        if (self.boardSize%2)==0:
            pass
        else:
            #get the middle point
            middle = int((self.boardSize/2)-0.5)
            middlePoint = [middle, middle]
            
        for k in range(len(possibleMoves)):
            boardCopy =self.matrix
            position = possibleMoves[k]
            i = position[0]
            j = position[1]
            move = [i,j]
            if (position==corners).all(-1).any(-1):
                cornersOpen.append(position)
                
            if (position==edges).all(-1).any(-1):
                edgesOpen.append(position)
                
            if (middlePoint==possibleMoves).all(-1).any(-1):
                self.move = middlePoint
                return self.move
            
            if self.spaceIsFree(move):
                if self.isWinner(boardCopy, self.P2sign):
                    self.move = i
                    return self.move
                
        cornersOpen = np.array(cornersOpen)       
        #print("corners open:", cornersOpen)
        edgesOpen = np.array(edgesOpen)
        #print("openedges", edgesOpen)
        
        #go for corners
        if len(cornersOpen)>0:
            self.move = self.selectRandom(cornersOpen)
            return self.move
        
        #go for edges
        if len(edgesOpen)>0:
            self.move = self.selectRandom(edgesOpen)
            return self.move
        
        return self.move


# In[6]:


class humanMakeMove:
    def __init__(self):
        self.input1 = input("put move 1:")
        self.input2 = input("put move 2:")
    def move(self):
        return self.input1, self.input2


# In[7]:


class CompPlayer(Player):
    def __init__(self,boardSize):
        super().__init__(boardSize) 
    def makeMove(self):
        #print("CompPlayerBoard: ",self.matrix)
        #board = self.matrix
        self.possibleMoves = np.argwhere(self.matrix == self.empty)
        possibleMoves = np.argwhere(self.matrix == self.empty)
        
        corners = [[0,0],[0,self.boardSize-1],
                   [self.boardSize-1, self.boardSize-1],
                  [self.boardSize-1,0]]
        edges=[]
        for i in [0,self.boardSize-1]:
            for k in range(1,self.boardSize-1):
                point1 = [i,k]
                point2 = [k,i]
                edges.append(point1)
                edges.append(point2)
                
        #print("possible moves",possibleMoves)
        #print("edges:",edges)
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
            if (middlePoint==possibleMoves).all(-1).any(-1):
                self.move = middlePoint
                return self.move
        
        for k in range(len(possibleMoves)):
            position = possibleMoves[k]
            if (position==corners).all(-1).any(-1):
                cornersOpen.append(position)
            if (position==edges).all(-1).any(-1):
                edgesOpen.append(position)
                
        self.move=[-1,-1]   
        for player in [self.P2sign, self.P1sign]:
            for k in range(len(possibleMoves)):
                #print("possible moves:",len(possibleMoves))
                boardCopy = self.matrix.copy()
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
                    return self.move
                else:
                    pass
                
        cornersOpen = np.array(cornersOpen)       
        #print("corners open:", cornersOpen)
        edgesOpen = np.array(edgesOpen)
        #print("openedges", edgesOpen)
        
        #if not(self.isWinner(self.matrix, self.P1sign)):
        #go for corners
        if len(cornersOpen)>0:
            self.move = self.selectRandom(cornersOpen)
            #return self.move

        #go for edges
        if len(edgesOpen)>0:
            self.move = self.selectRandom(edgesOpen)
            #return self.move
        
        return self.move


# In[ ]:


matrixSize = 5

startGame(boardSize=matrixSize).main()


# In[ ]:




