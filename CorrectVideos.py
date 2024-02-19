import cv2
assert cv2.__version__[0] >= '3', 'The fisheye module requires opencv version >= 3.0.0'
import sys
import numpy as np
import os
import glob

# take in -- directory, sampling rate
script_ = sys.argv[0]
fps_ = sys.argv[1]

try:
    fps_ = float(fps_)
except TypeError:
    print('fps must be convertible to a float.')
directory_ = sys.argv[2]
#rotate_image = sys.argv[3]
#image_type = sys.argv[4]
#image_type = '*.'+image_type
#rotate_image = int(rotate_image)
#calibration_directory = 'CalibrationWall/'
## Load matricies for correcting images
K = np.load('K.npy')
D = np.load('D.npy')
DIM = np.load('DIM.npy')
# directory_ = 'D:/Behavior/VGlut1-IRES2-Cre-D/ESKO1-00031/SKO1-08765/Baseline/20240209'
## Rectify images first
# directory_ = 'D:/Panopticon/string_pull_behavior/StringPullingVideo/hm4di_female_tr_earnotch/20240111_006'
os.chdir(directory_)
file_date = directory_.split('/')[-1]
subject_id = directory_.split('/')[4]
cage_id = directory_.split('/')[3]
strain_id = directory_.split('/')[2]
experiment_type = directory_.split('/')[5]

#images = []
#images = glob.glob(image_type)

trial_ = []
videos = glob.glob('*.avi')

def ConvertVideo(v):
    orig_vid = cv2.VideoCapture(v)
    print(v)
    video_name = subject_id+'_'+experiment_type+'_'+file_date+'_T'+v.split('_')[-1]
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


for v in videos:
    ConvertVideo(v)
been_here_file = open('beenhere.txt','x')
been_here_file.close()
print('All done.')

# for t in trials:
#     if not os.path.exists(t):
#         os.mkdir(t)
#         print(t)
#     trial_images = glob.glob(t+'-*')
#     for ti in trial_images:
#         img = cv2.imread(ti)
#         if rotate_image == 1:
#             img = cv2.rotate(img, cv2.ROTATE_180)
#         fname = ti.split('-')[-1];
#         h, w = img.shape[:2];
#         map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2);
#         udimg = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT);
#         if image_type == 'png':
#             cv2.imwrite(directory_ + '/' + t + '/' + fname.split('.')[0]+'.jpg', udimg,[int(cv2.IMWRITE_JPEG_QUALITY), 100]);
#         else:
#             cv2.imwrite(directory_ + '/' + t + '/' + fname, udimg);
#     os.chdir(directory_+'/'+t)
#     images_corr = []
#     images_corr = glob.glob('*.jpg')
#     fids = []
#     for ic in images_corr:
#         fids.append(int(ic.split('.')[0]))
#     idx = np.argsort(fids)  # grab the correct indicies of the frames
#
#     filename = directory_+'/'+t+'/'+subject_id+'-'+experiment_type+'-'+file_date+'-'+t+'.avi'
#
#     # Make video
#     fourcc = cv2.VideoWriter_fourcc('F', 'M', 'P', '4')
#     video = cv2.VideoWriter(filename, fourcc, fps_,
#                             (700, 1080))  # could maybe add the filename to the camera params...?
#
#     for id_ in idx:
#         img = cv2.imread(images_corr[id_])
#         video.write(img)
#     video.release()
#     print('Video saved as {}.'.format(filename))
#     os.chdir('..')

