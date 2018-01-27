# NSA-Drone : HAVE FUN
Ar Drone 2.0 various tools.
 
# WHAT CAN I DO WITH THIS CODE?
A couple of things:

 (1) A very basic AR Drone controller : just connect your pc to an AR Drone 2.0 and launch pc-command.py, you will be able to control it with your keyboard.
 
 (2) An AR Drone 2.0 hacker : if you see an evil ar drone 2.0, launch hack.sh : it will automatically cut the connection with its owner, and you will gain control of it. Then, just use the previous functionnality to make whatever you want with it. COOL OPTION : if your goal is just to make the drone land, launch emer.py script, it will be much faster.
 
 (3) An automatic drone that follows a target : use it with previous options to make it even more wonderful.
 
# WOW! BUT HOW DO I USE IT?
For each option, you will need python (tested with version 2.7) and a PC with linux.

Moreover, you will need :
 * For option (1) : pygame (tested with version 1.9.3).
 * For option (2) : the aircrack-ng suite (tested with version 1.2 beta3)
 * For option (3) : openCV for python (tested with version 3.3.0 with patched ROI selector bugs)
 
# AN EXAMPLE : "NSA-Drone"
An application example : in a team, we are building a drone that carries a rPi that will allow us to use options (1), (2), (3).
Options (1) and (3) will be updated to : "Give control to another node connected to the drone" and "AR Drone 2.0 that follows your drone".

# BEFORE YOU START
This project is not finished yet. There are unfilled pieces of code, but I'm doing my best !

# DISCLAIMER
I'm not responsible for any case of stolen or broken drones. And don't use it for bad purposes :/.

Author : DonKey
