# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 10:02:55 2022

@author: ilia
"""

from PyQt6 import QtGui, QtWidgets, QtGui, QtCore, uic
import sys
import cv2
import numpy as np
import os
from enum import Enum

###########################################################
###########################################################
### Video detection classs
###########################################################
###########################################################

class VideoMode(Enum):
    Board = 1
    Original = 2
    Calibration = 3
    Detection = 4
    
class VideoThread(QtCore.QThread):
    change_pixmap_signal = QtCore.pyqtSignal(np.ndarray)
    

    def __init__(self, videoPort):
        super().__init__()
        self.videoPort = videoPort
        self._run_flag = True
        self.width = 320
        self.height = 240
        self.mode = VideoMode.Original

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(self.videoPort)
        while self._run_flag:
            image_show = self.generateImage("No video")
            ret, image_original = cap.read()
            if ret:
                image_show = image_original
                if (self.mode == VideoMode.Board):
                    image_show = self.generateImage("No board detected")
                elif (self.mode == VideoMode.Calibration):
                    image_show = self.generateImage("No calibration")
                elif (self.mode == VideoMode.Detection):
                    image_show = self.generateImage("No detection")
                    
            self.change_pixmap_signal.emit(image_show)
        # shut down capture system
        cap.release()

    def generateImage(self, text):
        blank_image = np.zeros((self.height, self.width,3), np.uint8)
        blank_image[:,:] = (128,0,0)
        font                   = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10,self.width // 2)
        fontScale              = 1
        fontColor              = (255,255,255)
        thickness              = 2
        lineType               = 2
        
        cv2.putText(blank_image,text, 
            bottomLeftCornerOfText, 
            font, 
            fontScale,
            fontColor,
            thickness,
            lineType)
        return blank_image

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

###########################################################
###########################################################
### Application classs
###########################################################
###########################################################

class AppTicTacToe(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('app.ui', self)
        ## non-resizable main window
        self.setFixedSize(self.size())
        ## icons list
        self.icons = {
            "dobot1"    : "dobot1.png",
            "dobot2"    : "dobot2.png",
            "red"       : "red.png",
            "blue"      : "blue.png",
            "empty"     : "empty.png",
            }
        self.GameSize = 3
        self.setWindowTitle("Qt tic-tac-toe game")
        self.display_width = 320
        self.display_height = 240
        ## create the label that holds the image
        self.cameraImageLabel.resize(self.display_width, self.display_height)
        self.cameraImageLabel.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.cameraImageLabel.customContextMenuRequested.connect(self.video_on_context_menu)
        
        ## Log editors for read only
        self.logPlayer1.setReadOnly(True)
        self.logPlayer2.setReadOnly(True)
        ## images on button
        self.setPlayerPic(1, 'dobot')
        self.setPlayerPic(2, 'dobot')
        self.makeGameArea()
        ## create the video capture thread
        self.threadVideo = VideoThread(0)
        ## connect its signal to the update_image slot
        self.threadVideo.change_pixmap_signal.connect(self.update_image)
        ## start the thread
        self.threadVideo.start()


    def closeEvent(self, event):
        print("Close event received.")
        self.threadVideo.stop()
        event.accept()


    def setPlayerPic(self, playernum, icon):
        path = os.path.dirname(os.path.abspath(__file__))
        lbl = self.findChild(QtWidgets.QLabel, 'lblPlayer' + str(playernum))
        lbl.setPixmap(QtGui.QPixmap(
            os.path.join(path, self.icons[icon + str(playernum)])).scaled(self.display_width, self.display_height, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        
    def btn_game_pressed(self, ):
        btn = self.sender()
        print("GameButton pressed.", 'r=', btn.row, 'c=', btn.col)
#        self.setGameButtonIcon(btn, "red")
        pass

        

    def setGameButtonIcon(self, btn, icon):
        ico = QtGui.QIcon(self.icons[icon])
        btn.setIcon(ico)
        btn.setIconSize(btn.size())
        pass


    def makeGameArea(self):
        ## delete all existed buttons
        for i in reversed(range(self.gameLayout.count())): 
            self.gameLayout.itemAt(i).widget().setParent(None)
        ## create buttons
        for c in range(self.GameSize):
            for r in range(self.GameSize):
                btn = QtWidgets.QPushButton("")
                btn.setFixedSize(100,100)
                self.setGameButtonIcon(btn, "empty")
                btn.clicked.connect(self.btn_game_pressed)
                btn.row = r
                btn.col = c
                self.gameLayout.addWidget(btn, r, c)
                pass
            

    def video_on_context_menu(self, pos):
        contextMenu = QtWidgets.QMenu(self)
        Acts = []
        for i, mode in enumerate(VideoMode):
            act = QtGui.QAction(mode.name, self)
            act.modeToSwitch = mode
            Acts.append(act)
            
        contextMenu.addActions(Acts)
        action = contextMenu.exec(self.cameraImageLabel.mapToGlobal(pos))   ## contextMenu for cameraImageLabel only, so use it for position search
        ## pass action to video class
        if action != None:
            self.setVideoSource(action.modeToSwitch)

    def setVideoSource(self, mode):
        print("setVideoSource: mode=", mode)
        self.threadVideo.mode = mode
        
        

    @QtCore.pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.cameraImageLabel.setPixmap(qt_img)


    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        return QtGui.QPixmap.fromImage(p)
    
if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    a = AppTicTacToe()
    a.show()
    sys.exit(app.exec())