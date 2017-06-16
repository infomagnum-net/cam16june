import multiprocessing
import cv2
import dlib
import time
import threading
import numpy as np
from skimage import io
from sklearn.externals import joblib
import datetime
import glob
import os
import time
import MySQLdb
import redis

redisdb = redis.Redis(host='localhost', port=6379, db=1)
mysqldb = MySQLdb.connect("localhost","root","root","zm" )
cursor = mysqldb.cursor()
detector = dlib.get_frontal_face_detector()
filepath = os.getcwd()
clf = joblib.load(filepath+'/trained_classifier.pkl')
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(filepath+"/old_shape_predictor_68_face_landmarks.dat")
facerec = dlib.face_recognition_model_v1(filepath+"/dlib_face_recognition_resnet_model_v1.dat")

#EVENTSTOVIDEO()
cam_queue = multiprocessing.Queue()

def calculatetime(time1):
    fmt='%Y-%m-%d %H:%M:%S'
    d1 = datetime.datetime.strptime(time1, fmt)
    d2_current = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(d2_current, fmt)
    d1_ts = time.mktime(d1.timetuple())
    d2_ts = time.mktime(d2.timetuple())
    restime=int(d2_ts-d1_ts) / 60
    return restime

timedict={}
def appenddict(name,imgpath,imgname,crop_img):
    current_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if name in timedict:
        if calculatetime(timedict[name])> 2:
            timedict.update({name:current_time})
            cv2.imwrite(filepath+"/static/media/detected/"+str(imgname)+".jpg",crop_img)
            cursor.execute("INSERT INTO VideoCaptured(uuid,image, status,name,occupation,created_at,updated_at) VALUES ('%s', '%s','%s', '%s', '%s','%s','%s')" % (name, imgpath, "Known",name,'',current_time,current_time))
            mysqldb.commit()
    else:
        print (name)
        timedict.update({name:datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        cv2.imwrite(filepath+"/static/media/detected/"+str(imgname)+".jpg",crop_img)
        cursor.execute("INSERT INTO VideoCaptured(uuid,image, status,name,occupation,created_at,updated_at) VALUES ('%s', '%s','%s', '%s', '%s','%s','%s')" % (name, imgpath, "Known",name,'',current_time,current_time))
        mysqldb.commit()


def EVENTS_CREATION(image):
    if (os.path.isdir("/home/zoom/Desktop/TASKS/events/"+todaystr) == True):
            cv2.imwrite("/home/zoom/Desktop/TASKS/events/"+todaystr+"/"+datetime.datetime.now().strftime('%Hh%Mm%Ss%f') + '.jpg', image)
    else :
        os.mkdir("/home/zoom/Desktop/TASKS/events/"+todaystr)
        cv2.imwrite("/home/zoom/Desktop/TASKS/events/"+todaystr+"/"+datetime.datetime.now().strftime('%Hh%Mm%Ss%f') + '.jpg', image)
    
def diffImg(t0, t1, t2):
    d1 = cv2.absdiff(t2, t1)
    d2 = cv2.absdiff(t1, t0)
    return cv2.bitwise_and(d1, d2)


def cam_feed(cam_queue):
    cap = cv2.VideoCapture("rtsp://192.168.0.16/user=admin&password=&channel=1&stream=0.sdp?")
    #cap = cv2.VideoCapture(0)
    cap1 = cap
    cap.set(3,1920)   
    cap.set(4,1080)   
    cap.set(5, 10)     
    t_minus = cv2.cvtColor(cap1.read()[1], cv2.COLOR_RGB2GRAY)
    t = cv2.cvtColor(cap1.read()[1], cv2.COLOR_RGB2GRAY)
    t_plus = cv2.cvtColor(cap1.read()[1], cv2.COLOR_RGB2GRAY)
    while(cap.isOpened()):
        ret,image = cap1.read()
        motion = diffImg(t_minus, t, t_plus)
        t_minus = t
        t = t_plus
        t_plus = cv2.cvtColor(cap1.read()[1], cv2.COLOR_RGB2GRAY)
        print (cv2.countNonZero(motion))
        if cv2.countNonZero(motion) > 400000:     # MOTION DETECTION VALUE
            ret,frame = cap.read()        
         #   fm = cv2.Laplacian(frame, cv2.CV_64F).var()    # BLUR DETECTION
            print "BEFORE MOTION DETECTION"
            # if fm > 500 :
            #     print "AFTER MOTION DETECTION",fm
            cam_queue.put(frame)
                # EVENTS_CREATION(frame)
        


def croping(img):
    
    dets1, scores, idx = detector.run(img, 1, -1)
    print scores[0]
    if scores[0] >  1.6 :
        print " IN IF ------------------------------------------"
        dets = detector(img, 1)
        print "dets"
        for k, d in enumerate(dets):
            print "in for"
            crop_img = img[(d.top()):(d.bottom()),(d.left()):(d.right())]
            predictions(crop_img)



def predictions(img1):
    imgname=(((str(datetime.datetime.now())).split(" ")[1]).replace(":","")).replace(".","")
    print "PREDECTION"
    try:
        dets = detector(img1, 1)   
        for k, d in enumerate(dets):
            cv2.imwrite("test.jpg",img1)
            shape = sp(img1, d)
            face_descriptor = facerec.compute_face_descriptor(img1, shape)
            a = face_descriptor
            vector21 = np.array(a)    
        y_pred = clf.predict(vector21)
        predictions = clf.predict_proba(vector21).ravel()
        imgpath="/static/media/detected/"+str(imgname)+".jpg"
        print predictions
        
        if ((predictions[0]*100) > 70):
            print (y_pred[0])
            appenddict(y_pred[0],imgpath,imgname,img1)

        elif ((predictions[1]*100) > 70):
            print ("same face")
            print (y_pred[0])
            appenddict(y_pred[0],imgpath,imgname,img1)

        elif ((predictions[2]*100) > 70):
            print (y_pred[0])
            appenddict(y_pred[0],imgpath,imgname,img1)

        else:
            print ("unknown")
            current_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            imgpath="/static/media/undetected/"+str(imgname)+".jpg"
            cv2.imwrite(filepath+"/static/media/undetected/"+str(imgname)+".jpg",img1)
            cursor.execute("INSERT INTO VideoCaptured(uuid,image, status,name,occupation,created_at,updated_at) VALUES ('%s', '%s','%s', '%s', '%s','%s','%s')" % (imgname, imgpath, "UnTrained","",'',current_time,current_time))
            mysqldb.commit()

    except Exception as e:
        print e.message


def from_queue():
    while True:    
        from_queue1 = cam_queue.get()
        #Prediction(from_queue1)
        croping(from_queue1)


if __name__ == "__main__":
    cam_process = multiprocessing.Process(target=cam_feed,args=(cam_queue,))
    cam_process.start()
    c2 = multiprocessing.Process(target =from_queue)
    c2.start()