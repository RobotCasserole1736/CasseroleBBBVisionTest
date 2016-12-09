import os, sys
import subprocess 

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
       
#Path to root directory where we put the files on the remote
TARGET_SCRIPT_DIR = "~/CasseroleVision/"
TARGET_SERVICE_DIR = "/lib/systemd/system/"

#Utility to determine if path is an executable   
def isExecutable(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    
#Runs command with error checking and prints info
def runCmd(cmd):
    try:
        retstr = subprocess.check_output(cmd, stderr=subprocess.STDOUT,shell=True)
    except Exception as E:
        print("ERROR: issues while running command " + cmd)
        print(E)
        sys.exit(-1)
    return retstr
    
    
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
    
    
for path in SCP_PATH_LIST:
    if(isExecutable(path)):
        scp_exe = path
        break
       
if(scp_exe == None):
    print("ERROR: cannot find SSH utility on this PC.... is Git installed?")
    sys.exit(-1)
    

# See if we can ping the BBB
cmd = "ping -n 1 " + TARGET_IP_ADDRESS
retstr = runCmd(cmd)

if("unreachable" in retstr.decode('utf-8')):
    print("ERROR: Attempted ping, but cannot contact target at " + TARGET_IP_ADDRESS)
    sys.exit(-1)
    

#Pre-steps: stop service on roboRIO
cmd = ssh_exe + "root@" + TARGET_IP_ADDRESS + " systemctl stop CasseroleVisionCoprocessor"
print("Stopping vision coprocessor service")
runCmd(cmd)

#Copy python scripts
cmd = scp_exe + "root@" + TARGET_IP_ADDRESS + TARGET_SCRIPT_DIR + " ./*.py"
print("Copying python scripts")
runCmd(cmd)

#Copy service
cmd = scp_exe + "root@" + TARGET_IP_ADDRESS + TARGET_SERVICE_DIR + " ./CasseroleVisionCoprocessor.service"
print("Copying service definition")
runCmd(cmd)

#Post-steps: start and enalble service
print("Restarting services")
cmd = ssh_exe + "root@" + TARGET_IP_ADDRESS + " systemctl enable CasseroleVisionCoprocessor"
runCmd(cmd)
cmd = ssh_exe + "root@" + TARGET_IP_ADDRESS + " systemctl start CasseroleVisionCoprocessor"
runCmd(cmd)
    
print("Vision service deployed!")
                 
