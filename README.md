# CasseroleBBBVisionTest
Quick work for testing vision processing on Beaglebone Black

Many many many thanks to FRC2481 for their simple instructions on getting this started.

Their awesome work can be found [here](https://github.com/Frc2481/paul-bunyan).

##Basic Setup

We will use the default angstrom linux distro.

For first setup, the BBB must be connected to a network with internet access.

On a brand new BBB, ssh into it using your favorite ssh utility.

Login with:

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
    pip install http://pypi.python.org/packages/source/p/pynetworktables/pynetworktables-2015.3.1.tar.gz
   

Get this repo onto the BBB:

    cd ~
    git clone https://github.com/RobotCasserole1736/CasseroleBBBVisionTest
    
Checkout your favorite release. Probably latest on master should be correct.

To start the vision processing manually, run the "runVision.sh" script in the root of the repo.
More instructions to come on how to set this up to go automatically at boot.

#Notes on Cameras & Settings

To get good images for processing, it's usually best to try to get a dark image. The only lit-up
pixels should be the target in question.

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

