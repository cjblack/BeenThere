import sys

from PyQt6.QtMultimedia import QMediaPlayer, QVideoFrame
from PyQt6.QtMultimediaWidgets import QVideoWidget
#from PyQt5.QtWidgets import QAction
from PyQt6.QtGui import * #QIcon, QAction
from PyQt6.QtCore import *
from PyQt6.QtWidgets import QFormLayout, QSlider, QDockWidget, QApplication, QLabel, QWidget, QFileDialog, QPushButton, QVBoxLayout, QMenuBar, QMainWindow, \
    QTreeWidget, QTreeWidgetItem
import FormatVideos as FVid
import os
import glob
import datetime
import cv2
import numpy as np
import json
import subprocess
from datetime import datetime
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
        self.setGeometry(100,100,1000,800)
        self.CreateMenuBar()
        self.folders_for_analysis = []
        #self.treeDicts = dict()
        self.isCorrected = False
        self.dock = QDockWidget('File Selector')
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        self.tree = QTreeWidget()
        layout = QFormLayout(self.tree)
        self.tree.setLayout(layout)
        self.tree.setHeaderLabels(['Directory'])
        self.dock.setWidget(self.tree)
        self.tree.selectionModel().selectionChanged.connect(self.CurrentIndex)

        vidLayout = QVBoxLayout()

        self.vidPlayer = VideoPlayer()
        self.startButton = QPushButton('Start')
        self.startButton.clicked.connect(self.vidPlayer.PlayVideo)

        self.pauseButton = QPushButton('Pause')
        self.pauseButton.clicked.connect(self.vidPlayer.PauseVideo)
        self.stopButton = QPushButton('Stop')
        self.stopButton.clicked.connect(self.vidPlayer.StopVideo)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.vidPlayer.SetPosition)
        self.vidPlayer.mediaPlayer.positionChanged.connect(self.PositionChanged)
        self.vidPlayer.mediaPlayer.durationChanged.connect(self.DurationChanged)

        vidLayout.addWidget(self.vidPlayer)
        vidLayout.addWidget(self.startButton)
        vidLayout.addWidget(self.pauseButton)
        vidLayout.addWidget(self.stopButton)
        vidLayout.addWidget(self.slider)

        container = QWidget()
        container.setLayout(vidLayout)
        self.setCentralWidget(container)
        self.show()
        self.videoFormats = ['mp4', 'avi'] # add others...

    def PositionChanged(self, position):
        self.slider.setValue(position)
    def DurationChanged(self, duration):
        self.slider.setRange(0,duration)

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
        filesSubMenu = editMenu.addMenu('&Files')

        removeFilesAction = QAction('Remove', self)
        removeFilesAction.setStatusTip('Remove marked files')
        removeFilesAction.triggered.connect(self.RemoveFiles)
        filesSubMenu.addAction(removeFilesAction)

        selectFilesAction = QAction('Select', self)
        selectFilesAction.setStatusTip('Select files for processing')
        selectFilesAction.triggered.connect(self.ProcessFiles)
        filesSubMenu.addAction(selectFilesAction)

        ## Analysis menu
        analysisMenu = menuBar.addMenu('&Analysis')
        videoSubMenu = analysisMenu.addMenu('&Video')

        correctVideosAction = QAction('Correct Fisheye', self)
        correctVideosAction.setStatusTip('Corrects video for fisheye distortion')
        correctVideosAction.triggered.connect(self.CorrectIt2)
        videoSubMenu.addAction(correctVideosAction)

        rotateVideosAction = QAction('Rotate Video', self)
        rotateVideosAction.setStatusTip('Rotates video 90 degrees clockwise')
        rotateVideosAction.triggered.connect(self.RotateIt)
        videoSubMenu.addAction(rotateVideosAction)

        ## Help menu
        helpMenu = menuBar.addMenu('&Help')

    def RemoveFiles(self):
        checked = dict()
        root = self.tree.invisibleRootItem()
        signal_count = root.childCount()
        for i in range(signal_count):
            signal = root.child(i)
            checked_sweeps = list()
            num_children = signal.childCount()
            for n in range(num_children):
                child = signal.child(n)
                if child.checkState(0) == Qt.CheckState.Checked:
                    checked_sweeps.append(child)

            for child in checked_sweeps:
                child.parent().removeChild(child)

            #checked[signal.text(0)]=checked_sweeps
        #print(checked)
    def ProcessFiles(self):
        '''
        Get id's of files selected in folder view
        :return:
        '''
        self.analysisDict = dict()
        self.parentDict = dict()
        root = self.tree.invisibleRootItem()
        signal_count = root.childCount()
        for i in range(signal_count):
            signal = root.child(i)
            checked_sweeps = list()
            num_children = signal.childCount()
            for n in range(num_children):
                child = signal.child(n)
                if child.checkState(0) == Qt.CheckState.Checked:
                    checked_sweeps.append(child.text(0))
            self.analysisDict[signal.text(0)]=checked_sweeps
            self.parentDict[signal.text(0)] = signal
            print(signal)
        print(self.analysisDict)
        print(self.parentDict)

    def TestIt(self):
        print('Test it.')
    def CorrectIt(self):
        '''
        Check if folders have been corrected and then will correct the videos in them
        :return:
        '''
        print('Correcting...')
        self.ProcessFiles()
        self.corrected_file_dict = dict()
        if len(self.folders_for_analysis) != 0:
            for folder_ in self.folders_for_analysis:
                os.chdir(folder_)
                # if len(glob.glob('been_here.json')) != 0:
                #     print('Just checking for now...')
                #     #break
                # else:
                corrections_dict = FVid.LoadFishEyeCorrections()
                file_dict = FVid.SetupFiles(folder_)
                corrected_file_names = FVid.CorrectVideos(file_dict, corrections_dict)
                self.corrected_file_dict[folder_] = corrected_file_names
        self.isCorrected = True

        return self.corrected_file_dict # dont actually need this since it is part of the class

    def CorrectIt2(self):
        '''
        Check if folders have been corrected and then will correct the videos in them
        :return:
        '''
        print('Correcting...')
        self.ProcessFiles()
        self.corrected_file_dict = dict()
        corrections_dict = FVid.LoadFishEyeCorrections()
        if len(self.analysisDict) != 0:
            for folder, videos in self.analysisDict.items():
                os.chdir(folder)
                # if len(glob.glob('been_here.json')) != 0:
                #     print('Just checking for now...')
                #     #break
                # else:
                file_dict = FVid.SetupFiles(folder)
                file_dict['videos'] = videos # monkey patch this for the moment
                corrected_file_names = FVid.CorrectVideos(file_dict, corrections_dict)
                self.corrected_file_dict[folder] = corrected_file_names
        self.isCorrected = True
        self.UpdateTreeParent()
        return self.corrected_file_dict  # dont actually need this since it is part of the class

    def RotateIt(self):
        '''

        :return:
        '''
        print('Rotating...')
        self.ProcessFiles()
        self.corrected_file_dict = dict()
        if len(self.analysisDict) != 0:
            for folder, videos in self.analysisDict.items():
                os.chdir(folder)

    def SCPIt(self):
        '''
        This will eventually SCP files to a specific location on a remote server.
        :return:
        '''
        self.ProcessFiles()
        now_ = datetime.now()
        prefix_='C:/Behavior/'
        now_str = now_.strftime("%Y%m%d-%H-%M-%S")
        param_file_name = prefix_+now_str+'_vfa.txt'
        json_file_name = prefix_+now_str+'_vfa.json'
        param_dict = dict()
        if len(self.analysisDict) != 0:
            files_to_send = list()
            for folder, videos in self.analysisDict.items():
                for video in videos:
                    files_to_send.append(video)
                    fname = folder+'/'+video
                    print('Running SCP for {}'.format(fname))
                    tfiles.SCPToServer(fname, 'C:/Users/chris/BeenThere/sendoff.json')
            len_files_to_send = str(len(files_to_send))
            # Create param file to store video files for array analysis on computing cluster
            f = open(param_file_name,'w')
            f.write(len_files_to_send+'\n')
            for file in files_to_send:
                f.write(file+'\n')
            f.close()
            tfiles.SCPToServer(param_file_name, 'C:/Users/chris/BeenThere/sendoff.json')
            param_dict['count'] = len_files_to_send
            param_dict['files'] = files_to_send
            json_f = open(json_file_name,'w')
            json.dump(param_dict,json_f)
            json_f.close()
            tfiles.SCPToServer(json_file_name, 'C:/Users/chris/BeenThere/sendoff.json')

        #if self.isCorrected == True:
            #for folder in self.corrected_file_dict:
                #for file_ in self.corrected_file_dict[folder]:
                    #fname = folder+'/'+file_
                    #print('Running SCP for {}'.format(fname))
                    #tfiles.SCPToServer(fname,'C:/Users/chris/BeenThere/sendoff.json')
    def OpenDialog(self):
        '''

        :return:
        '''
        self.treeDicts = dict()
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
        self.UpdateTree()

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
        #self.tree = QTreeWidget()

        for key,values in self.treeDicts.items():
            item = QTreeWidgetItem([key])
            item.setCheckState(0,Qt.CheckState.Unchecked)
            for value in values:
                child = QTreeWidgetItem([value])
                child.setCheckState(0,Qt.CheckState.Unchecked)
                item.addChild(child)
            self.tree.addTopLevelItem(item)
        #self.tree.show()
        #self.setCentralWidget(self.tree)

        self.tree.selectionModel().selectionChanged.connect(self.CurrentIndex)
    def UpdateTree(self):
        #self.tree = QTreeWidget()

        for key,values in self.treeDicts.items():
            item = QTreeWidgetItem([key])
            item.setCheckState(0,Qt.CheckState.Unchecked)
            for value in values:
                child = QTreeWidgetItem([value])
                child.setCheckState(0,Qt.CheckState.Unchecked)
                item.addChild(child)
            self.tree.addTopLevelItem(item)

    def UpdateTreeParent(self):
        for key, values in self.corrected_file_dict.items():

            parent = self.parentDict[key]
            print(parent)
            for value in values:
                child = QTreeWidgetItem([value])
                child.setCheckState(0, Qt.CheckState.Unchecked)
                parent.insertChild(0,child)
                #parent.addChild(child)
                #print('Adding {}'.format(value))
            #self.tree.addTopLevelItem(parent)

    def CurrentIndex(self):
        parent = self.tree.selectionModel().currentIndex().parent().data()
        child = self.tree.selectionModel().currentIndex().data()
        if type(parent) == str and type(child) == str:
            path = parent+'/'+child
            print('Location is {}'.format(parent))
            print('Video is {} '.format(child))
            if child.split('.')[-1] in self.videoFormats:
                self.vidPlayer.SetSource(path)
                self.vidPlayer.PlayVideo()
            else:
                print('Please select a video')
        else:
            print('Not a valid selection')
class VideoPlayer(QVideoWidget):
    def __init__(self):
        super().__init__()
        self.mediaPlayer = QMediaPlayer()

    def SetSource(self, source):
        self.mediaPlayer.setSource(QUrl.fromLocalFile(source))
        self.mediaPlayer.setVideoOutput(self)
        self.currentVideo = source

    def PlayVideo(self):
        self.mediaPlayer.play()
    def StopVideo(self):
        self.mediaPlayer.stop()
    def PauseVideo(self):
        self.mediaPlayer.pause()

    def SetPosition(self, position):
        self.mediaPlayer.setPosition(position)

class FrameGrabber(QVideoFrame):
    def __init__(self):
        super().__init__()
        print('nothing')


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
                # if len(glob.glob('been_here.json')) != 0:
                #     print('This folder has been visited already...')
                #     #break
                # else:
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