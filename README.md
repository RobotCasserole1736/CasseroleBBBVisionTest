# CasseroleBBBVisionTest
Quick work for testing vision processing on Beaglebone Black

Many many many thanks to FRC2481 for their simple instructions on getting this started.

Their awesome work can be found [here](https://github.com/Frc2481/paul-bunyan).

##Basic Setup

### Internet - dependent Prerequisites

We will use the default angstrom linux distro.

For first setup, the BBB must be connected to a network with internet access.

On a brand new BBB, ssh into it using your favorite ssh utility. You will likely have to look up the IP address by looking at the router setup page, and determining what DHCP address was assigned to the BBB.

When prompted, login with:

    user: root
    password: <leave blank>
    
Yes it's bad to do stuff as root. But also easier. Just don't do silly things.

Update the time so SSL certificate validation occurs ok:

    ntpdate -b -s -u pool.ntp.org

Now install the python utilities needed:

    opkg update
    opkg install python-pip
    opkg install python-setuptools
    opkg install python-opencv
    opkg install python-misc
    opkg install python-modules
    pip install http://pypi.python.org/packages/source/p/pynetworktables/pynetworktables-2015.3.1.tar.gz
    pip install psutil
   

Get this repo onto the BBB:

    cd ~
    git clone https://github.com/RobotCasserole1736/CasseroleBBBVisionTest
    
Checkout your favorite release. Probably latest on master should be correct.

### Robot network - dependent Prerequisites

Now that all the dependencies are installed, the unit should be moved and placed on the robot network (probably no internet access).
Once this is done, log back in.

Set a static IP address of 10.17.36.20, with the default gateway pointing to the router (usually 10.17.36.1)

    ls -la /var/lib/connman/
    cd /var/lib/connman/ethernet_[xx]
    more settings
    cd /usr/lib/connman/test
    ./set-ipv4-method ethernet_[xx]_cable manual 10.17.36.20 255.255.255.0 10.17.36.1
    reboot
    
Once the BBB boots again, you should be able to connect via the set up static IP address.

To start the vision processing manually, run the "runVision.sh" script in the root of the repo.
More instructions to come on how to set this up to go automatically at boot.

# Script Design

## Overall
As is, the script is set up to maintain a robust connection with the IP camera,
process frames as they come in, and post the processing results to NetworkTables
(or just print them out, as it does now)

The psutil library is used to monitor CPU and memory loading. 

The exact data processed out of the image will change year to year. Some
possibiilities include:

* Total time from reciving the image to posting the processing results
* For each target:
  * X/Y position within the image
  * Information for acessing the validity of the target
    * Bounding Box Size/Area
    * Infill percentage
    * Skew


## Network Connectivity
The read and connect routines have fairly short timeouts, but will attempt to 
reconnect indefinitely if the connection is ever lost. There's been some basic
desktop testing to prove out that there are no race conditions between starting
the camera and starting the BBB. 

## Status LED
To indicate status, the usual status LED is overwritten. During BBB boot sequence,
the status LED will follow the default on-for-boot, then heartbeat until the
vision processing script starts.

Once the vision processing script has started, the LED will turn off fully. 
As long as the script is waiting for a connection, the LED will remain dark. Once
valid image frames are getting processed, the LED will turn back on to be mostly
solid (occasional pulse off). If the LED ever goes off, it means the script is
not actively processing frames. Usually this is due to lack of a network connetion
to the IP camera



#Notes on Cameras & Settings

To get good images for processing, it's usually best to try to get a dark image. 
The only lit-up pixels should be the target in question.

This usually means

* Fixed (non-automatic) white balance
* Exposure turned down to minimum
* Brightness turned down to minimum
* All auto-adjustement disabled
    
Note that I've been testing with an axis M1013, which is a horrible camera choice
since it is impossible to disable all brightness compensation. M1011 is better 
for vision processing, I think... But, basicallly, we wouldn't ever want to use the M1013.

[This](http://wpilib.screenstepslive.com/s/4485/m/24194/l/288984-camera-settings) is a good resource on this sort of thing.



#Remote Desktop Connections

x11vnc is installed and runable on the BBB. It's not recommended to have it always on since it can soak up processor cycles, which are very valuable. However, for some vision debugging, it's nice to have.

To remote desktop, first ssh into the BBB as described above. Then run the following magic incantation:

    x11vnc -bg -o %HOME/.x11vnc.log.%VNCDISPLAY -auth /var/run/gdm/auth-for-gdm*/database -display :0  -forever
    
Then connect to it using any VNC utility. For windows, I like [this one](https://www.realvnc.com/download/viewer/).

To adjust the screen resolution, sadly this all has to be done on the server (BBB) side, and only after the 
connection has been started. To do this, open the Terminal application under Applications->System, and run the following command:

    xrandr --fb 1600x900
    
Of course, resolution may be adjusted to suit.

All these things can be put into .sh scripts if desired to speed setup

