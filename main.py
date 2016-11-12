import cv2
import urllib 
import numpy as np
import os, sys
from datetime import datetime
from datetime import timedelta

################################################################################
#Config Data
################################################################################

#Fixed IP address of IP Camera
camera_IP = '10.111.76.25'

#Set to true to attempt to display debug images. Should be false when running headless
displayDebugImg = False

################################################################################
# Global Data
################################################################################
targetAreas = []
targetXs = []
targetYs = []
targetHeights = []
targetWidths = []

execution_start_time_ms = datetime.now()      #Marker for start of program execution
frame_capture_time_ms = 0      #Marker for time of most recent full image frame capture
prev_frame_capture_time_ms = 0 #Marker for previous full image frame capture
ip_capture_time = 0            #Marker for time of most recent IP data RX
proc_time_ms = 0               #Total time to process a frame in ms




################################################################################
# Utility Functions
################################################################################

# returns the elapsed milliseconds since the start of the program
def millis():
   dt = datetime.now() - execution_start_time_ms
   ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
   return ms
   
   
   
################################################################################
# Main Processing algorithm
################################################################################
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


################################################################################
################################################################################
### Main Method
################################################################################
################################################################################


#Open data stream from IP camera
stream = urllib.urlopen('http://'+camera_IP+'/mjpg/video.mjpg')
bytes = ''
frame_counter = 0


#Attempt to initalize graphics for displaying video feeds, if requested.
if(displayDebugImg):
    try:
        result = cv2.startWindowThread()
    except Exception as e:
        result = -1
        print("Exception while attempting to start display")
        
    if(result != 1):
        #If we couldnt' open the feeds, force debugging images off but continue
        # normally otherwise. This usually happens when this is run without a desktop
        # environment available (headless run).
        print("Warning, could not start graphics. Will not produce debugging images")
        displayDebugImg = False
    
    
if(displayDebugImg):
    cv2.namedWindow('Video', cv2.WINDOW_NORMAL)


# Main execution loop
while frame_counter < 300:

    # Read data from the network in 1kb chunks
    #  Mark the time each chunk is fully read in.
    bytes += stream.read(1024)
    ip_capture_time = millis()
    
    # Search for special byte sequences which indicate the start and end of
    #  single-video-frame image data
    b = bytes.rfind('\xff\xd9')
    a = bytes.rfind('\xff\xd8', 0, b-1)
    
    #Check if the presence of both markers indicate a full image is in the input buffer
    if a != -1 and b != -1:
        # Image frame has been found, Conver the data to an image in prep for processing
        
        # Extract the raw image data 
        jpg = bytes[a:b+2]
        # Clear processed bytes from the input data buffer
        bytes = bytes[b+2:]
        # Convert the raw image bytes into an image structure openCV can use
        img = cv2.imdecode(np.fromstring(jpg, dtype = np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
        # Mark the time we found this image
        prev_frame_capture_time_ms = frame_capture_time_ms
        frame_capture_time_ms = ip_capture_time
        # Update the image counter
        frame_counter = frame_counter+1
        
        
        #Clear out the arrays which will hold the processed data
        targetAreas = []
        targetXs = []
        targetYs = []
        targetHeights = []
        targetWidths = []

        #Process the image
        img_process(img)
        
        # Calculate processing time
        proc_time_ms = millis() - ip_capture_time
        #Calculate present FPS (capture and processing)
        fps = 1000/(frame_capture_time_ms - prev_frame_capture_time_ms)
        
        # Output the actual processed data
        # Just printing for now, eventually this will be network tables
        print(("Proc Time: %.2f ms" % proc_time_ms) + (" | FPS: %.2f" % fps))
        print("Area: " + " | ".join(map(str,targetAreas)))
        print("X   : " + " | ".join(map(str,targetXs)))
        print("Y   : " + " | ".join(map(str,targetYs)))
        
        # Show debugging image
        if(displayDebugImg):
            cv2.imshow('Video', img) 
            
        

        
# Close out any debugging windows
if(displayDebugImg):
    cv2.destroyAllWindows() 


