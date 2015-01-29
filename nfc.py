#-------------------------------------------------------------------------------
# Name:        NFC Reader
# Purpose:
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
import MFRC522
from attendance import onScreen

def readNfc():
    reading = True
    while reading:
        MIFAREReader = MFRC522.MFRC522()

        #while continue_reading:
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        #if status == MIFAREReader.MI_OK:
        #    print("Card detected")

        (status,backData) = MIFAREReader.MFRC522_Anticoll()
        if status == MIFAREReader.MI_OK:
            #print ("Card Number: "+str(backData[0])+","+str(backData[1])+","+str(backData[2])+","+str(backData[3])+","+str(backData[4]))
            MIFAREReader.AntennaOff()
            reading=False
            return str(backData[0])+str(backData[1])+str(backData[2])+str(backData[3])+str(backData[4])

