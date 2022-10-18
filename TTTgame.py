import random
import numpy as np
from TTTplayer import HumanPlayer, ComputerPlayer

class TicTacToeGame:
    def __init__(self, Player1, Player2, boardSize):
        self.empty = 0
        self.P1sign = int(1)
        self.P2sign = int(-1)
        self.boardSize = boardSize
        self.P1 = Player1(self.P1sign)
        self.P2 = Player2(self.P2sign)
        self.players = [self.P1, self.P2]
        #choose randomly who will play first
        #random.shuffle(self.players)  
        
      
    def DobotCleanBoard(self, board):
        """
        Function request initial board state 
        and returns position of accupied spaces

        Parameters
        ----------
        board : 2D arrray.

        Returns
        -------
        occupied : 2D array of occupied places.

        """
        matrix = board.copy()
        print("cleaning board")
        occupied= (np.where(abs(matrix) >self.empty))
        occupied = np.asarray(occupied).T
        return occupied
    
    def boardOccupied(self, board):
        if np.all(board==self.empty):
            print("board empty")
            return False
        else:
            return True
        
    def isBoardFull(self):
        print("checking if board is full")
        if np.all(self.board==[self.P1sign,self.P2sign]):
            return True
        else:
            return False
        
    def getBoardState(self):
        board_empty =  [
                 [0,0,0],
                 [0,0,0],
                 [0,0,0]]
        return np.array(board_empty)
        ## manually input
        val1 = int(input("val1: "))
        val2 = int(input("val2: "))
        val3 = int(input("val3: "))
        
        row1 = np.array([val1,val2,val3])
        val4 = int(input("val4: "))
        val5 = int(input("val5: "))
        val6 = int(input("val6: "))
        row2 = np.array([val4,val5,val6])
        val7 = int(input("val7: "))
        val8 = int(input("val8: "))
        val9 = int(input("val9: "))
        row3 = np.array([val7,val8,val9])
        
        board = np.array([row1,row2,row3])
        return board
        
    def isWinner(self):
        print("checking for the winner")
        status = False
        m = self.board
        diag = m.diagonal()
        diagFlip = np.fliplr(m).diagonal()
        #first check the diagonal if any win
        for playerSign in [self.P1sign, self.P2sign]:
            if (np.all(diag==playerSign) or np.all(diagFlip==playerSign)):
                status = True
            #then check all the rows and columns
            else:
                
                for i in range(self.boardSize):
                    col = m[i]
                    row = m[:,i]
                    #if all signs in the row/col are the same =win
                    if (np.all(col==playerSign) or np.all(row==playerSign)):
                        status = True
        return status
    
    def Empty(self,b):
        """
        checks for empty spaces

        Parameters
        ----------
        b : 2D array.

        Returns
        -------
        Empty : 2D array of empty spaces.

        """
        EmptySpaces = np.where(b==self.empty)
        Empty = np.ones(b.shape, bool)
        Empty[EmptySpaces]=False
        return Empty
    def Occupied(self,b,sign):
        """
        checks occupied spaces

        Parameters
        ----------
        b : 2D array - board.
        playersign: player sign

        Returns
        -------
        Occupied : returns occupied spaces.

        """
        OccupiedSpaces = np.where(b==sign)
        Occupied = np.ones(b.shape, bool)
        Occupied[OccupiedSpaces]=False
        return Occupied
    
    def isMoveAllowed(self, board):
        """
        decides wheter the move is allowed

        Parameters
        ----------
        board : 2D array.

        Returns
        -------
        bool
            True or False

        """
        print("checking if move is allowed")
        old = self.oldboard
        new = board
        print("old board\n", old, "\n new board\n", new)
                
        empty_old = self.Occupied(old, self.empty)
        p1_old = self.Occupied(old, self.P1sign)
        p2_old = self.Occupied(old, self.P2sign)
        empty_new = self.Occupied(new, self.empty)
        p1_new = self.Occupied(new, self.P1sign)
        p2_new = self.Occupied(new, self.P2sign)
        
        p1comparison = (p1_old==p1_new)
        p2comparison = (p2_old==p2_new)
        emptycomparison = (empty_old==empty_new)
        
        ec = np.where(emptycomparison==False)
        p1c = np.where(p1comparison==False)
        p2c = np.where(p2comparison==False)
        
        e = np.shape(ec)[1]
        p1 = np.shape(p1c)[1]
        p2 = np.shape(p2c)[1]
        
        if e>=2:
            print("more than one move done")
            return False
        elif e==1:
            print("one empt space taken")
            if p1>=2 or p2>=2:
                print("more than one change in roder was detected")
                return False
            elif p1==1 or p2==1:
                return True
         
    def requestAndCheckMove(self, player):
        try:
            print("player", player)
            #player.giveBoard(self.board)
            print("pass board to player:", self.board)
            boardnew = player.makeMove(self.board)
            if self.isMoveAllowed(boardnew):
                print("writing to board")
                self.board = boardnew
                return True
            else:
                print("move not allowed")
                pass
        except:
            print("pass,,,")
        
    def _full(self):
        f = (input("full ?: "))
        if f=="y":
            return True
        elif f=="n":
            return False
    def _win(self):
        w = (input("win ?:"))
        if w =="y":
            return True
        elif w == "n":
            return False
        
        
    def printWarningMessage(self, msg):
        print("Game Warning: ", msg)
        
    def printGameWinner(self, player):
        print("!!!player ", player.__class__.__name__," won!!!")
        
    def printGameTie(self):
        print("Game result is a tie.")
        
    def printGameTurn(self,player):
        print("its player ", player.__class__.__name__," turn")
        
    def printBoardState(self,board):
        """
        print board

        Parameters
        ----------
        board : 2D array.
        """
        matrix = (board.copy())
        print("board",matrix)
        

    def changePlayer(self, player):
        if player==self.players[0]:
            player=self.players[1]
        elif player==self.players[1]:
            player=self.players[0]
        return player
    

    def startGame(self):
        print("players",self.players)
        player = self.players[0]
        ## clear the board
        while True:
            #### call the initial state of the board ####
            self.boardState = self.getBoardState()
            print("board: ", self.boardState)
            
            if self.boardOccupied(self.boardState):
                self.printWarningMessage("Please, clear the board!")
                print("board occupied")
                self.DobotCleanBoard(self.boardState)
            else:
                self.board = self.boardState
                break
        print("=================  start a game =================")
        
        while True:
            print("-------------- next turn --------------")
            self.printBoardState(self.board)
            self.oldboard = self.board.copy()
            f = self.isBoardFull()
            w = self.isWinner()
            
            if f:
                print("full board")
                if w:
                    print("win")
                    player = self.changePlayer(player)
                    self.printGameWinner(player)
                    break
                else:
                    print("tie")
                    self.printGameTie()
                    break
            elif not(f):
                print("not full board")
                if w:
                    print("win")
                    player = self.changePlayer(player)
                    self.printGameWinner(player)
                    break
                else:
                    print("kepp playing")
                    self.printGameTurn(player)
                    
                    if self.requestAndCheckMove(player):
                        print("move is good")
                        #change player
                        player = self.changePlayer(player)
                        self.printGameTurn(player)
                        continue
                    else:
                        print("cheating detected")
                        break
                    
                    
##################### START GAME #####################

if (__name__ == "__main__"):
    board_empty =  [
             [0,0,0],
             [0,0,0],
             [0,0,0]]

    board_test = [
             [0,0,0],
             [0,1,1],
             [0,0,-1]]


    typePlayer1 = ComputerPlayer
    typePlayer2 = ComputerPlayer

    #game instance create:
    game = TicTacToeGame(typePlayer1, typePlayer2, 3)
    #start game
    game.startGame()

