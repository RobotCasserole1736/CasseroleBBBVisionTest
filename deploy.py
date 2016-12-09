import os, sys
from subprocess import call, checkoutput

#Possible paths for SSH and SCP - assume we're using the ones from the GIT install,
# but don't assume people put them on their paths. Chris Gerth forces the C/B/D drive
# checking because he builds giant computers and installs things wherever he likes.
SSH_PATH_LIST = ["C:\\Program Files\\Git\\mingw32\\bin\\ssh.exe",
                 "B:\\Program Files\\Git\\mingw32\\bin\\ssh.exe",
                 "D:\\Program Files\\Git\\mingw32\\bin\\ssh.exe",
                 "C:\\Program Files\\Git\\usr\\bin\\ssh.exe",
                 "B:\\Program Files\\Git\\usr\\bin\\ssh.exe",
                 "D:\\Program Files\\Git\\usr\\bin\\ssh.exe",
                 "ssh"]
                 
SCP_PATH_LIST = ["C:\\Program Files\\Git\\mingw32\\bin\\scp.exe",
                 "B:\\Program Files\\Git\\mingw32\\bin\\scp.exe",
                 "D:\\Program Files\\Git\\mingw32\\bin\\scp.exe",
                 "C:\\Program Files\\Git\\usr\\bin\\scp.exe",
                 "B:\\Program Files\\Git\\usr\\bin\\scp.exe",
                 "D:\\Program Files\\Git\\usr\\bin\\scp.exe",
                 "scp"]
                 
#Beaglebone Black should be at a fixed IP address
TARGET_IP_ADDRESS = "10.11.76.20"
       

#Utility to determine if path is an executable   
def isExecutable(path):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    
    
##################################################################
### Main code begins here
##################################################################

#Find where SSH and SCP are at on the user's PC
ssh_exe = None
scp_exe = None
for path in SSH_PATH_LIST:
    if(isExecutable(path)):
        ssh_exe = path
        break
       
if(ssh_exe == None):
    print("ERROR: cannot find SSH utility on this PC.... is Git installed?")
    sys.exit(-1)
    
    
for path in SCP_PATH_LIST
    if(isExecutable(path)):
        scp_exe = path
        break
       
if(scp_exe == None):
    print("ERROR: cannot find SSH utility on this PC.... is Git installed?")
    sys.exit(-1)
    

# See if we can ping the BBB
retstr = subprocess.check_output(["ping -n 1 ", TARGET_IP_ADDRESS], stderr=subprocess.STDOUT,shell=True)
if("Destination host unreachable" in retstr):
    print("ERROR: Cannot ping target at " + TARGET_IP_ADDRESS)
    sys.exit(-1)
    


    
    

    
                 
