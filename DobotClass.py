import sys, os, time
import dobotlib.DobotDllType as dType
import math
import numpy as np
os.add_dll_directory( os.getcwd() )

CupHeight = 100 / 4	## mm
N = 6


QM = 1
zMax = 120 #Pen tip should touch the paper
zOffset = -70	# offset in Z from home to table


#####################################################
#####################################################
#####################################################
class CoordinateSystem():
    def __init__(self):
        self.LT = np.asarray( [[1, 0], [0, 1]] )
        self.ST = np.asarray( [[0, 0], [0, 0]] )
        self.P1 = [0, 0, 0]
        self.P2 = [1, 0, 0]

    def setRotatedCS(self, P1, P2):
        self.P1 = P1
        self.P2 = P2
        rot90 = np.asarray( [[0, -1], [1, 0]] )
        shift = np.asarray( [[0, -1], [1, 0]] )
        P1a = np.asarray(self.P1[:2])
        P2a = np.asarray(self.P2[:2])
        lineVec = P2a - P1a
        lineVecUnit = lineVec / np.linalg.norm(lineVec)
        print("CS:",lineVecUnit)
        newLT = np.asarray([lineVecUnit, np.dot(rot90, lineVecUnit)]).transpose()
        self.LT = newLT
        self.ST = P1a

    def C2D(self, C):
        """Convert coordinates in shifted/rotated system into Dobot coordinates
        """
        Cxy = C[:2]
        newCxy = np.dot( self.LT, Cxy )
        newCxy = newCxy + self.ST
        newC = C.copy()
        newC[0:2] = newCxy[0:2]
        return newC

    def D2C(self, C):
        """Convert Dobot coordinates into  coordinates in shifted/rotated system
        """
        Cxy = C[:2]
        newCxy = np.dot( np.linalg.inv(self.LT), Cxy )
        newCxy = newCxy - self.ST
        newC = C.copy()
        newC[0:2] = newCxy[0:2]
        return newC

########## end of class CS



class Dobot():
    CON_STR = {
        dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
        dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
        dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

    def __init__(self):
        #Load Dll and get the CDLL object
        os.add_dll_directory( os.getcwd() )
        self.api = dType.load()
        self.lastIndex = [0, ]
        ####Coordinate systems####
        self.RedCupStorageCS = CoordinateSystem()
        self.RedCupStorageCS.setRotatedCS([-61,-250], [77.6,-250])
        self.BlueCupStorageCS = CoordinateSystem()
        self.BlueCupStorageCS.setRotatedCS([-67.9,-175.9], [67.4,-178.2])
        self.BoardCS = CoordinateSystem()
        self.BoardCS.setRotatedCS([212.1,24.4], [273.7,24.1])
        self.gap = 134/4
        self.CupHeight = 25
        self.nrBlueCupSet=0
        self.x_home, self.y_home = 200, 0
       

    def connect(self):
        #Connect Dobot
        state = dType.ConnectDobot(self.api, "", 115200)[0]
        print("Connect status:",self.CON_STR[state])
        if (state == dType.DobotConnect.DobotConnect_NoError):
            # clear all error
            self.ClearAllError()
            #Clean Command Queued
            dType.SetQueuedCmdClear(self.api)
            #Start to Execute Command Queue
            ## dType.SetQueuedCmdStartExec(self.api)
            self.firstIndex = dType.GetQueuedCmdCurrentIndex(self.api)
            self.lastIndex = self.firstIndex
            return True
        else:
            #Disconnect Dobot
            dType.DisconnectDobot(self.api)
            return False

    def WaitCommandsDone(self, timeOut = None):
        start = time.time()
        print(start)
        print("Waiting for queued operations finishing.")
        #Start to Execute Command Queue
        ## dType.SetQueuedCmdStartExec(self.api)
        #Wait for Executing Last Command 
        while self.lastIndex[0] > dType.GetQueuedCmdCurrentIndex(self.api)[0]:
            dType.dSleep(100)
            if (timeOut != None):
                print('.', end='')
                delta = time.time() - start
                print('Delta:', delta)
                if delta > timeOut:
                    return False
            ### alrm = dType.GetAlarmsState(self.api)[0]
            ### if (alrm):
            ###     print("Alarm: ", alrm)
        return True

    def Reset(self):
        #Stop to Execute Command Queued
        dType.SetQueuedCmdForceStopExec(self.api)
        #Clean Command Queued
        dType.SetQueuedCmdClear(self.api)
        self.ClearAllError()
        ## self.PickupOff()
        #Start to Execute Command Queue
        dType.SetQueuedCmdStartExec(self.api)
        self.WaitCommandsDone(2)


    def HomeCalibration(self):
        #Stop to Execute Command Queued
        dType.SetQueuedCmdForceStopExec(self.api)
        #Clean Command Queued
        dType.SetQueuedCmdClear(self.api)
        self.ClearAllError()
        x = 200
        y = 0
        z = 100
        r = 0
        self.lastIndex = dType.SetHOMEParams(self.api,  x,  y,  z,  r,  isQueued=1)
        #Async Home
        self.lastIndex = dType.SetHOMECmd(self.api, temp = 0, isQueued = 1)
        print(self.lastIndex)
#        self.PickupOn()
        self.PickupOff()
        print(self.lastIndex)
        #Wait for Executing Last Command 
        print("Waiting for homing finished:")
        dType.SetQueuedCmdStartExec(self.api)
        done = self.WaitCommandsDone(35)
        if done:
            print("Homing finished.")
        else:
            print("Homing FAILED !")
        


    def close(self):
        ## self.WaitCommandsDone(1)
        #Stop to Execute Command Queued
        dType.SetQueuedCmdForceStopExec(self.api)
        #Clean Command Queued
        dType.SetQueuedCmdClear(self.api)
        self.ClearAllError()
        #Disconnect Dobot
        dType.DisconnectDobot(self.api)

    def text_prompt(self, msg):
        try:
            return input(msg)
        except NameError:
            return input(msg)


    def setZlimit(self, z):
        dType.SetPTPJumpParams(self.api, z-zOffset, z-zOffset+20)
        #print(dType.GetPTPJumpParams(self.api))
        pass

    def MoveToPos(self, x, y, z):
        print(f"moving to posititon: {x}, {y}, {z}")
        rHead = dType.GetHOMEParams(self.api)[3]
        self.lastIndex = dType.SetPTPCmd(self.api, dType.PTPMode.PTPMOVLXYZMode, x, y, z+zOffset, rHead, isQueued=1)
        #self.lastIndex = dType.SetWAITCmd(self.api, 5, isQueued=1)

    def JumpToPos(self, x,y,z):
        print("Jumpong to positon, ",x,y,z)
        rHead = dType.GetHOMEParams(self.api)[3]
        self.lastIndex = dType.SetPTPCmd(self.api, dType.PTPMode.PTPMOVJXYZMode, x, y, z+zOffset, rHead, isQueued=1)
        #self.lastIndex = dType.SetWAITCmd(self.api, 5, isQueued=1)

    def PickupOn(self, ):
        self.lastIndex = dType.SetEndEffectorSuctionCup(self.api, 1,  1, isQueued=1)
        self.lastIndex = dType.SetWAITCmd(self.api, 150, isQueued=1)

    def PickupOff(self, ):
        self.lastIndex = dType.SetEndEffectorSuctionCup(self.api, 1,  0, isQueued=1)
        self.lastIndex = dType.SetWAITCmd(self.api, 90, isQueued=1)

    def Wait(self, waitTime):
        self.lastIndex = dType.SetWAITCmd(self.api, waitTime*1000, isQueued=1)

    def GetPosition(self):
        return dType.GetPose(self.api)[:3]

    def ClearAllError(self):
        dType.ClearAllAlarmsState(self.api)

    def hang_around(self, ):
        pass

    def printpos(self, ):
        cp = dType.GetPose(self.api)[:3]
        x, y, z = cp[0], cp[1], cp[2]
        print('Current position: {x:.0f} {y:.0f} {z:.0f}'.format(x=x, y=y, z=z))
        cp = dType.GetHOMEParams(self.api)
        x, y, z = cp[0], cp[1], cp[2]
        print('Home position: {x:.0f} {y:.0f} {z:.0f}'.format(x=x, y=y, z=z))


    def MoveColumn(self, FP, TP, N, zHeight=25, zJumpMin=0):
        moved = 0
        nextZt = (moved+1) * zHeight
        nextZf = (N) * zHeight
        for i in reversed(range(N)):
            print('Cycle:',i+1)
            nextZf = (i+1) * zHeight
            # to pale
            self.MoveToPos(FP[0], FP[1],  max(nextZf, nextZt, zJumpMin) + 10 )
            self.MoveToPos(FP[0], FP[1] , max(nextZf, nextZt, zJumpMin) + 10)
            self.MoveToPos(FP[0], FP[1],  nextZf - 1 )
            # pick
            self.PickupOn()
            # move
            nextZt = (moved+1) * zHeight
            self.MoveToPos(FP[0], FP[1], max(nextZf, nextZt, zJumpMin) + 10 )
            self.MoveToPos(TP[0], TP[1], max(nextZf, nextZt, zJumpMin) + 10 )
            self.MoveToPos(TP[0], TP[1], nextZt - 1 )
            # pick off
            self.PickupOff()
            self.MoveToPos(TP[0], TP[1], max(nextZf, nextZt, zJumpMin) + 10 )
            moved += 1


    def PickToColumn(self, TP, zN, zUnitHeight=25, zJumpMin=0):
        nextZt = zN * zUnitHeight
        # to pale
        self.MoveToPos(TP[0], TP[1],  max(nextZt,  zJumpMin) + 10 )
        self.MoveToPos(TP[0], TP[1], max(nextZt,  zJumpMin) + 5)
        self.MoveToPos(TP[0], TP[1],  nextZt - 1 )
        # pick
        self.PickupOff()
        # move
        self.MoveToPos(TP[0], TP[1],  max(nextZt, zJumpMin) + 10 )


    def PickFromColumn(self, FP, zN, zUnitHeight=25, zJumpMin=0):
        print("picking the cup...")
        nextZf = zN * zUnitHeight
        self.MoveToPos(FP[0], FP[1], max(nextZf,  zJumpMin) + 10 )
        self.MoveToPos(FP[0], FP[1], max(nextZf,  zJumpMin) + 5)
        self.MoveToPos(FP[0], FP[1], nextZf - 1 )
        # pick
        self.PickupOn()
        # move
        self.MoveToPos(FP[0], FP[1], max(nextZf, zJumpMin) + 10 )


### ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
### ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
### ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def DobotMovements(self, parCS, parCenter, parL, parN, TimeWait, parColumnN = 2, parTotalN = 6):
        
        print('*'*50)
        print("Calibration...\n")
        ### self.HomeCalibration()
        home = dType.GetHOMEParams(self.api)
        self.CupsCS = parCS
    
        #Remember current position as pale
        P1 = np.asarray(self.CupsCS.P1[:2])
        print('Point 1: ', P1)
        P2 = np.asarray(self.CupsCS.P2[:2])
        print('Point 2: ', P2)
        P3 = parCenter
        P3d = self.CupsCS.D2C(P3)
        #print('Point 3 dob: ', P3d)
        zN = parColumnN
        xN = math.ceil( parTotalN / zN )

        x0 = P3d[0] # manually place
        y0 = P3d[1] # manually place
        D = np.linalg.norm(P1 - P2)
        dx = round ( D / (xN-1))    # gap between columns

        alph = 2 * math.pi / parN
        R = parL / 2 / math.sin(alph / 2)
        print('Diam', D)
        print('Alpha', alph)
        for i in range(0, parN):  # leave sides on place
            xn = math.floor(i / zN)
            zn = zN - (i % zN) # current number in column
            print('Forw: xn=', xn,'zn=',zn)
            self.PickFromColumn(
                        self.CupsCS.C2D([ xn*dx, 0 , CupHeight]), 
                        zn,
                        zJumpMin=(zN+1)*CupHeight)

            self.PickToColumn(
                        self.CupsCS.C2D([x0+R*math.cos(alph*(i+1)), y0+R*math.sin(alph*(i+1))  , CupHeight]),     
                        1,   # in the col
                        zJumpMin=(zN+1)*CupHeight)
        self.Wait(TimeWait)
        for i in reversed(range(0, parN)):  # leave sides on place
            xn = math.floor(i / zN) # curr column number
            zn = zN - (i % zN)
            print('Backward: xn=', xn,'zn=',zn)
            self.PickFromColumn(
                        self.CupsCS.C2D([x0+R*math.cos(alph*(i+1)), y0+R*math.sin(alph*(i+1))  , CupHeight]),     
                        1,   # in the col
                        zJumpMin=(zN+1)*CupHeight)

            self.PickToColumn(
                        self.CupsCS.C2D([ xn*dx, 0 , CupHeight]), 
                        zn,
                        zJumpMin=(zN+1)*CupHeight)
        self.Wait(0.5)
        self.MoveToPos(*home[:3] )


    def PickToCircleMove(self, TP, zN, zUnitHeight=25, zJumpMin=0):
        nextZt = zN * zUnitHeight
        # to pale
        self.JumpToPos(TP[0], TP[1],  max(nextZt,  zJumpMin) + 10 )
        self.MoveToPos(TP[0], TP[1], max(nextZt,  zJumpMin) + 5)
        self.MoveToPos(TP[0], TP[1],  nextZt - 1 )
		# pick
        self.PickupOff()
		# move
        self.MoveToPos(TP[0], TP[1],  max(nextZt, zJumpMin) + 10 )


    def PickFromCircleMove(self, FP, zN, zUnitHeight=25, zJumpMin=0):
        print("picking the cup...")
        nextZf = zN * zUnitHeight
        self.JumpToPos(FP[0], FP[1], max(nextZf,  zJumpMin) + 10 )
        self.MoveToPos(FP[0], FP[1], max(nextZf,  zJumpMin) + 5)
        self.MoveToPos(FP[0], FP[1], nextZf - 1 )
        # pick
        self.PickupOn()
        # move
        self.MoveToPos(FP[0], FP[1], max(nextZf, zJumpMin) + 10 )


    def PlaceCupToBoard(self, move):
        nr = self.nrBlueCupSet
        gap = self.gap
        x = move[1]*self.gap
        y = move[0]*self.gap*-1
        zn = 1
        print("passed move:", move)
        #get the cup
        self.PickFromCircleMove(
                        self.BlueCupStorageCS.C2D([gap*nr, 0 , self.CupHeight]), 
                        zn,
                        zJumpMin=self.CupHeight+50)
        print("place cup at", [x,y])
        
        #place cup on the board
        self.PickToCircleMove(
                        self.BoardCS.C2D([x, y , self.CupHeight]), 
                        zn,
                        zJumpMin=self.CupHeight+50)

        self.JumpToPos(self.BlueCupStorageCS.C2D([gap*nr, 0 , self.CupHeight])[0],
                        self.BlueCupStorageCS.C2D([gap*nr, 0 , self.CupHeight])[1],
                        self.CupHeight+50)               
        self.nrBlueCupSet +=1


#####################################################
#####################################################
#####################################################