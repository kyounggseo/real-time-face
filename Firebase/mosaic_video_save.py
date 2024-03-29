import cv2
import numpy as np
import os
import picamera as PiCamera
from time import sleep
import datetime
import sys
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from uuid import uuid4
import schedule

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('/home/kj/trainer/trainer.yml')
cascadePath = "/home/kj/face/opencv/data/haarcascades/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);
font = cv2.FONT_HERSHEY_SIMPLEX

id = 0

# 학습자 이름 출력
names = ['None', 'kyoungseo']

# 비디오 촬영 
cam = cv2.VideoCapture(0) # ngnix 서버 송출 시 rtmp://.. 주소
cam.set(3, 640) # set video widht
cam.set(4, 480) # set video height

fourcc = cv2.VideoWriter_fourcc(*'XVID')
basename = "smr"
suffix = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + '.avi' # 현재 날짜와 시간

filename = "_".join([basename, suffix])

#basename="exp"
#suffix = '.avi'
    
out =cv2.VideoWriter(filename, fourcc, 20.0, (640,480))
    
# Define min window size to be recognized as a face
minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)
 
while True:
    ret, img = cam.read()
    
    if not ret:
        print("can't read cap")
        break
    
    img = cv2.flip(img, 1) # Flip vertically
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
    faces = faceCascade.detectMultiScale( 
        gray,
        scaleFactor = 1.2,
        minNeighbors = 5,
        minSize = (int(minW), int(minH)),
       )
    
    for(x,y,w,h) in faces:
        
        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
        id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
        
        # 학습자일 경우 이름 출력
        if (confidence < 100):
            #id = names[id]
            id = "kyoungseo"
            confidence = "  {0}%".format(round(150 - confidence))
            
        # 학습자가 아닐 경우 모자이크 처리
        else: 
            id = "unknown"
            mosaic_loc = img[y:y + h, x:x + w]
            mosaic_loc = cv2.blur(mosaic_loc, (50,50))
            img_w_mosaic = img
            img_w_mosaic[y:y + h, x:x + w] = mosaic_loc
            confidence = "  {0}%".format(round(100 - confidence))
        
        cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
        cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
    
    out.write(img)
    cv2.imshow('camera',img)
    
    # 종료
    k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
    
    if k == 27:
        break
    
    # 촬영 종료후 메시지 출력
print("\n [INFO] Exiting Program and cleanup stuff")

cam.release()
out.release()
cv2.destroyAllWindows()
