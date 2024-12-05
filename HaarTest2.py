# Base code from https://medium.com/@vipulgote4/guide-to-make-custom-haar-cascade-xml-file-for-object-detection-with-opencv-6932e22c3f0e

"""
Notes from 12/4/24
- It looks like the Haar classifier is performing very poorly. On both positive and negative examples, it maintains a ~10% detection rate.
- Additionally, the bounding box is far too large right now. This might be an issue with .detectMultiScale, but tuning parameters seems to affect
    both + and - equally.
- I'm not sure why Haar training is terminating if it's only identifying 10% of positive images. Maybe an issue with the tool.

> Raising haar training size to 48x32 to see if it's a resolution issue.

- I think the issue is the images' size. The problem is that the images are 4000x3000 because they were taken on a phone. I'm going to mass scale down the images
    to a more workable size.

"""

import cv2
import os
from os import listdir
from PIL import Image
PIECE_CASCADE = cv2.CascadeClassifier("HaarTraining/classifier/cascade.xml")
POSITIVE_IMAGE_PATH = "HaarTraining/p"
NEGATIVE_IMAGE_PATH = "HaarTraining/n"

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

runTestOn(POSITIVE_IMAGE_PATH, "+")

# From https://stackoverflow.com/questions/21517879/python-pil-resize-all-images-in-a-folder
def massResize(folder, targetRatio):
    for item in folder:
        if os.path.isfile(folder+item):
            im = Image.open(folder+item)
            f, e = os.path.splitext(folder+item)
            imResize = im.resize((4000 * targetRatio,3000 * targetRatio), Image.ANTIALIAS)
            imResize.save(f + ' resized.jpg', 'JPEG', quality=90)