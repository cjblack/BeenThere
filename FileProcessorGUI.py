import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QFileDialog, QPushButton, QVBoxLayout
import FormatVideos as FVid
import os
import glob
import datetime
import cv2
import numpy as np
import json
import subprocess
import TransferFiles as tfiles

##
class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.folders_for_analysis = []
        self.setWindowTitle('Folder selector')
        self.setGeometry(100,100,280,80)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.folder_button = QPushButton('Select folders.', self)
        self.folder_button.clicked.connect(self.OpenDialog)
        layout.addWidget(self.folder_button)


        self.print_button = QPushButton('Print it.', self)
        self.print_button.clicked.connect(self.PrintIt)
        layout.addWidget(self.print_button)

        self.correct_video_button = QPushButton('Correct it.', self)
        self.correct_video_button.clicked.connect(self.CorrectIt)
        layout.addWidget(self.correct_video_button)

        self.clear_folders_button = QPushButton('Clear it.', self)
        self.clear_folders_button.clicked.connect(self.ClearIt)
        layout.addWidget(self.clear_folders_button)

        self.scp_files_button = QPushButton('SCP it.', self)
        self.scp_files_button.clicked.connect(self.SCPIt)

    def SCPIt(self):
        '''
        This will eventually SCP files to a specific location on a remote server.
        :return:
        '''
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
        return self.corrected_file_dict # dont actually need this since it is part of the class






app = QApplication([])
window=Window()
window.show()
sys.exit(app.exec())