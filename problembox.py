#!/usr/bin/env python3
# By Joseph Lannan for Betabox Labs

import os
from gtts import gTTS #google text to speach for computer voice
import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)

def Say(message):
    print("Saying " + message)
    filename = './audio/' + message.replace(" ", "") + '.mp3'
    exists = os.path.isfile(filename)
    if exists:
        os.system('mpg321 ' + filename + " > /dev/null") 
    else:
        print('had to get ' + filename)
        tts = gTTS(message,'en')
        tts.save(filename)
        os.system("mpg321 " + filename + " > /dev/null")

# output setup
GPIO.setup(21, GPIO.OUT) # Red LED
GPIO.setup(20, GPIO.OUT) # Green LED
#input setup
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP) #O2 UP, OFF
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP) #O2 DOWN, EMERGENCY Mode
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP) #EmergencyLS
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP) #PrimaryLS
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Airlock
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Purge

#LED Funcions
def setLEDRed():
    GPIO.output(21, GPIO.LOW)
    GPIO.output(20, GPIO.HIGH)

def setLEDGreen():
    GPIO.output(21, GPIO.HIGH)
    GPIO.output(20, GPIO.LOW)
# Some Variables for when the problem event occurs
problem = False
emergencyair = False
oxygen = 'normal'
emergencyls = False
primaryls = True
airlock = True
purgedair = False
problemsolved = False
def updatebuttons():
    print("Checking Inputs")
    global primaryls
    primaryls = bool(GPIO.input(13))
    print("primaryls = " + str(primaryls))
    global emergencyls
    emergencyls = bool(GPIO.input(12))
    print("emergencyls = " + str(emergencyls))
    global oxygen
    if (GPIO.input(19)):
        oxygen = "off"
    elif (GPIO.input(26)):
        oxygen = "emergency"
    else:
        oxygen = "normal"
    print("Oxygen = " + oxygen)
    global problemsolved
    problemsolved = emergencyls and not primaryls
    print("problemsolved = " + str(problemsolved))
    global problem
    print("problem = " + str(problem))
# Events for when buttons are pressed
def button19ON(channel):
    sleep(.1)
    if GPIO.input(19) == 0:
        Say("Oxygen turned off. You have 1 minute of oxygen remaining.")
    else:
        Say("Oxygen system set to default")
def button26ON(channel):
    sleep(.1)
    if GPIO.input(26) == 0:
        Say("Backup Oxygen Enabled.")
    else:
        Say("Oxygen system set to default")
def button6(channel):
    sleep(.1)
    if GPIO.input(6) == 1:
        Say("Airlock has been enabled")
    else:
        Say("Airlock has been disabled")
def button13(channel):
    sleep(.1)
    print(GPIO.input(13))
    if GPIO.input(13) == 1:
        Say("Primary Life support has been enabled")
    else:
        Say("Primary Life support has been disabled")
def button12(channel):
    sleep(.1)
    if GPIO.input(12) == 1:
        Say("Emergency Life support has been enabled")
    else:
        Say("Emergency Life support has been disabled")
def button17ON(channel):
    sleep(.1)
    global problem
    global oxygen
    purgedair = True
    Say("Purging Air")
    sleep(2)
    if problem:
        updatebuttons()
        print("Checking Problem Conditions to see if solved")
        print("Problemsolved = " + str(problemsolved))
        if (problemsolved):
            Say('Crisis averted, air is normal')
            problem = False
            setLEDGreen()
        elif (oxygen == 'off'):
            Say('Remaining oxygen has been purged, warning out of oxygen')
        elif (not primaryls and not emergencyls):
            Say('Air Purged, You have 30 seconds of life support remaining')
        else:
            print('problem has not been solved')
    else:
        print("No problem is occuring")
#Event Detection
GPIO.add_event_detect(17, GPIO.BOTH, callback=button17ON, bouncetime=5000)
GPIO.add_event_detect(26, GPIO.FALLING, callback=button26ON, bouncetime=3000)
GPIO.add_event_detect(19, GPIO.FALLING, callback=button19ON, bouncetime=5000)

GPIO.add_event_detect(12, GPIO.BOTH, callback=button12, bouncetime=4000)
GPIO.add_event_detect(13, GPIO.BOTH, callback=button13, bouncetime=4000)
GPIO.add_event_detect(6, GPIO.BOTH, callback=button6, bouncetime=4000)
# main loop
try:
    while True:

        setLEDGreen()
        updatebuttons()
        input('Press enter to trigger an event....')
        problem = True
        setLEDRed()
        os.system('mpg123 ./audio/alert_siren.mp3 > /dev/null')
        Say("Primary Lifesupport failure. Atmosphere leak in from primary life support. You have 5 minute before air depletion")
        os.system('mpg123 ./audio/alert_siren.mp3 > /dev/null')

        input('Press enter to end')
        setLEDGreen()
finally:
    GPIO.cleanup
