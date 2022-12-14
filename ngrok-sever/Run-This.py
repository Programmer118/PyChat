from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QFontDatabase, QIcon, QKeySequence
from PyQt5.QtCore import Qt, QSize    
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
# from PyQt5.QtGui import *
from PyQt5.uic import loadUiType

import os,sys
from threading import Thread


FROM_MAIN, _ = loadUiType(os.path.join(os.path.dirname(__file__),"untitled.ui"))

def clicked():
    os.system('python livein.py')
def click():
    os.system("start chump.py")

class Main(QMainWindow,FROM_MAIN):

    def __init__(self,parent=None):
        super(Main,self).__init__(parent)
        self.setupUi(self)

        self.setWindowIcon(QIcon("avatar1.png"))

        self.movie = QtGui.QMovie("gifloader.gif")
        self.loading.setMovie(self.movie)
        self.movie.start()

        # self.screen_width, self.screen_height = self.geometry().width(), self.geometry().height()
        # self.resize(self.screen_width * 2, self.screen_height * 2) 

        fixedFont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixedFont.setPointSize(12)

        self.server.setFont(fixedFont)
        self.client.setFont(fixedFont)

        self.server.clicked.connect(self.threading1)
        self.client.clicked.connect(self.threading2)


    def threading1(self):
        # Call work function
        t1=Thread(target=clicked)
        t1.start()
        self.label.setText("SERVER RUNNING...")
    def threading2(self):
        # Call work function
        t1=Thread(target=click)
        t1.start()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.show()
    exit(app.exec_())