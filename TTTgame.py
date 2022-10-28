import random, time
import numpy as np
from TTTplayer import HumanPlayer, ComputerPlayer
from AppCommon import VideoMode, BoardState
import logging
logger = logging.getLogger("AppTicTacToe")



#uncommment when use dobot code
#from DobotMovement import Dobot

class TicTacToeGame:
    def __init__(self, Player1, Player2, boardSize, nr=0):
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
        self.gameNumber = nr
        self.moveNumber = 0
        self.Log = []
        self.result = None
        
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
        self.oppositePlayer = self.players[self.playerturn+1]
        self.cheatingCounter = 0
        #choose randomly who will play first
    
    def assignPlayer(self, playerType, playerSign):
        if playerType == "human":
            playerGlobal=HumanPlayer(playerSign,self)
        elif playerType=="computer":
            playerGlobal=ComputerPlayer(playerSign,self)
        else:
            playerGlobal=HumanPlayer(playerSign,self)
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
        logger.debug("Cleaning board...")
        occupied= (np.where(abs(matrix) >self.empty))
        occupied = np.asarray(occupied).T
        return occupied
    

    def boardOccupied(self, board):
        if np.all(board==self.empty):
            logger.debug("Board: empty")
            return False
        else:
            return True
        
    def isBoardFull(self):
        logger.debug("Checking if board is full...")
        if np.any(self.Board==self.empty):
            return False
        else:
            return True
        
    def getBoardState(self):
        """
        Returns manually entered board state

        Returns
        -------
        board : 2D-array
            cups configuration.

        """
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
        logger.debug("Manualy entered board:\n" + str(board))
        return board

        
    def isWinner(self):
        logger.debug("Checking for the winner...")
        status = False
        m = self.Board
        diag = m.diagonal()
        diagFlip = np.fliplr(m).diagonal()
        ## first check the diagonal if any win
        for playerSign in [self.P1sign, self.P2sign]:
            if (np.all(diag==playerSign) or np.all(diagFlip==playerSign)):
                status = True
            ## then check all the rows and columns
            else:
                
                for i in range(self.boardSize):
                    col = m[i]
                    row = m[:,i]
                    ## if all signs in the row/col are the same =win
                    if (np.all(col==playerSign) or np.all(row==playerSign)):
                        status = True
        return status
    


    def isLastBoardStatePresent(self, newboard):
        """
        Check, that previous state of board (position and "color") is 
        present in _newboard_ array

        Parameters
        ----------
        newboard : 2D-array
            Board state to be checked.

        Returns
        -------
        result : bool
            True -- previous board state is presented in newboard.
            False -- previous board state is NOT presented in newboard
                    by any reason: "color" is changed or position is empty

        """
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
        
    def _printWarningMessage(self, msg):
        self.printWarningMessage(msg)
    def printWarningMessage(self, msg):
        if msg:
            logger.info("Game Warning: " + str(msg))

    def _printGameWinner(self):
        self.printGameWinner(self.playerturn+1)
    def printGameWinner(self, playernumber):
        logger.info("WON!!!: player" + str(playernumber) +
              str(self.currenPlayer.__class__.__name__))
        
    def _printGameTie(self):
        self.printGameTie()
    def printGameTie(self):
        logger.info("Game result is a tie.")

    def _printGameTurn(self):
        self.printGameTurn(self.playerturn+1)
    def printGameTurn(self, playernumber):
        logger.info("It's player"+ str(playernumber) + 'turn' +
              str(self.currenPlayer.__class__.__name__))
        
    def _printBoardState(self, board):
        self.printBoardState(board)
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
        logger.info (str(result))
        

    def changePlayer(self):
        self.oppositePlayer = self.players[self.playerturn]
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
            ## mask of Board state
            maskB = np.isin(self.Board, self.empty)
            ## set all old moves in NewBoard to Empty
            newB = newboard.copy()
            newB[maskB == False] = BoardState.Empty
            ## count non-empty places occupied by current player
            pc = np.count_nonzero(newB == self.currenPlayer.playerSign) 
            mcnt = np.count_nonzero(newB != self.empty)
            
            if mcnt == 1:
                logger.debug("One move made")
                if pc == 1:
                    logger.debug("Current player made the move. OK.")
                    lastOkmove = np.argwhere(newB == self.currenPlayer.playerSign)
                    lastOkmove += 1 # model / human readable
                    self.Log.append(*(lastOkmove.tolist()))
                    return True
                else:
                    logger.info("NOT current player made the move.")
                    return False
            else:
                logger.info("Not the only one move made")
                return False
         

    def requestAndCheckMove(self):
        """
        Ask Player to get a next move in game, check that move is allowed.
        If the given move is not allowed, ask Player  again.

        Returns
        -------
        bool
            True -- finaly the move is accepted.
            None -- in case the Game was interrupted
            False -- never. TODO: return False if cheating detected

        """
        while (self._run_flag==True):
            time.sleep(1)   ## hang-up protection
            newmove = self.currenPlayer.getNextMove(self.Board)
            if (isinstance(newmove, tuple)):
                boardnew = self.Board.copy()
                boardnew[newmove[0], newmove[1]] = self.currenPlayer.playerSign
            else:
                boardnew = newmove
            lastpr = self.isLastBoardStatePresent(boardnew)
            if (lastpr == True):
                self.cheatingCounter = 0
            else:
                ## Cups from last accepted board absent: not detected or cheated
                self.cheatingCounter += 1
                ## TODO:check cheating treashold
                logger.info("Previous state changed. Not-detected or cheated?")
                ## continue waiting correct move
                continue
            allowed = self.isMoveAllowed(boardnew)
            if allowed:
                self.Board = boardnew
                self.GameMoveAccepted()
                return True
            elif allowed == False:
                logger.info("move not allowed" , )
                self._printWarningMessage("Last move is wrong!")
                self.GameMoveRejected()
                continue
            else:
                logger.info("make the move!!!" + ' '*15)
                self._printWarningMessage("")
                continue
        ## in case of interrupting of game
        return None
        
    

    def startGame(self):
        """
        Main Game loop:
            Ask from player the move.
            Check for winner or tie.
            Change player
            Repeat
        At beginning wait till the board (especialy given by object detection) is empty.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        self._run_flag = True
        self.result = None
        
        
        ### TODO: Allow for second player to be the one cup on board (opposite color)
        
        ## clear the board
        while (True and self._run_flag == True):
            time.sleep(5)   ## hang-up protection
            #### call the initial state of the board ####
            board = self.getBoardState()
            self._printBoardState(board)
            
            if self.boardOccupied(board):
                self._printWarningMessage("Please, clear the board!")
                #self.DobotCleanBoard(board)
            else:
                self.Board = board
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
                logger.debug("Board is full")
                if win:
                    self.GameWin()
                else:
                    self.GameTie()
                break
            elif not(full):
                logger.debug("Board: NOT full")
                if win:
                    self.GameWin()
                    break
            logger.debug("-------------- next turn --------------")
            self.changePlayer()
            self._printGameTurn()
            self._printBoardState(self.Board)
            checkresult = self.requestAndCheckMove()
            if (checkresult == True):
                logger.debug("Move allowed")
                self.currenPlayer.MoveApproved()
                continue # game
            elif (checkresult == False):
                logger.debug("cheating detected")
                break
            else:
                logger.debug("CheckMove: interrupted.")
                break
        ## end of game-turn while cycle
        ## check game is canceled and finish game!
        if ( self._run_flag == False):
            logger.info("Game was canceled")
            self._printWarningMessage("Game canceled")
            pass
        self._printBoardState(self.Board)
        self.gameOver()
        return self.result

    def GameMoveAccepted(self):
        self.moveNumber += 1
        self.currenPlayer.MoveApproved()
        pass

    def GameMoveRejected(self):
        ### self.currenPlayer.MoveRejected()
        pass

    def GameWin(self):        
        self._printGameWinner()
        self.oppositePlayer.Loser()
        self.currenPlayer.Winner()
        self.result = self.playerturn+1

    def GameTie(self):        
        self._printGameTie()
        self.result = 0

    def gameOver(self):
        self.P1.endOfGame()
        self.P2.endOfGame()
        pass
        

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

