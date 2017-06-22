#!/usr/bin/python
import subprocess as sp
import time
import sys
import os
from math import floor
import RPi.GPIO as GPIO

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# ------------------- VARIABLES DEFINITIONS ------------------- #
state = 0 # 0 = idle, 1 = long range motion detected (PIR), 2 = short range motion detected (UD), 3 = kiosk mode
PIR_IN = 4

UD_TRIG = 23
UD_ECHO = 24
LEVEL = 50 # detection level, only act when value below level (cm)

IDLE_TIME = 20

# ------------------- STATES DEFINITIONS ------------------- #
# state 0 - idle state
action0 = ["eog", "-f", "/home/pi/Documents/Code/background.jpg"]

# state 1 - long range motion detected
action1 = ["omxplayer", "filename", "-o", "hdmi"]
action1[1] = "/home/pi/Documents/Code/state1video.mp4" # video file to be played

# state 2 - short range motion detected
action2 = ["omxplayer", "filename", "-o", "hdmi"]
action2[1] = "/home/pi/Documents/Code/state2video.mp4" # video file to be played

# state 3 - kiosk mode
action3 = ["chromium-browser","--noerrdialogs","--kiosk","http://www.davinci.nl","--incognito"]



# ------------------- FUNCTION DEFINITIONS ------------------- #
def setup_PIR(PIR_IN):
        GPIO.setup(PIR_IN, GPIO.IN)         #Read output from PIR motion sensor
        return;

def setup_UD (UD_TRIG, UD_ECHO):
        GPIO.setup(UD_TRIG,GPIO.OUT)
        GPIO.setup(UD_ECHO,GPIO.IN)
        return;

def measure_PIR(PIR_IN):
        motion = GPIO.input(PIR_IN)
        print(["Motion: ", motion])
        time.sleep(0.5)
        
        if (motion == 1):
                state_PIR = True
                print(["Motion Detected!"])
        else:
                state_PIR = False
        return state_PIR;

def measure_UD (UD_TRIG, UD_ECHO, LEVEL):
        GPIO.output(UD_TRIG, False)
        # print "Waiting For Sensor To Settle"
        time.sleep(0.1)

        GPIO.output(UD_TRIG, True)
        time.sleep(0.00001)
        GPIO.output(UD_TRIG, False)

        while GPIO.input(UD_ECHO)==0:
          pulse_start = time.time()

        while GPIO.input(UD_ECHO)==1:
          pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        
        print(["Distance:",distance,"cm"])

        if (distance < LEVEL):
                state_UD = True
        else:
                state_UD = False
        return state_UD;

def detect_unlock():
        state_UL = False
        return state_UL;

def detect_touch():

        state_TH = True
        
        return state_TH;

# ------------------- MAIN PROGRAM ------------------- #
# Setup actions
setup_PIR(PIR_IN)
setup_UD(UD_TRIG, UD_ECHO)

# start in state 0
# sp.Popen(action0)

# Main loop
while (True):
        # Measure
        state_pir = measure_PIR(PIR_IN)
        state_ud = measure_UD(UD_TRIG, UD_ECHO, LEVEL)
        state_unlock = detect_unlock()
        state_touch = detect_touch()

        # Switch states
        if (True):
                if (state == 0): # idle state
                        if (state_unlock):
                                process = sp.Popen(action3, stdout=sp.PIPE, shell=False)
                                state = 3
                        elif (state_ud):
                                process = sp.Popen(action2, stdout=sp.PIPE, shell=False)
                                state = 2
                        elif (state_pir):
                                process = sp.Popen(action1, stdout=sp.PIPE, shell=False)
                                state = 1

                if (state == 1): # long range motion detected (PIR)
                        if (state_unlock):
                                process.kill()
                                process = sp.Popen(action3, stdout=sp.PIPE, shell=False)
                                state = 3
                        elif (state_ud):
                                process.kill()
                                process = sp.Popen(action2, stdout=sp.PIPE, shell=False)
                                state = 2
                        elif (process.poll() != None):
                                state = 0
                                
                        print(process.poll())

                if (state == 2): # short range motion detected (UD)
                        if (state_unlock):
                                process.kill()
                                process = sp.Popen(action3, stdout=sp.PIPE, shell=False)
                                state = 3
                        elif (process.poll() != None):
                                state = 0

                        print(process.poll())
                         
                if (state == 3): # interactive kiosk mode
                        if (not(state_touch())):
                                process.kill()
                                state = 0
                        

                print("State:", state)
