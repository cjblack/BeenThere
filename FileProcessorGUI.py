import sys

#from PyQt5.QtWidgets import QAction
from PyQt6.QtGui import * #QIcon, QAction
from PyQt6.QtCore import *
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QFileDialog, QPushButton, QVBoxLayout, QMenuBar, QMainWindow, \
    QTreeWidget, QTreeWidgetItem
import FormatVideos as FVid
import os
import glob
import datetime
import cv2
import numpy as np
import json
import subprocess
import TransferFiles as tfiles
import glob

##

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Been There.')
        #widget1 = Window()
        #self.setFixedSize(400,300)
        #self.setCentralWidget(widget1)
        self.CreateMenuBar()
        self.folders_for_analysis = []
        self.treeDicts = dict()
        self.isCorrected = False
    def CreateMenuBar(self):
        menuBar = QMenuBar(self)
        self.setMenuBar(menuBar)

        ## File menu
        fileMenu = menuBar.addMenu('&File')
        selectFoldersAction = QAction('&Select Folders', self)
        selectFoldersAction.setStatusTip('Select folders for running analysis.')
        selectFoldersAction.triggered.connect(self.OpenDialog)
        fileMenu.addAction(selectFoldersAction)
        # SCP options
        scpFilesAction = QAction('SCP Files', self)
        scpFilesAction.setStatusTip('SCP files to destination in sendoff.json')
        scpFilesAction.triggered.connect(self.SCPIt)
        fileMenu.addAction(scpFilesAction)


        ## Edit menu
        editMenu = menuBar.addMenu('&Edit')
        clearFoldersAction = QAction('&Clear Folders', self)
        clearFoldersAction.setStatusTip('Clear folders currently in memory')
        clearFoldersAction.triggered.connect(self.ClearIt)
        editMenu.addAction(clearFoldersAction)

        ## Analysis menu
        analysisMenu = menuBar.addMenu('&Analysis')
        videoSubMenu = analysisMenu.addMenu('&Video')

        correctVideosAction = QAction('Correct Fisheye', self)
        correctVideosAction.setStatusTip('Corrects video for fisheye distortion')
        correctVideosAction.triggered.connect(self.CorrectIt)
        videoSubMenu.addAction(correctVideosAction)

        ## Help menu
        helpMenu = menuBar.addMenu('&Help')
    def TestIt(self):
        print('Test it.')
    def CorrectIt(self):
        '''
        Check if folders have been corrected and then will correct the videos in them
        :return:
        '''
        print('Correcting...')
        self.corrected_file_dict = dict()
        if len(self.folders_for_analysis) != 0:
            for folder_ in self.folders_for_analysis:
                os.chdir(folder_)
                if len(glob.glob('been_here.json')) != 0:
                    break
                else:
                    corrections_dict = FVid.LoadFishEyeCorrections()
                    file_dict = FVid.SetupFiles(folder_)
                    corrected_file_names = FVid.CorrectVideos(file_dict, corrections_dict)
                    self.corrected_file_dict[folder_] = corrected_file_names
        self.isCorrected = True

        return self.corrected_file_dict # dont actually need this since it is part of the class


    def SCPIt(self):
        '''
        This will eventually SCP files to a specific location on a remote server.
        :return:
        '''
        if self.isCorrected == True:
            for folder in self.corrected_file_dict:
                for file_ in self.corrected_file_dict[folder]:
                    fname = folder+'/'+file_
                    print('Running SCP for {}'.format(fname))
                    tfiles.SCPToServer(fname,'C:/Users/chris/BeenThere/sendoff.json')
        print('I dont do anything yet.')
    def OpenDialog(self):
        '''

        :return:
        '''
        self.dialog = QFileDialog()
        folder = self.dialog.getExistingDirectory(None, 'Select a folder')
        print(folder)
        self.folders_for_analysis.append(folder)
        fileStore = []
        for file in os.listdir(folder):
            if file.endswith('.avi'):
                fileStore.append(file)
        self.treeDicts[folder] = fileStore.copy()
        fileStore.clear()
        self.MakeTree()

    def PrintIt(self):
        '''
        Just prints the folders_for_analysis path
        :return:
        '''
        print(self.folders_for_analysis)
    def ClearIt(self):
        '''
        Simply clears folders_for_analysis in case you made a mistake...
        :return:
        '''
        self.folders_for_analysis = []
    def MakeTree(self):
        self.tree = QTreeWidget()

        for key,values in self.treeDicts.items():
            item = QTreeWidgetItem([key])
            item.setCheckState(0,Qt.CheckState.Unchecked)
            for value in values:
                child = QTreeWidgetItem([value])
                child.setCheckState(0,Qt.CheckState.Unchecked)
                item.addChild(child)
            self.tree.addTopLevelItem(item)
        self.tree.show()
        self.setCentralWidget(self.tree)

        self.tree.selectionModel().selectionChanged.connect(self.TestIt)


class Tree(QTreeWidget):
    def __init__(self):
        super().__init__()

class Window(QWidget):
    def __init__(self):
        super().__init__()


        self.folders_for_analysis = []


        self.setWindowTitle('Been There.')
        self.setGeometry(100,100,280,80)


        layout = QVBoxLayout()
        self.setLayout(layout)


        self.folder_button = QPushButton('Select folders.', self)
        self.folder_button.clicked.connect(self.OpenDialog)
        layout.addWidget(self.folder_button)


        self.print_button = QPushButton('Print it.', self)
        self.print_button.clicked.connect(self.PrintIt)
        layout.addWidget(self.print_button)

        self.isCorrected = False
        self.correct_video_button = QPushButton('Correct it.', self)
        self.correct_video_button.clicked.connect(self.CorrectIt)
        layout.addWidget(self.correct_video_button)

        self.clear_folders_button = QPushButton('Clear it.', self)
        self.clear_folders_button.clicked.connect(self.ClearIt)
        layout.addWidget(self.clear_folders_button)

        self.scp_files_button = QPushButton('SCP it.', self)
        self.scp_files_button.clicked.connect(self.SCPIt)
        layout.addWidget(self.scp_files_button)

    def SCPIt(self):
        '''
        This will eventually SCP files to a specific location on a remote server.
        :return:
        '''
        if self.isCorrected == True:
            for folder in self.corrected_file_dict:
                for file_ in self.corrected_file_dict[folder]:
                    fname = folder+'/'+file_
                    print('Running SCP for {}'.format(fname))
                    tfiles.SCPToServer(fname,'C:/Users/chris/BeenThere/sendoff.json')
        print('I dont do anything yet.')

    def ClearIt(self):
        '''
        Simply clears folders_for_analysis in case you made a mistake...
        :return:
        '''
        self.folders_for_analysis = []
    def OpenDialog(self):
        '''

        :return:
        '''
        self.dialog = QFileDialog()
        folder = self.dialog.getExistingDirectory(None, 'Select a folder')
        print(folder)
        self.folders_for_analysis.append(folder)
    def PrintIt(self):
        '''
        Just prints the folders_for_analysis path
        :return:
        '''
        print(self.folders_for_analysis)

    def CorrectIt(self):
        '''
        Check if folders have been corrected and then will correct the videos in them
        :return:
        '''
        print('Correcting...')
        self.corrected_file_dict = dict()
        if len(self.folders_for_analysis) != 0:
            for folder_ in self.folders_for_analysis:
                os.chdir(folder_)
                if len(glob.glob('been_here.json')) != 0:
                    break
                else:
                    corrections_dict = FVid.LoadFishEyeCorrections()
                    file_dict = FVid.SetupFiles(folder_)
                    corrected_file_names = FVid.CorrectVideos(file_dict, corrections_dict)
                    self.corrected_file_dict[folder_] = corrected_file_names
        self.isCorrected = True
        return self.corrected_file_dict # dont actually need this since it is part of the class





app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
# app = QApplication([])
# window=Window()
# window.show()
# sys.exit(app.exec())