# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 16:03:27 2022

@author: kasia
"""
import numpy as np
import random
from AppCommon import VideoMode, BoardState
from DobotClass import Dobot
import tensorflow as tf
import logging
tf.autograph.set_verbosity(0)

logger = logging.getLogger("AppTicTacToe")


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
        
        Parameters
        ----------
        board : 2D-array
            current game board. 

        Returns
        -------
        Tuple or 2D-array
            return the move to Game. 
            Could be passed the move as tuple(row, col)
            or 2d-array as new board configuration.

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
        Player.__init__(**locals())
        self.MODEL_FILE = 'model-'+str(self.game.boardSize)+'.h5'
        self.MODEL_LOCAL = 'local-model-'+str(self.game.boardSize)+'.h5'
        self.randomMoves = 2
        self.offeredMove = None # last move passed to Game
        try:
            self.predict_model = tf.keras.models.load_model(self.MODEL_LOCAL)
        except:
            self.predict_model = tf.keras.models.load_model(self.MODEL_FILE)
            logger.error("Local Model loading failed, fallback to pretrained model.")
        try:
            self.dobot = Dobot(sign)
            self.dobot.connect()
            self.dobot.HomeCalibration()
        except:
            logger.warning("Dobot initialization error.")


         
    def isWinner(self, matrix, playerSign):
        m = matrix
        diag = m.diagonal()
        diagFlip = np.fliplr(m).diagonal()
        ## first check the diagonal if any win
        if np.all(diag == playerSign) or np.all(diagFlip == playerSign):
            status = True
        ## then check all the rows and columns
        else:
            status = False
            for i in range(self.boardSize):
                col = m[i]
                row = m[:,i]
                ## if all signs in the row/col are the same =win
                if np.all(col==playerSign) or np.all(row== playerSign):
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
        logger.debug("board size " + str(self.boardSize))
        matrix = board.copy()
        self.possibleMoves = np.argwhere(matrix == self.empty)
        possibleMoves = np.argwhere(matrix == self.empty)
        logger.debug("Poss moves:\n" + str(possibleMoves))
        
        ## CHECK for WIN / LOSE positions
        for player in [self.game.currenPlayer.playerSign, self.game.oppositePlayer.playerSign]:
            for k in range(len(possibleMoves)):
                boardCopy = matrix.copy()
                position = possibleMoves[k]
                i = position[0]
                j = position[1]
                move = [i,j]
                
                boardCopy[i,j] = player
                if self.isWinner(boardCopy, player):
                    matrix[move[0]][move[1]] = self.playerSign
                    self.offeredMove = move
                    return matrix
                else:
                    pass

        ## Random moves, if needed
        if self.game.moveNumber in range(self.randomMoves):
            logger.info("Computer player  "+ str(self.game.playerturn + 1) + '  made random move.')
            move = self.selectRandom(possibleMoves)
            self.offeredMove = move
            return tuple(move)
        
        ## Model prediction
        try:
            request = []
            for m in possibleMoves:
                gms = np.empty((2 * self.game.boardSize ** 2))
                gms.fill(-1+1)
                glog = [item for sublist in self.game.Log for item in sublist]
                glog = np.array(glog)
                n = len(glog)
                if n > 0:
                    gms[:n] = glog
                gms[n] = m[0] + 1
                gms[n+1] = m[1] + 1
                gms = np.expand_dims(gms, axis=0)
                request.append(gms)
            request = np.vstack(request)
            pred = self.predict_model.predict(request, batch_size=len(possibleMoves))
            logger.debug("Model return predictions:\n" + str(pred))
            pln = self.game.playerturn + 1
            mypred = np.array(pred)[:,pln]
            mi = np.argmax(mypred)
            logger.debug("Index of maximum win:" + str(mi))
            move = possibleMoves[mi]
        except:
            move = self.selectRandom(possibleMoves)
        self.offeredMove = move
        return (tuple(move))


    
    def MoveApproved(self):
        if self.offeredMove is not None:
            try:
                self.dobot.PlaceCupToBoard(self.offeredMove)
            except:
                logger.warning("Dobot move: error")
            self.offeredMove = None

    def startOfGame(self):
        pass

    def endOfGame(self):
        try:
            self.dobot.close()
        except:
            logger.warning("Dobot close: error.")
        self.TrainModel()
        pass

    def TrainModel(self):
        ## Train model using current results
        if self.game.result != None:
            glog = [item for sublist in self.game.Log for item in sublist]
            ## step-by-step log:
            AllSteps = []
            for i in range(1, ((len(glog)) // 2)): ## start from first move
                S = np.empty((2 * self.game.boardSize ** 2))
                S.fill(0)
                S[:i*2] = glog[:i*2]
                AllSteps.append(S)
                repn = i
        
            npSteps = np.array(AllSteps)
            res = np.zeros(3)
            res[self.game.result] = 1
            res = np.expand_dims(res, axis=0)
            npRes = np.repeat(res, [repn,], axis=0)
            logger.debug("Training data\n" + str(npSteps))
            logger.debug("Training results\n" + str(npRes))
            try:
                hist = self.predict_model.fit(npSteps, npRes, epochs=1)
            except:
                logger.error("Training failed!")
                return False
            try:
                acc = float(hist.history['accuracy'][0])
                self.predict_model.save(self.MODEL_LOCAL)
                logger.info("Retrained model was saved, accuracy is "+str(acc))
            except:
                logger.error("Retrained model saving failed!")
        pass


