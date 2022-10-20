import threading
import os, math, sys
from PyQt6.QtCore import QSize, Qt, QObject, Signal
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton


# Subclass QMainWindow to customize your application's main window
class test_gui_dobot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        button = QPushButton("Press Me!")
        button.setCheckable(True)
        button.clicked.connect(self.button_clicked)
        # Set the central widget of the Window.
        self.setCentralWidget(button)
    def button_clicked(self):
        print("button clicked")
######RUNNING WINDOW###############
if __name__=="__main__":
    app = QApplication(sys.argv)
    window = test_gui_dobot()
    window.show()
    sys.exit(app.exec())


