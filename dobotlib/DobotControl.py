import threading
import DobotDllType as dType
import numpy as np
import sys, os, time

os.add_dll_directory(os.getcwd())
lastIndex = 0
#####################################################
#####################################################
#####################################################

def DobotMovements():
    home = dType.GetHOMEParams(api)

    text_prompt('Move Suction Cup over pile of cups and press Enter')
    #Remember current position as pale
    PalePos = dType.GetPose(api)[:3]
    MovedPos = PalePos.copy()
    MovedPos[1] = MovedPos[1] + 100

    text_prompt('Move Suction Cup to new place and press Enter')
    dist = 0
    while dist < 40:
        newpos = dType.GetPose(api)[:3]
        dist = np.linalg.norm(np.asarray(PalePos[:2]) - np.asarray(newpos[:2]))
    MovedPos = newpos

    dType.SetPTPJumpParams(api, PalePos[2]-zOffset, PalePos[2]-zOffset+10)
    print(dType.GetPTPJumpParams(api))
    print(dType.PTPMode.PTPMOVJXYZMode)

    MoveColumn(PalePos, MovedPos, N)



def text_prompt(msg):
    try:
        return raw_input(msg)
    except NameError:
        return input(msg)


def setZlimit(z):
	#dType.SetPTPJumpParams(api, z-zOffset, z-zOffset+20)
	#print(dType.GetPTPJumpParams(api))
	pass

def MoveToPos(x, y, z):
	rHead = dType.GetHOMEParams(api)[3]
	dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, x, y, z+zOffset, rHead, isQueued=QM)
	dType.SetWAITCmd(api, 5, isQueued=QM)

def JumpToPos(x,y,z):
	rHead = dType.GetHOMEParams(api)[3]
	dType.SetPTPCmd(api, dType.PTPMode.PTPMOVJXYZMode, x, y, z+zOffset, rHead, isQueued=QM)
	dType.SetWAITCmd(api, 5, isQueued=QM)

def PickupOn():
	dType.SetEndEffectorSuctionCup(api, 1,  1, isQueued=QM)
	dType.SetWAITCmd(api, 150, isQueued=QM)

def PickupOff():
	dType.SetEndEffectorSuctionCup(api, 1,  0, isQueued=QM)
	dType.SetWAITCmd(api, 90, isQueued=QM)

def Wait(waitTime):
	dType.SetWAITCmd(api, waitTime*1000, isQueued=QM)

def hang_around():
	pass

def printpos():
	cp = dType.GetPose(api)[:3]
	x, y, z = cp[0], cp[1], cp[2]
	print('Current position: {x:.0f} {y:.0f} {z:.0f}'.format(x=x, y=y, z=z))
	cp = dType.GetHOMEParams(api)
	x, y, z = cp[0], cp[1], cp[2]
	print('Home position: {x:.0f} {y:.0f} {z:.0f}'.format(x=x, y=y, z=z))


def MoveColumn(FP, TP, N):
	moved = 0
	nextZt = (moved+1) * CupHeight
	nextZf = (N) * CupHeight
	for i in reversed(range(N)):
		print('Cycle:',i)
		nextZf = (i+1) * CupHeight
		# to pale
		MoveToPos(FP[0], FP[1], max(nextZf, nextZt) + 10 )
		setZlimit(max(nextZf, nextZt))
		MoveToPos(FP[0],	FP[1] , max(nextZf, nextZt) + 10)
		MoveToPos(FP[0], FP[1], nextZf )
		# pick
		PickupOn()
		# move
		nextZt = (moved+1) * CupHeight
		MoveToPos(FP[0], FP[1], max(nextZf, nextZt) + 10 )
		setZlimit(max(nextZf, nextZt))
		MoveToPos(TP[0], TP[1], max(nextZf, nextZt) + 10 )
		MoveToPos(TP[0], TP[1], nextZt )
		# pick off
		PickupOff()
		MoveToPos(TP[0], TP[1], max(nextZf, nextZt) + 10 )
		moved += 1


#####################################################
#####################################################
#####################################################

CupHeight = 100 / 4	## mm
N = 4

QM = 1
zMax = 120 #Pen tip should touch the paper
zOffset = -70	# offset in Z from home to table

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

#Load Dll and get the CDLL object
api = dType.load()
#Connect Dobot
state = dType.ConnectDobot(api, "", 115200)[0]
print("Connect status:",CON_STR[state])

if (state == dType.DobotConnect.DobotConnect_NoError):
    #Clean Command Queued
    dType.SetQueuedCmdClear(api)
    dType.SetQueuedCmdStartExec(api)

    DobotMovements()

    #Start to Execute Command Queue
    dType.SetQueuedCmdStartExec(api)
    #Wait for Executing Last Command 
    while lastIndex > dType.GetQueuedCmdCurrentIndex(api)[0]:
        dType.dSleep(100)
    #Stop to Execute Command Queued
    dType.SetQueuedCmdStopExec(api)

#Disconnect Dobot
dType.DisconnectDobot(api)

