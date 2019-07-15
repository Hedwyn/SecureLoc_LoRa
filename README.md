# SecureLoc
Secure Indoor localization system based on DWM1000, DecaDuino library and PAnda 3D engine.

##Brief
Should be run with Panda3D 1.10, embedding Python 3.6.

Make sure the python directory of Panda 3D is in your Path.

Simply run with: python main.py.



Useful parameters :

In application.py :

set ENABLE_LOGS to 1 to keep track of the ranging, position and speed measurements in text file. 
set PLAYBACK to True to replay existing logs.
set DEBUG to 1 to get more debug informations.
Modify the server IP address to match yours if not using the playback mode.

In world.py :

set DEBUG to 1 to get more debug informations.*

anchors.tab :
contains the anchors position. Should be the closest possible to the reality

Detailed documentation is provided in Documentation.pdf

###Contact: baptiste.pestourie@lcis.grenoble-inp.fr
