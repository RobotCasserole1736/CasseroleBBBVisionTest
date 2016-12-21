# Class to hold a single set of observations from the image coprocessor
# One set of observations is derived from processing a single frame in the
# image stream into one or more targets, along with metadata about the
# processing time.

import json

class TargetObservation(object):
    def __init__(self):
        self.clear()

    def clear(self):
        self.frameCounter = 0 # Indicates which frame this was - incriments for each new processed frame
        # Target data. All arrays will be the same length. Each index in the arrays
        # represents a unique qualified target identified in the frame.
        self.Xs = [] # X coordinates of the centriods
        self.Ys = [] # Y coordinates of the centriods
        self.boundedAreas = [] # 2D areas enclosed by the found contours
        self.widths = [] # Total widths of the observed targets
        self.heights = [] # Total heights of the observed targets
        # Metadat used to track performance, or reduce phase delay effects in control loops
        self.procTime = 0 # Time from frame reception over IP to transmit, in milliseconds.
        self.cpuLoad = 0 # Percentage of cpu time spent doing things other than nothing
        self.memLoad = 0 # Percent of the available RAM bytes which are in use by some process
        self.fps = 0 # Number of frames per second that are recieved, processed, and transmitted.

    def addTarget(self, X_in, Y_in, area_in, width_in, height_in):
        self.Xs.append(X_in)
        self.Ys.append(Y_in)
        self.boundedAreas.append(area_in)
        self.widths.append(width_in)
        self.heights.append(height_in)


    def setMetadata(self, frameCounter_in, procTime_ms_in, cpuLoad_pct_in, memLoad_pct_in, fps_in):
        self.frameCounter = frameCounter_in
        self.procTime = procTime_ms_in
        self.cpuLoad = cpuLoad_pct_in
        self.memLoad = memLoad_pct_in
        self.fps = fps_in

    def toJsonString(self):
        # HEY YOU DEVELOPER LOOK HERE!!!!
        # The format used to create this json string must align with the
        # format expected by the roboRIO in the java code. If you alter this
        # code, you _must_ go look at the java code to ensure they remain aligned.
        infoDict = {"frameCounter":self.frameCounter,
                    "Xs":self.Xs,
                    "Ys":self.Ys,
                    "boundedAreas":self.boundedAreas,
                    "widths":self.widths,
                    "heights":self.heights,
                    "procTime":self.procTime,
                    "cpuLoad":self.cpuLoad,
                    "memLoad":self.memLoad,
                    "fps":self.fps}

        return json.dumps(infoDict)






# No main code to be had....
