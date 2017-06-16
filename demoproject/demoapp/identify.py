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
import string,MySQLdb

mysqldb = MySQLdb.connect("localhost","root","root","zm" )
cursor = mysqldb.cursor()
detector = dlib.get_frontal_face_detector()
cam_queue = multiprocessing.Queue()
filepath = os.getcwd()
clf = joblib.load('/home/zoom/Desktop/15-06-17/demoproject/demoapp/trained_classifier.pkl')
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor("/home/zoom/Desktop/15-06-17/demoproject/demoapp/old_shape_predictor_68_face_landmarks.dat")
facerec = dlib.face_recognition_model_v1("/home/zoom/Desktop/15-06-17/demoproject/demoapp/dlib_face_recognition_resnet_model_v1.dat")
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
        if calculatetime(timedict[name])>5:
            timedict.update({name:current_time})
            cv2.imwrite(filepath+"/static/media/detected/"+str(imgname)+".jpg",crop_img)
            cursor.execute("INSERT INTO VideoCaptured(uuid,image, status,name,occupation,created_at,updated_at) VALUES ('%s', '%s','%s', '%s', '%s','%s','%s')" % (name, imgpath, "Known",name,'',current_time,current_time))
            mysqldb.commit()
        else:
            print ("lessthan 5 mins")
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
        if cv2.countNonZero(motion) > 600000:
            ret,frame = cap.read()        
            print "in queue"
            cam_queue.put(frame)
            # EVENTS_CREATION(frame)

def croping(img):
    imgname=(((str(datetime.datetime.now())).split(" ")[1]).replace(":","")).replace(".","")
    print "PREDECTION"
    try:
        dets = detector(img, 1)
        
        for k, d in enumerate(dets):
            crop_img = img[(d.top()):(d.bottom()),(d.left()):(d.right())]
            shape = sp(crop_img, d)
            face_descriptor = facerec.compute_face_descriptor(crop_img, shape)
            a = face_descriptor
            print a
            vector21 = np.array(a)

        y_pred = clf.predict(vector21)
        predictions = clf.predict_proba(vector21).ravel()
        imgpath="/static/media/detected/"+str(imgname)+".jpg"

        if ((predictions[0]*100) > 63):
            print ("same face")
            appenddict(y_pred[0],imgpath,imgname,crop_img)

        elif ((predictions[1]*100) > 63):
            print ("same face")
            appenddict(y_pred[0],imgpath,imgname,crop_img)

        elif ((predictions[2]*100) > 63):
            appenddict(y_pred[0],imgpath,imgname,crop_img)

        else:
            print ("unknown")
            current_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            imgpath="/static/media/undetected/"+str(imgname)+".jpg"
            cv2.imwrite(filepath+"/static/media/undetected/"+str(imgname)+".jpg",crop_img)
            cursor.execute("INSERT INTO VideoCaptured(uuid,image, status,name,occupation,created_at,updated_at) VALUES ('%s', '%s','%s', '%s', '%s','%s','%s')" % (imgname, imgpath, "UnTrained","",'',current_time,current_time))
            mysqldb.commit()
            # try:
            #     cursor.execute("INSERT INTO VideoCaptured(uuid,image, status,name,occupation,created_at,updated_at) VALUES ('%s', '%s','%s', '%s', '%s','%s','%s')" % (imgname, imgpath, "UnTrained","",'',current_time,current_time))
            #     mysqldb.commit()
            # except Exception as e:
            #     mysqldb = MySQLdb.connect("localhost","root","root","zm" )
            #     cursor = mysqldb.cursor()
            #     cursor.execute("INSERT INTO VideoCaptured(uuid,image, status,name,occupation,created_at,updated_at) VALUES ('%s', '%s','%s', '%s', '%s','%s','%s')" % (imgname, imgpath, "UnTrained","",'',current_time,current_time))
            #     mysqldb.commit()
            #     print '*************'
            #     print e.message

    except Exception as e:
        print e.message


def from_queue():
    while True:    
        from_queue1 = cam_queue.get()
        croping(from_queue1)

if __name__ == "__main__":
    cam_process = multiprocessing.Process(target=cam_feed,args=(cam_queue,))
    cam_process.start()
    c2 = multiprocessing.Process(target =from_queue)
    c2.start()
