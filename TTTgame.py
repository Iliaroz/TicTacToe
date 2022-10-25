import random, time
import numpy as np
from TTTplayer import HumanPlayer, ComputerPlayer
from AppCommon import VideoMode, BoardState

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
        self.empty = BoardState.Empty
        self.P1sign = BoardState.Blue  # (1)
        self.P2sign = BoardState.Red   # (-1)
        self.boardSize = boardSize
        self.Board = np.empty((self.boardSize, self.boardSize), dtype=BoardState)
        self.Board.fill(BoardState.Empty)
        
        #### ASSIGN PLAYERS ####
        self.P1 = self.assignPlayer(Player1,self.P1sign)
        self.P2 = self.assignPlayer(Player2,self.P2sign)
        ####                ####
        
        self.players = [self.P1, self.P2]
        self.playerturn = 0
        self.currenPlayer = self.players[self.playerturn]
        self.cheatingCounter = 0
        #choose randomly who will play first
    
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
        if np.any(self.Board==self.empty):
            return False
        else:
            return True
        
    def getBoardState(self):
        rows = []
        for r in range(self.boardSize):
            row = np.empty(self.boardSize)
            rowstr = input("row "+str(r+1)+ " [br ]: ")
            rowstr = rowstr.upper()
            for i in range(self.boardSize):
                try:
                    c = rowstr[i]
                except:
                    c = ' '
                if (c == 'B'):
                    row[i] = self.P1sign
                elif (c == 'R'):
                    row[i] = self.P2sign
                else:
                    row[i] = self.empty
            rows.append(row)
        board = np.array(rows)
        print("Manualy entered board:\n", board)
        return board

        
    def isWinner(self):
        print("Checking for the winner...")
        status = False
        m = self.Board
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


    def isLastBoardStatePresent(self, newboard):

        ## mask of Board state
        maskB = np.isin(self.Board, [self.P1sign, self.P2sign])
        ## set all new moves in NewBoard to Empty
        newB = newboard.copy()
        newB[maskB == False] = BoardState.Empty
        ## compare (Board) to (NewBoard w/o addings)
        eqB = np.equal(self.Board, newB)
        result = np.all( eqB )
        return result
        pass

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
        print("WON!!!: player",self.playerturn+1,
              self.currenPlayer.__class__.__name__)
        
    def printGameTie(self):
        print("Game result is a tie.")
        
    def printGameTurn(self):
        print("It's player",self.playerturn+1,"turn",
              self.currenPlayer.__class__.__name__)
        
    def printBoardState(self, board):
        """
        print board

        Parameters
        ----------
        board : 2D array.
        """
        result = '-' * (self.boardSize*3 + 2)
        for row in range(self.boardSize):
            r = board[row].tolist()
            S = "|"
            for col in range(self.boardSize):
                if r[col] == BoardState.Blue: # P1sign = blue
                    S += " X "
                elif r[col] == BoardState.Red:    # P2sign = red
                    S += " O "
                else:
                    S += " . "
            S += '|'
            result += '\n'
            result += S
        result += '\n'
        result += '-' * (self.boardSize*3 + 2)
        print (result)
        

    def changePlayer(self):
        if self.playerturn == 0:
            self.playerturn = 1
        else:
            self.playerturn = 0
        self.currenPlayer = self.players[self.playerturn]


    def isMoveAllowed(self, newboard):
        """
        decides wheter the move is allowed

        Parameters
        ----------
        board : 2D array.

        Returns
        -------
        bool
            True or False, None if no move
        """
        if np.array_equal(self.Board, newboard):
            return None
        else:
            print("Is move allowed?")
            print("\n new board\n", newboard)
                    
            ## mask of Board state
            maskB = np.isin(self.Board, self.empty)
            ## set all old moves in NewBoard to Empty
            newB = newboard.copy()
            newB[maskB == False] = BoardState.Empty
            ## count non-empty places occupied by current player
            pc = np.count_nonzero(newB == self.currenPlayer.playerSign) 
            mcnt = np.count_nonzero(newB != self.empty)
            
            if mcnt == 1:
                print("One move made")
                if pc == 1:
                    print("Current player made the move. OK.")
                    return True
                else:
                    print("NOT current player made the move.")
                    return False
            else:
                print("Not the only one move made")
                return False
         

    def requestAndCheckMove(self):
        while (self._run_flag==True):
            time.sleep(1)   ## hang-up protection
            boardnew = self.currenPlayer.makeMove(self.Board)
            lastpr = self.isLastBoardStatePresent(boardnew)
            if (lastpr == True):
                self.cheatingCounter = 0
            else:
                ## Cups from last accepted board absent: not detected or cheated
                self.cheatingCounter += 1
                ## TODO:check cheating treashold
                print("\rPrevious state changed. Not-detected or cheated?", end='')
                ## continue waiting correct move
                continue
            allowed = self.isMoveAllowed(boardnew)
            if allowed:
                self.Board = boardnew
                return True
            elif allowed == False:
                print("\rmove not allowed" + ' '*15, end='')
                continue
            else:
                print("\rmake the move!!!" + ' '*15, end='')
                continue
        ## in case of interrupting of game
        return None
        
    

    def startGame(self):
        self._run_flag = True
        
        ## clear the board
        while (True and self._run_flag == True):
            time.sleep(5)   ## hang-up protection
            #### call the initial state of the board ####
            self.boardState = self.getBoardState()
            self.printBoardState(self.boardState)
            
            if self.boardOccupied(self.boardState):
                self.printWarningMessage("Please, clear the board!")
                print("Board occupied")
                #self.DobotCleanBoard(self.boardState)
            else:
                self.Board = self.boardState
                break
        print("================= GAME STARTED =================")
        
        ## fake change, player changes at begin of turn
        self.changePlayer()
        while (True and self._run_flag == True):
            time.sleep(1)   ## hang-up protection
            ## check winner and full board
            full = self.isBoardFull()
            win = self.isWinner()
            if full:
                print("Board is full")
                if win:
                    self.printGameWinner()
                else:
                    self.printGameTie()
                break
            elif not(full):
                print("Board: NOT full")
                if win:
                    self.printGameWinner()
                    break
            print("-------------- next turn --------------")
            self.changePlayer()
            self.printGameTurn()
            self.printBoardState(self.Board)
            checkresult = self.requestAndCheckMove()
            if (checkresult == True):
                print("Move allowed")
                continue # game
            elif (checkresult == False):
                print("cheating detected")
                break
            else:
                print("CheckMove: interrupted.")
                break
        ## end of game-turn while cycle
        if ( self._run_flag == False):
            print("Game was canceled")
            self.printWarningMessage("Game canceled")
        self.gameOver()

        
    def gameOver(self):
        self.P1.endOfGame()
        self.P2.endOfGame()
        

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
    type2 = "human"

    #game instance create:
    game = TicTacToeGame(type2, type2, 3)
    #start game
    game.startGame()

