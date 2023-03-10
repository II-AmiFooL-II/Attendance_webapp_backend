import face_recognition
import cv2
import os
import numpy as np
from sys import getsizeof
import urllib.request as ur

def init_face(img):
    try:
    #decoded= ur.urlopen(img)
        imges = face_recognition.load_image_file(img)
        unknown_encode = face_recognition.face_encodings(imges)
        #print(getsizeof(unknown_encode[0]))
        #print(len(unknown_encode))
        if len(unknown_encode)>1:
            return -1,[]
        #np.save('test1.npy', unknown_encode[0])
        return 0,unknown_encode[0]
    except:
        return -1,[]

def compare_face(img,encode):
    try:
        imges = face_recognition.load_image_file(img)
        print("1")
        unknown_encode = face_recognition.face_encodings(imges)[0]
        print("2")
        known_encode = encode
        result = face_recognition.compare_faces([known_encode],unknown_encode)
        print(3)
        if result[0]!=True:
            print("failed")
            return 1
        return 0
    except:
        return 0
'''
train = open("train.jpg")
print(init_face(train))
print(compare_face("train.jpg",1))
'''