# Base code from https://medium.com/@vipulgote4/guide-to-make-custom-haar-cascade-xml-file-for-object-detection-with-opencv-6932e22c3f0e

import cv2
import os
from os import listdir
from PIL import Image, ImageOps
PIECE_CASCADE = cv2.CascadeClassifier("HaarTraining/classifier/cascade.xml")
POSITIVE_IMAGE_PATH = "HaarTraining/p"
NEGATIVE_IMAGE_PATH = "HaarTraining/n"

# Haars and shows bbox for an image.
def bboxDisplay(imagePath):
    img = cv2.imread(imagePath)
    resized = cv2.resize(img,(400,300))
    gray = cv2.cvtColor(resized,cv2.COLOR_BGR2GRAY)

    pieces = PIECE_CASCADE.detectMultiScale(gray, 2, 4)

    renderPieceBBoxes(img, pieces)
    showShortcut(img)

def checkImageForPiece(imagePath):
    img = cv2.imread(imagePath)
    resized = cv2.resize(img,(400,300))
    gray = cv2.cvtColor(resized,cv2.COLOR_BGR2GRAY)

    pieces = PIECE_CASCADE.detectMultiScale(gray, 2, 4)
    
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

# From https://stackoverflow.com/questions/21517879/python-pil-resize-all-images-in-a-folder
def massResize(folder):
    for item in os.listdir(folder):
        print(item)
        path = folder + "/" + item

        if os.path.isfile(path):
            im = Image.open(path)
            im = ImageOps.exif_transpose(im)
            f, e = os.path.splitext(path)
            imResize = im.resize((800, 600), Image.BILINEAR)
            imResize.save(f + "_resize.jpg", 'JPEG', quality=90)
            
def clearResizes(folder):
    for item in os.listdir(folder):
        path = folder + "/" + item
        if item.count("resize") > 0:
            os.remove(path)

def clearNonResizes(folder):
    for item in os.listdir(folder):
        path = folder + "/" + item
        if item.count("resize") == 0:
            os.remove(path)

def clearWrongFiles(folder):
    for item in os.listdir(folder):
        path = folder + "/" + item
        if item.count(".") == 0:
            print(item)
            os.remove(path)

#runTestOn(NEGATIVE_IMAGE_PATH, "+")
#massResize(POSITIVE_IMAGE_PATH)
#clearResizes(POSITIVE_IMAGE_PATH)
#clearNonResizes(POSITIVE_IMAGE_PATH)
#clearWrongFiles(POSITIVE_IMAGE_PATH)
            
def showAllIn(folder):
    for item in os.listdir(folder):
        path = folder + "/" + item
        bboxDisplay(path)

showAllIn(POSITIVE_IMAGE_PATH)
        