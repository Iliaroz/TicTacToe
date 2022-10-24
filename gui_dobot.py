import threading
import os, math, sys
from PyQt6.QtCore import QSize, Qt, QObject
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from DobotClass import Dobot


# Subclass QMainWindow to customize your application's main window
class test_gui_dobot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dobot = Dobot()
        self.dobot.connect()
        self.dobot.HomeCalibration()
        self.setWindowTitle("My App")
        button = QPushButton("Press Me!")
        button.setCheckable(True)
        button.clicked.connect(self.button_clicked)
        # Set the central widget of the Window.
        self.setCentralWidget(button)
    def button_clicked(self):
        print("button clicked")#
        move = [0,1]
        self.dobot.PlaceCupToBoard(move)
######RUNNING WINDOW###############
if __name__=="__main__":
    app = QApplication(sys.argv)
    window = test_gui_dobot()
    window.show()
    sys.exit(app.exec())


