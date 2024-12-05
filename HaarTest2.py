# From https://medium.com/@vipulgote4/guide-to-make-custom-haar-cascade-xml-file-for-object-detection-with-opencv-6932e22c3f0e

import cv2
piece_cascade = cv2.CascadeClassifier("HaarTraining/classifier/cascade.xml")

img= cv2.imread("HaarTraining/p/20241120_144753.jpg")

resized = cv2.resize(img,(400,300))
gray = cv2.cvtColor(resized,cv2.COLOR_BGR2GRAY)
pieces = piece_cascade.detectMultiScale(gray,2,1) # Tune 6.5 and 17
print(f"{len(pieces)} were found")

for(x,y,w,h) in pieces:
    resized=cv2.rectangle(resized,(x,y),(x+w,y+h),(0,255,0),2)
cv2.imshow('img',resized)
cv2.waitKey(0)
cv2.destroyAllWindows()