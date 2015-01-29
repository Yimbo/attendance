#!/usr/bin/python

#-------------------------------------------------------------------------------
# Name:        Attendance
# Purpose:     Read user input and read NFC tag, then insert both into database
#
# Author:      Jakub 'Yim' Dvorak
#
# Created:     26.10.2013
# Copyright:   (c) Jakub Dvorak 2013
# Licence:
#   ----------------------------------------------------------------------------
#   "THE BEER-WARE LICENSE" (Revision 42):
#   Jakub Dvorak wrote this file. As long as you retain this notice you
#   can do whatever you want with this stuff. If we meet some day, and you think
#   this stuff is worth it, you can buy me a beer in return.
#   ----------------------------------------------------------------------------
#-------------------------------------------------------------------------------

import display
import nfc
import mysql
import beeper

import sys
import tty
import termios
import logging

import thread
import time

import RPi.GPIO as GPIO

#Enable debug logging into log
DEBUG=True
#Enable printing informations to std. output
VERBOSE=True

class Actions:
    incomming=1
    outcomming=2
    breakstart=3
    breakend=4

if(DEBUG):
    logging.basicConfig(format='%(asctime)s %(message)s',filename='attendance.log', level=logging.DEBUG)

def debug(message):
    logging.debug(message)

def onScreen(message):
    if(VERBOSE):
        print(message)

def read():
    ledRedOn()
    cardId=nfc.readNfc()
    beep()
    ledRedOff()
    return cardId

def readNfc(action):
    if(action==55):#7 - Incomming
        onScreen("Logging In...")
        display.lcdWriteFirstLine("Prichod...")
        display.lcdWriteSecondLine("Swipe your Card")
        cardId=read()
        logging.info("Incomming - %s",cardId)
        name = mysql.insertReading(cardId,Actions.incomming)
        display.lcdWriteSecondLine(name)
    if(action==57):#9 - outcomming
        onScreen("...")
        display.lcdWriteFirstLine("Logging out...")
        display.lcdWriteSecondLine("Swipe your Card")
        cardId=read()
        logging.info("Outcomming - %s",cardId)
        name = mysql.insertReading(cardId,Actions.outcomming)
        display.lcdWriteSecondLine(name)
    if(action==49):#1 - break start
        onScreen("Zacatek pauzy...")
        display.lcdWriteFirstLine("Pauza zacatek...")
        display.lcdWriteSecondLine("Swipe your Card")
        cardId=read()
        logging.info("Break start - %s",cardId)
        name = mysql.insertReading(cardId,Actions.breakstart)
        display.lcdWriteSecondLine(name)
    if(action==51):#3 - break end
        onScreen("Konec pauzy...")
        display.lcdWriteFirstLine("Pauza konec...")
        display.lcdWriteSecondLine("Swipe your Card")
        cardId=read()
        logging.info("Break end - %s",cardId)
        name = mysql.insertReading(cardId,Actions.breakend)
        display.lcdWriteSecondLine(name)
    if(action==53):#5 - Deletion of last inserted action
        onScreen("Delete the last entry...")
        display.lcdWriteFirstLine("Deleting...")
        display.lcdWriteSecondLine("")
        cardId=read()
        logging.info("Deleting last action - %s",cardId)
        (lastTime,lastAction)=mysql.getLastReading(cardId) or (None, None)

        if(lastTime == None or lastAction == None):
            display.lcdWriteSecondLine("Unknown Event")
            logging.info("Action not found")
            time.sleep(1)

        else:
            display.lcdWriteFirstLine("Delete Event?")
            if(lastAction==Actions.incomming):
                display.lcdWriteSecondLine("Check In")
            elif(lastAction==Actions.outcomming):
                display.lcdWriteSecondLine("Check Out")
            elif(lastAction==Actions.breakstart):
                display.lcdWriteSecondLine("Pauza zacatek")
            elif(lastAction==Actions.breakend):
                display.lcdWriteSecondLine("End of Pause?")
            a=getOneKey()
            if(a==49):#1
                onScreen("Mazu")
                logging.info(" - Deleting action %s (cas: %s)",lastAction, lastTime)
                mysql.deleteLastReading(cardId)
                display.lcdWriteSecondLine("Deleted!")
            else:
                onScreen("Not Deleted")
                logging.info(" - Deleting canceled")
                display.lcdWriteSecondLine("Not deleted!")

    #Sleep a little, so the information about last action on display is readable by humans
    time.sleep(1)

def ledRedOn():
    GPIO.output(8,True)

def ledRedOff():
    GPIO.output(8,False)

def beep():
    #starting beeping in separate thread to not slow down whole application
    thr = thread.start_new_thread(beepAsync, ())

def beepAsync():
    GPIO.output(13,True)
    time.sleep(0.1)
    GPIO.output(13,False)


#Backing up the input attributes, so we can change it for reading single
#character without hitting enter  each time
fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
def getOneKey():
    try:
        tty.setcbreak(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        return ord(ch)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


displayTime=True
def printDateToDisplay():
    while True:
        #Display current time on display, until global variable is set
        if displayTime!=True:
            thread.exit()
        display.lcdWriteFirstLine(time.strftime("%d.%m. %H:%M:%S", time.localtime()))
        onScreen(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()))
        time.sleep(1)

def initGpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(8, GPIO.OUT)
    GPIO.setup(13, GPIO.OUT)

def main():
    GPIO.cleanup()
    try:
        initGpio()
        display.init()
        while True:
            display.lcdWriteSecondLine("Choose an action...")
            global displayTime
            displayTime=true
            #Start new thread to show curent datetime on display
            # and wait for user input on keyboard
            thr = thread.start_new_thread(printDateToDisplay, ())
            a = getOneKey()
            displayTime=False
            if 47 < a < 58:
                readNfc(a)
    except KeyboardInterrupt:
        GPIO.cleanup()
        pass
    GPIO.cleanup()

if __name__ == '__main__':
    debug("----------========== Starting session! ==========----------")
    main()
