import cv2
import urllib 
import numpy as np

cap = cv2.VideoCapture('http://10.111.76.25/mjpg/video.mjpg')
bytes=''

frame_counter = 0

#cv2.namedWindow('preview', cv2.WINDOW_NORMAL)


while frame_counter < 500:

    ret, frame = cap.read()

#    cv2.imshow('Video', frame) 
    frame_counter = frame_counter+1
  
    if(frame_counter % 10 == 0):
        print(frame_counter)
    


cv2.destroyAllWindows()
