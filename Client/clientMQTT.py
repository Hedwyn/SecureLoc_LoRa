from serial import *
import paho.mqtt.client as mqtt
import socket
import time
#HOST = '169.254.1.1'
HOST = '127.1.1.1' #if run locally

PORT = 1883 # default mqtt port
#SERIALPATH = ["/dev/ttyACM0", # for Linux / Rasp
#              "/dev/ttyACM1"]
SERIALPATH = ["COM22"] # for windows

distance = 0
anchor_id = ''
bot_id = ''
NB_DATA = 8 # number of datatypes sent by the node
ROOT = 'SecureLoc/anchors_data/'

# initializing some variables
rssi = 0
exit_flag = 0

# starting mqtt client
mqttc = mqtt.Client()

mqttc.connect(HOST, PORT, 60)

mqttc.loop_start()

# getting
Serialports = []
for path in SERIALPATH:
    try:
        Serialports.append(Serial(path, baudrate=115200, timeout=1, writeTimeout=1) )
    except SerialException:
        print("No serial device on the given path :" + path)

while not(exit_flag):
    for serialport in Serialports:
        try:
            if serialport.isOpen():

                if (serialport.in_waiting > 0 ):

                    line = serialport.readline().decode('utf-8').strip()

                    if line[0] == '*' and line[-1] == '#':
                        x = line.split("|")
                        if len(x) == NB_DATA:
                            anchor_id = x[0][15:17]
                            bot_id = x[1][14:17]
                            print("identifiant ancre" + str(anchor_id))
                            print("identifiant robot" + str(anchor_id))

                            distance = float(x[2][:])
                            [ts1,ts2,ts3,ts4] = [float(x[3]), float(x[4]), float(x[5]), float(x[6]) ]
                            rssi = x[7][:-1]



                        else:
                            print('wrong formatted frame received: {}'.format(line))
                    print(line)


                    mqttc.publish(ROOT + str(anchor_id) + "/" + str(bot_id) + "/distance", str(distance) )
                    mqttc.publish(ROOT + str(anchor_id) + "/" + str(bot_id) + "/rssi", str(rssi) )
                    ts_list = [ts1,ts2,ts3,ts4]
                    mqttc.publish(ROOT + str(anchor_id) + "/" + str(bot_id) + "/ts", str(ts_list) )


            else:
                print("device on " + str(serialport) + " has been disconnected \n")
                Serialports.remove(serialport)
        except KeyboardInterrupt:
            print("Ctrl + C received, quitting")
            exit_flag = True
        except:
            print('An error occured, did you unplug the device ?')
            break;
