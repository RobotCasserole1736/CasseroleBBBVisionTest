import cv2
import urllib2 as u
import numpy as np
import os, sys
from datetime import datetime
from datetime import timedelta
import time
import psutil
import pythonled
import Pipeline
import TargetObservation
import UDPServer

################################################################################
#Config Data
################################################################################

#Fixed IP address of IP Camera
camera_IP = '10.17.36.11'

#Fixed IP address of this BBB
bbb_IP = '10.17.36.20'

################################################################################
# Global Data
################################################################################

#data structure object to hold info about the present data processed from the image fram
curObservation = TargetObservation.TargetObservation()

#global flag to turn debug display on and off
# Presently attempts to display images, so shouldn't
# ever get turned on if running without a display
# hooked up (or VNC or something like that...)
displayDebugImg = False

#Timestamp tracking info. Needed for performance metrics and for reporting
# image processing delay
execution_start_time_ms = datetime.now()      #Marker for start of program execution
frame_capture_time_ms = 0      #Marker for time of most recent full image frame capture
prev_frame_capture_time_ms = 0 #Marker for previous full image frame capture
ip_capture_time = 0            #Marker for time of most recent IP data RX
proc_time_ms = 0               #Total time to process a frame in ms

#Performance metric tracking
fps_current = 0
cpu_load_pct = 0
mem_load_pct = 0


#Status LED
statusLED0 = pythonled.pythonled(0)
statusLED1 = pythonled.pythonled(1)
statusLED2 = pythonled.pythonled(2)
statusLED3 = pythonled.pythonled(3)
ledStatus = False

# image processing pipeline (codegenerated from GRIP)
procPipeline = Pipeline.Pipeline()

# Server to transmit processed data over UDP to the roboRIO
outputDataServer = UDPServer.UDPServer(send_to_address = "roborio-1736-frc.local", send_to_port = 5800)


################################################################################
# Utility Functions
################################################################################

def indicateLEDsNotRunning():
    statusLED1.off()
    ledStatus = False

    
def indicateLEDsProcessingActive():
    global ledStatus
    
    if(ledStatus == False):
        statusLED1.on()
        ledStatus = True


# returns the elapsed milliseconds since the start of the program
def millis():
   dt = datetime.now() - execution_start_time_ms
   ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
   return ms

# Performs a robust connection to a given URL, and returns a stream once created
#  In this context, robust means this function will continue to attempt the connection
#  until successful, retrying at reasonable intervals. THe returned stream will have
#  a pretty snappy timeout, so expect the connection to actually be robust!
#  On all stream reads, be sure to catch issues reading (usually timeouts) and perhaps
#  attempt to reconnect if needed.
def robust_url_connect(url):
    local_stream = None
    print("Attempting to connect to \"" + url + "\"")
    while local_stream  is None:
        try:
            local_stream  = u.urlopen(url, timeout=2.0)
        except Exception as e:
            indicateLEDsNotRunning()
            print("Could not connect to \"" + url + "\".")
            print("Reason: " + str(e))
            time.sleep(1)
            print("Retrying...")
            local_stream  = None
            continue
    print("Successfully connected to camera image stream at \"" + url + "\"")
    return local_stream


################################################################################
# Main Processing algorithm... or a thin wrapper around it?
################################################################################
def img_process(img):
    """
    #Run the generated GRIP image processing pipeline
    procPipeline.set_source0(img)
    procPipeline.process()


    #Extract relevant outputs into the current observation
    for c in procPipeline.filter_contours_output:
        x, y, w, h = cv2.boundingRect(c)
        curObservation.addTarget(x, y, 0, w, h) #area unused for now.
    """
        
    hsv_thres_lower = np.array([39,156,9])
    hsv_thres_upper = np.array([92,255,255])
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv_mask = cv2.inRange(hsv, hsv_thres_lower, hsv_thres_upper)
    

    contours, hierarchy = cv2.findContours(hsv_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_KCOS)
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        #minimal amount of qualification on targets
        if(w > 10 and h > 10): 
            curObservation.addTarget(x, y, 0, w, h) #area unused for now.



################################################################################
################################################################################
### Main Method
################################################################################
################################################################################
ledStatus = False
indicateLEDsNotRunning()

#Open data stream from IP camera
# Robust connect should hopefullyprevent race conditions between the camera
# booting and this software attemptting to connect to it.
camera_url = 'http://'+camera_IP+'/mjpg/video.mjpg'
camera_data_stream = robust_url_connect(camera_url)

#Reset byte stream and frame counter
bytes = ''
frame_counter = 0

# Process command line arguments.
# Only one is possible: "--debug" will turn on image display for visual algorithm
#  debugging
if(len(sys.argv) == 2 and sys.argv[1] is "--debug"):
    print("INFO: Debug images will be displayed.")
    displayDebugImg = True

# Start json server which will spew info to the roboRIO

#Attempt to initalize graphics for displaying video feeds, if requested.
if(displayDebugImg):
    try:
        result = cv2.startWindowThread()
    except Exception as e:
        result = -1
        print("WARNING: Exception while attempting to start display")

    if(result != 1):
        #If we couldnt' open the feeds, force debugging images off but continue
        # normally otherwise.
        print("WARNING: could not start graphics. Will not produce debugging images")
        displayDebugImg = False


if(displayDebugImg):
    cv2.namedWindow('Video', cv2.WINDOW_NORMAL)


# Main execution loop
while True:

    # Read data from the network in 1kb chunks
    #  Catch any issues reading. if we have issues, try to reset the connection.
    try:
        bytes += camera_data_stream.read(4096)
    except Exception as e:
        print("WARNING: problems reading camera data from stream.")
        print("Reason: " + str(e))
        print("Attempting to restart connection...")
        camera_data_stream = robust_url_connect(camera_url)
        continue


    #  Mark the time each chunk is fully read in.
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


        # Clear out the arrays which will hold the processed data
        curObservation.clear()

        # Process the image
        img_process(img)

        # Capture CPU metrics at a slower interval, we don't need to update these
        #  super often.
        if(frame_counter % 15 == 0):
            cpu_load_pct = psutil.cpu_percent()
            mem_load_pct = psutil.virtual_memory().percent

        # Calculate processing time
        proc_time_ms = millis() - ip_capture_time
        # Calculate present FPS (capture and processing)
        fps_current = 1000/(frame_capture_time_ms - prev_frame_capture_time_ms)

        # Add the metadata to the present target observation data
        curObservation.setMetadata(frame_counter,proc_time_ms,cpu_load_pct,mem_load_pct,fps_current)

        # Transmit the vision processing results to the roboRIO
        outputDataServer.sendString(curObservation.toJsonString())
        indicateLEDsProcessingActive()


        # Debug printing
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        # print("Frame # "+ str(frame_counter))
        # print(("Proc Time: %.2f ms" % proc_time_ms) +
        #       (" | FPS: %.2f" % fps_current) +
        #       (" | CPU: %.1fpct" % cpu_load_pct)+
        #       (" | MEM: %.1fpct" % mem_load_pct))
        # print("Area: " + " | ".join(map(str,targetAreas)))
        # print("X   : " + " | ".join(map(str,targetXs)))
        # print("Y   : " + " | ".join(map(str,targetYs)))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")

        # Show debugging image
        if(displayDebugImg):
            cv2.imshow('Video', img)

        # I'm presuming this is needed to allow background things to hapapen
        time.sleep(.01)



#Turn off status LED
indicateLEDsNotRunning()
# Close out any debugging windows
if(displayDebugImg):
    cv2.destroyAllWindows()
