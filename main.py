import cv2
import urllib 
import numpy as np

#config Data
camera_IP = '10.111.76.25'


#Global Data
targetAreas = []
targetXs = []
targetYs = []
targetHeights = []
targetWidths = []

#Processing algorithm
def img_process(img):
    hsv_thres_lower = np.array([0,0,117])
    hsv_thres_upper = np.array([180,255,255])
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv_mask = cv2.inRange(hsv, hsv_thres_lower, hsv_thres_upper)
    

    contours, hierarchy = cv2.findContours(hsv_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_KCOS)

    for c in contours:

        area = cv2.contourArea(c)
        x, y, w, h = cv2.boundingRect(c)


        if (area > 150 and          #Min Area
               w < 100 and          #Max Width
               h < 1000):           #Max Height

            #Calculate Center of image
            x += w / 2.0
            y += h / 2.0
            targetAreas.append(area)
            targetHeights.append(h)
            targetWidths.append(w)
            targetXs.append(x)
            targetYs.append(y)




#Main Method
stream = urllib.urlopen('http://'+camera_IP+'/mjpg/video.mjpg')
bytes = ''


frame_counter = 0

#cv2.startWindowThread()
#cv2.namedWindow('Video', cv2.WINDOW_NORMAL)


while frame_counter < 300:

    bytes += stream.read(16384)
    b = bytes.rfind('\xff\xd9')
    a = bytes.rfind('\xff\xd8', 0, b-1)
    if a != -1 and b != -1:
        jpg = bytes[a:b+2]
        bytes = bytes[b+2:]
        img = cv2.imdecode(np.fromstring(jpg, dtype = np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
        
        targetAreas = []
        targetXs = []
        targetYs = []
        targetHeights = []
        targetWidths = []

        img_process(img)
        
        # cv2.imshow('Video', proc_img) 
        print("Area: " + " | ".join(map(str,targetAreas)))
        print("X   : " + " | ".join(map(str,targetXs)))
        print("Y   : " + " | ".join(map(str,targetYs)))
        frame_counter = frame_counter+1

        


#cv2.destroyAllWindows() 


