from __future__ import print_function
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from skimage import io
import dlib
import glob
import os
import numpy as np
from sklearn.externals import joblib
import redis
redisdb = redis.Redis(host='localhost', port=6379, db=1)
detector = dlib.get_frontal_face_detector()
filepath = os.getcwd()
sp = dlib.shape_predictor(filepath+"/old_shape_predictor_68_face_landmarks.dat")
facerec = dlib.face_recognition_model_v1(filepath+"/dlib_face_recognition_resnet_model_v1.dat")
faces_folder_path=filepath+"/static/media/TrainingPhotos/"

def svmtrainer():
    X = []
    y = []
    for f in glob.glob(os.path.join(faces_folder_path, "*.jpg")):
        lablename = (f.split(faces_folder_path)[1]).split("-")[0]
        img=io.imread(f)
        dets = detector(img, 1)
        for k, d in enumerate(dets):
            print ("FACE DETECTED")
            shape = sp(img, d)
            face_descriptor = facerec.compute_face_descriptor(img, shape)
            a = face_descriptor
            vector2 = np.array(a)
            X.append(vector2)
            y.append(lablename)

    param_grid = {'C': [1e3, 5e3, 1e4, 5e4, 1e5],
                  'gamma': [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.1], }
    clf = GridSearchCV(SVC(kernel='rbf', class_weight='balanced', probability=True), param_grid)
    clf = clf.fit(X, y)
    joblib.dump(clf, 'trained_classifier.pkl')
    redisdb.hmset("pklstat", {"stat":"recently updated"})

