# From https://medium.com/analytics-vidhya/haar-cascades-explained-38210e57970d

import numpy as np
import cv2
piece_cascade = cv2.CascadeClassifier("HaarTraining/classifier/cascade.xml")

img = cv2.imread("HaarTesting/p1.jpg")
img = cv2.resize(img, (0,0), fx=0.008, fy=0.008) 
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

pieces = piece_cascade.detectMultiScale(gray, 1.3, 5)
print(len(pieces))
for (x,y,w,h) in pieces:
    img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)

cv2.imshow('img',img)
cv2.waitKey(0)
cv2.destroyAllWindows()