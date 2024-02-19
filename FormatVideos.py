import cv2
assert cv2.__version__[0] >= '3', 'The fisheye module requires opencv version >= 3.0.0'
import sys
import numpy as np
import os
import glob
import datetime
import json

def LoadFishEyeCorrections()->dict:
    corrections_dict = dict()
    corrections_dict['K'] = np.load('C:/Users/chris/BeenThere/K.npy')
    corrections_dict['D'] = np.load('C:/Users/chris/BeenThere/D.npy')
    corrections_dict['DIM'] = np.load('C:/Users/chris/BeenThere/DIM.npy')
    return corrections_dict
def SetupFiles(directory_:str)->dict:
    file_dict = dict()

    os.chdir(directory_)
    file_dict['directory'] = directory_
    file_dict['file_date'] = directory_.split('/')[-1]
    file_dict['subject_id'] = directory_.split('/')[4]
    file_dict['cage_id'] = directory_.split('/')[3]
    file_dict['strain_id'] = directory_.split('/')[2]
    file_dict['experiment_type'] = directory_.split('/')[5]
    file_dict['videos'] = glob.glob('*.avi')
    return file_dict

def CorrectVideos(file_dict: dict, corrections_dict:dict):
    processing_type = 'FishEyeCorrection'
    videos = file_dict['videos']
    corrected_videos = []
    subject_id = file_dict['subject_id']
    experiment_type = file_dict['experiment_type']
    file_date = file_dict['file_date']
    K = corrections_dict['K']
    DIM = corrections_dict['DIM']
    D = corrections_dict['D']

    for v in videos:
        orig_vid = cv2.VideoCapture(v)
        fps_ = orig_vid.get(cv2.CAP_PROP_FPS)
        print(fps_)
        print(v)
        video_name = subject_id+'_'+experiment_type+'_'+file_date+'_T'+v.split('_')[-1]
        corrected_videos.append(video_name)
        fourcc = cv2.VideoWriter_fourcc('F', 'M', 'P', '4')
        video = cv2.VideoWriter(video_name, fourcc, fps_,
                                (700, 1080))
        ret = True
        while ret:
            ret, frame = orig_vid.read()
            if ret == True:
                h,w = frame.shape[:2]
                map1, map2 = cv2.fisheye.initUndistortRectifyMap(K,D,np.eye(3),K,DIM, cv2.CV_16SC2)
                corr_frame = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
                video.write(corr_frame)
        video.release()
        orig_vid.release()
    CreateBeenHere(processing_type, corrected_videos)
    return corrected_videos

def CreateBeenHere(processing_type, files):
    current_time = str(datetime.datetime.now())
    been_here_dict = dict({'Processing': {current_time.split(' ')[0]: {'Type': processing_type, 'Date': current_time, 'Files': files}}})
    bhd_json = json.dumps(been_here_dict)
    with open('been_here.json', 'w') as bh_file:
        bh_file.write(bhd_json)

    print('All done.')





