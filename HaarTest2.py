# Base code from https://medium.com/@vipulgote4/guide-to-make-custom-haar-cascade-xml-file-for-object-detection-with-opencv-6932e22c3f0e

import cv2
import os
from os import listdir
PIECE_CASCADE = cv2.CascadeClassifier("HaarTraining/classifier/cascade.xml")
POSITIVE_IMAGE_PATH = "HaarTraining/p"
NEGATIVE_IMAGE_PATH = "HaarTraining/n"

def checkImageForPiece(imagePath):
    img = cv2.imread(imagePath)
    resized = cv2.resize(img,(400,300))
    gray = cv2.cvtColor(resized,cv2.COLOR_BGR2GRAY)

    pieces = PIECE_CASCADE.detectMultiScale(gray, 1.6, 4) \
    
    return len(pieces) > 0

    
# Adds the bboxes of given pieces on an image 
def renderPieceBBoxes(image, pieces):
    for(x,y,w,h) in pieces:
        image = cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
    
def showShortcut(image):
    cv2.imshow('img',image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def runTestOn(folder, expected):
    positive = 0
    negative = 0
    for image in os.listdir(folder):
        if checkImageForPiece(folder + "/" + image) > 0:
            positive += 1
            print(f"{expected} test returned +")
        else:
            negative += 1
            print(f"{expected} test returned -")
    
    print(f"## {expected} TEST DONE: {positive} + / {negative} - \t\t => {positive / (positive + negative)} % pos")

runTestOn(NEGATIVE_IMAGE_PATH, "+")