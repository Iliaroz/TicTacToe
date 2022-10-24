import random, time
import numpy as np
from TTTplayer import HumanPlayer, ComputerPlayer
#uncommment when use dobot code
#from DobotMovement import Dobot

class TicTacToeGame:
    def __init__(self, Player1, Player2, boardSize):
        """
        

        Parameters
        ----------
        Player1 : "human" or "computer" values.
        Player2 : "human" or "computer" values.
        boardSize : int value of board size.

        Returns
        -------
        None.

        """
        #uncommment when use dobot code
        #self.Dobot = Dobot()
        self._run_flag = False
        self.empty = 0
        self.P1sign = int(1)
        self.P2sign = int(-1)
        self.boardSize = boardSize
        
        #### ASSIGN PLAYERS ####
        self.P1 = self.assignPlayer(Player1,self.P1sign)
        self.P2 = self.assignPlayer(Player2,self.P2sign)
        ####                ####
        
        # self.P1 = Player1(self.P1sign, self)
        # self.P2 = Player2(self.P2sign, self)
        self.players = [self.P1, self.P2]
        self.playerturn = 0
        #choose randomly who will play first
        #random.shuffle(self.players)  
    
    def assignPlayer(self, playerType, playerSign):
        if playerType == "human":
            playerGlobal=HumanPlayer(playerSign,self)
        elif playerType=="computer":
            playerGlobal=ComputerPlayer(playerSign,self)
        return playerGlobal
      
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
        time.sleep(2)
        matrix = board.copy()
        print("Cleaning board...")
        occupied= (np.where(abs(matrix) >self.empty))
        occupied = np.asarray(occupied).T
        return occupied
    
    def dobotMoveCupTo(self, move):
        """
        Function receive board place to move cup using dobot

        Parameters
        ----------
        move : point coordinate.
        """
        #self.Dobot.makeMove(move)
        pass


    def boardOccupied(self, board):
        if np.all(board==self.empty):
            print("Board: empty")
            return False
        else:
            return True
        
    def isBoardFull(self):
        print("Checking if board is full...")
        if np.any(self.board==self.empty):
            return False
        else:
            return True
        
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
        print("Checking for the winner...")
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
        old = self.oldboard
        new = board
        if np.array_equal(old, new):
            print("No move detected")
            time.sleep(2)
            return None
        else:
            print("Is move allowed?")
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
                print("One move made")
                if p1>=2 or p2>=2:
                    print("more than one change in board was detected")
                    return False
                elif p1==1 or p2==1:
                    return True
         
    def requestAndCheckMove(self):
        player = self.players[self.playerturn]
        while True:
            time.sleep(5)
            #print("player", player)
            #player.giveBoard(self.board)
            #print("pass board to player:", self.board)
            boardnew = player.makeMove(self.board)
            allowed = self.isMoveAllowed(boardnew)
            if allowed:
                #print("saving board...")
                # move = player.requestMove()
                # self.dobotMoveCupTo(move)
                self.board = boardnew
                return True
                break
            elif allowed==False:
                print("move not allowed")
                break
            elif allowed==None:
                print("make the move!!!")
                continue
            print("----pass----")
        
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
        
    def printGameWinner(self):
        self.changePlayer()
        print("WON!!!: player",self.playerturn+1,
              self.players[self.playerturn].__class__.__name__)
        
    def printGameTie(self):
        print("Game result is a tie.")
        
    def printGameTurn(self):
        print("It's player",self.playerturn+1,"turn",
              self.players[self.playerturn].__class__.__name__)
        
    def printBoardState(self,board):
        """
        print board

        Parameters
        ----------
        board : 2D array.
        """
        matrix = board.copy()
        print("BOARD")
        for row in range(self.boardSize):
            r = matrix[row].tolist()
            for col in range(self.boardSize):
                if r[col]==self.empty:
                    r[col]=" "
                if r[col]==self.P1sign:
                    r[col]="O"
                if r[col]==self.P2sign:
                    r[col]="X"
            print(np.array(r))
        #print("BOARD\n",matrix)
        

    def changePlayer(self):
        if self.playerturn==0:
            self.playerturn =1
        elif self.playerturn==1:
            self.playerturn =0
    

    def startGame(self):
        self._run_flag = True
        
        ## clear the board
        while (True and self._run_flag == True):
            #### call the initial state of the board ####
            time.sleep(2)
            self.boardState = self.getBoardState()
            self.printBoardState(self.boardState)
            
            if self.boardOccupied(self.boardState):
                self.printWarningMessage("Please, clear the board!")
                print("Board occupied")
                #self.DobotCleanBoard(self.boardState)
            else:
                self.board = self.boardState
                break
        print("================= GAME STARTED =================")
        
        while (True and self._run_flag == True):
            self.oldboard = self.board.copy()
            time.sleep(10)
            print("-------------- next turn --------------")
            self.printGameTurn()
            self.printBoardState(self.board)
            f = self.isBoardFull()
            w = self.isWinner()
            #self.printGameTurn()
            if f:
                print("Board is full")
                if w:
                    #print("win")
                    self.printGameWinner()
                    break
                else:
                    self.printGameTie()
                    break
            elif not(f):
                print("Board: NOT full")
                if w:
                    #print("win")
                    self.printGameWinner()
                    break
                else:
                    print("...good to continue...")
                    
                    if self.requestAndCheckMove():
                        print("Move allowed")
                        #change player
                        self.changePlayer()
                        continue
                    else:
                        print("cheating detected")
                        break
        if ( self._run_flag == False):
            print("Game was canceled")
            self.printWarningMessage("Game canceled")
                    
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


    type1 = "human"
    type2 = "computer"

    #game instance create:
    game = TicTacToeGame(type2, type2, 3)
    #start game
    game.startGame()

