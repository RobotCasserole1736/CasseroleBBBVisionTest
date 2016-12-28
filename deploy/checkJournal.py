import os, sys
import subprocess 
import time

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
TARGET_IP_ADDRESS = "10.17.36.20"
       


#Utility to determine if path is an executable   
def isExecutable(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    
#Runs command with error checking and prints info
def runCmd(cmd, ignore_error=False, cmd_stdin = None):
    errors_present = False
    retstr = ""
    print("\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print("Running command:\n" + cmd)

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,stdin=subprocess.PIPE)
    if(cmd_stdin != None):
        proc.stdin.write(cmd_stdin.encode())
    retstr = proc.communicate()[0]
    retstr = retstr.decode('utf-8')

    if((errors_present or proc.returncode != 0) and ignore_error == False):
        print("Error while running command:\n" + retstr)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")
        sys.exit(-1)
        
    print("Command returned:\n" + retstr)
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")
    return retstr
    
    
##################################################################
### Main code begins here
##################################################################

#Find where SSH and SCP are at on the user's PC
ssh_exe = None
scp_exe = None
for path in SSH_PATH_LIST:
    if(isExecutable(path)):
        ssh_exe = "\"" + path + "\"" 
        break
       
if(ssh_exe == None):
    print("ERROR: cannot find SSH utility on this PC.... is Git installed?")
    sys.exit(-1)
    
    
for path in SCP_PATH_LIST:
    if(isExecutable(path)):
        scp_exe = "\"" + path + "\"" 
        break
       
if(scp_exe == None):
    print("ERROR: cannot find SSH utility on this PC.... is Git installed?")
    sys.exit(-1)
    

# See if we can ping the BBB
cmd = "ping -n 1 " + TARGET_IP_ADDRESS
retstr = runCmd(cmd)

if("unreachable" in retstr):
    print("ERROR: Attempted ping, but cannot contact target at " + TARGET_IP_ADDRESS)
    sys.exit(-1)
    

#Pre-steps: Make directory on target if not already existing
cmd = ssh_exe + " root@" + TARGET_IP_ADDRESS + " journalctl -b | grep python "
print("Querying for info about python scripts...")
runCmd(cmd, True, "\n")



sys.exit(0)

                 
