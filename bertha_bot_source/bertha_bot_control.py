#!/usr/bin/env python
# .. -*- coding: utf-8 -*-
#
# Library imports
# ---------------
import time
#
# Local imports
# -------------
from bertha_bot_base import ButtonGui
from bertha_bot_base import main
from bertha_bot_controller import RobotController
#
# Must import after ``bertha_bot_base`` to get SIP API set
# correctly.
from PyQt4.QtCore import QElapsedTimer, pyqtSlot
#
# ROS Imports
# -----------
import rospy

from PIL import Image

# Set frame size and threshold
w = 640/2
h = 480/2
thresh = 5


class BotControl(ButtonGui):

    #__________________________________________________________________________
    #
    # Block aligment algorithms
    #__________________________________________________________________________
    def blocks_detected1(self, alignment, image, haircut_lower, haircut):

        pil_image = Image.fromarray(image)

        # Load image into pixel array
        pixels = pil_image.load()

        counter = 0
        # Iterate through column
        for i in range(haircut,h-haircut_lower):
            white = True
            # Check pixels color
            for each in pixels[alignment,i]:
                if not(each < 80 or each > 155):
                    white = False
            # Increment for detections
            if(white):
                counter += 1

        # Return true if detections higher than threshold
        return (counter >= thresh)


    def blocks_detected2(self, alignment, image, haircut_lower, haircut):
        
        pil_image = Image.fromarray(image)

        # Load image into pixel array
        pixels = pil_image.load()

        count = 0

        # Iterate through column
        for i in range(haircut,h-haircut_lower):
            # Check pixels color
            white = True
            first = True
            for each in pixels[alignment,i]:
                if(each > 100) or (each < 50):
                    white = False
                if(first):
                    min = each
                    max = each
                    first = False
                else:
                    if(each > max):
                        max = each
                    if(each < min):
                        min = each

            # Increment for detections
            if(max-min >30):
                white = False
            if white:
                count+=1

        # Return true if detections higher than threshold
        return (count >= thresh)


    def checkForDuplicates(self, array):
        # Check to see if duplicates occur
        duplicatesExist = False
        # Iterate through array
        i = 0
        while i <  len(array):
            # Compare current element to every other element
            j = i + 1
            while j < len(array):
                if array[i] == array[j]:
                    duplicatesExist = True
                j += 1
            i += 1
        
        return duplicatesExist
                
            
    #__________________________________________________________________________
    #
    # Rail cart alignment algorithm
    #__________________________________________________________________________
    def alignWithCartRight2Left(self):

        print "CART ARRAY: ", self.railCartArray
        self.setTrackingColor(self.controller.railCartColorMatrix[self.railCartArray[0]])

        print self.x_center
        if (self.x_center >= 120):
            if (self.x_center >= 120) and (self.countRecalulateCenter == 1):
                self.countRecalulateCenter = 0
                self.alignWithCartR2L = False
                self.alignPub.publish(True)
            self.countRecalulateCenter += 1    
        else:
            pass


    def alignWithCartLeft2Right(self):

        self.setTrackingColor(self.controller.railCartColorMatrix[self.railCartArray[0]])

        print self.x_center
        if (self.x_center <= 180):
            if (self.x_center <= 180) and (self.countRecalulateCenter == 1):
                self.countRecalulateCenter = 0
                self.alignWithCartL2R = False
                self.alignPub.publish(True)
            self.countRecalulateCenter += 1  
        else:
            pass

    # Reverse railcart array for second course orientation.
    def reverseArray(self, array):
        newArray = [None] * len(array)
        for index in xrange(len(array)):
            newArray[index] = array[len(array)-(index+1)]
        return newArray


    #__________________________________________________________________________
    #
    # Vision parameters for GUI
    #__________________________________________________________________________

    def on_hsThreshold_valueChanged(self, value):
        print(value)

    # Show current tracking color
    def updateTrackingColorLabel(self, s):
        self.lbAuto_2.setText(s)

    def updateCenterPositions(self, x, y):
        self.lbAuto_3.setText(x)
        self.lbAuto_4.setText(y)


    #__________________________________________________________________________
    #
    # Color Sensing Functions for GUI
    #__________________________________________________________________________

    def on_pbScan_pressed(self):
        print("Scanning Blocks")
        sensorData = self.controller.scanBlocks()
        self.setColorGui(sensorData)
        print("Blocks have been scanned")

    def on_pbScan_released(self):
        print("Scan Released")
        
    def setColorGui(self, data):
        sensorArray = ['error','error','error','error','error','error','error','error']

        for i in xrange(len(data)):
            if(data[i] == 0):
                sensorArray[i] = 'error'
            elif(data[i] == 1):
                sensorArray[i] = 'blue'
            elif(data[i] == 2):
                sensorArray[i] = 'green'
            elif(data[i] == 3):
                sensorArray[i] = 'red'
            elif(data[i] == 4):
                sensorArray[i] = 'yellow'

        self.lef1.setText("F: "+str(sensorArray[0]))
        self.leb1.setText("B: "+str(sensorArray[1]))
        self.lef2.setText("F: "+str(sensorArray[2]))
        self.leb2.setText("B: "+str(sensorArray[3]))
        self.lef3.setText("F: "+str(sensorArray[4]))
        self.leb3.setText("B: "+str(sensorArray[5]))
        self.lef4.setText("F: "+str(sensorArray[6]))
        self.leb4.setText("B: "+str(sensorArray[7]))


    #__________________________________________________________________________
    #
    # Platform height commands for GUI
    #__________________________________________________________________________
    # Raise 2 inches
    def on_pbRaise2in_pressed(self):
        print("Raise 2 Inches Pressed")
        self.controller.SetNavCommand(50)
    #def on_pbRaise2in_released(self):
    #    print("Raise 2 Inches Released")
    #    self.controller.SetNavCommand(46)

    # Raise 3 inches
    def on_pbRaise3in_pressed(self):
        print("Raise 3 Inches Pressed")
        self.controller.SetNavCommand(54)
    #def on_pbRaise3in_released(self):
    #    print("Raise 3 Inches Released")
    #    self.controller.SetNavCommand(46)

    # Lower 2 inches
    def on_pbLower2in_pressed(self):
        print("Lower 2 Inches Pressed")
        self.controller.SetNavCommand(58)
    #def on_pbLower2in_released(self):
    #    print("Lower 2 Inches Released")
    #    self.controller.SetNavCommand(46)

    # Lower 3 inches
    def on_pbLower3in_pressed(self):
        print("Lower 3 Inches Pressed")
        self.controller.SetNavCommand(62)
    #def on_pbLower3in_released(self):
    #    print("Lower 3 Inches Released")
    #    self.controller.SetNavCommand(58)

    #__________________________________________________________________________
    #
    # Navigation Commands for GUI
    #__________________________________________________________________________
    def on_pbForward_pressed(self):
        print("Forward Pressed")
        self.controller.SetNavCommand(76)
    def on_pbForward_released(self):
        print("Forward Released")
        self.controller.SetNavCommand(46)

    def on_pbBack_pressed(self):
        print("Backward Pressed")
        self.controller.SetNavCommand(108)
    def on_pbBack_released(self):
        print("Backward Released")
        self.controller.SetNavCommand(0x2e)

    def on_pbLeft_pressed(self):
        print("Left Pressed")
        self.controller.SetNavCommand(140)
    def on_pbLeft_released(self):
        print("Left Released")
        self.controller.SetNavCommand(46)

    def on_pbRight_pressed(self):
        print("Right Pressed")
        self.controller.SetNavCommand(172)
    def on_pbRight_released(self):
        print("Right Released")
        self.controller.SetNavCommand(46)

    def on_pbRLeft_pressed(self):
        print("Rotate Left Pressed")
        self.controller.SetNavCommand(232)
    def on_pbRLeft_released(self):
        print("Rotate Left Released")
        self.controller.SetNavCommand(46)

    def on_pbRRight_pressed(self):
        print("Rotate Right Pressed")
        self.controller.SetNavCommand(200)
    def on_pbRRight_released(self):
        print("Rotate Right Released")
        self.controller.SetNavCommand(46)

    def on_pbRaisePlatform_pressed(self):
        print("Raise Platform Pressed")
        self.controller.SetNavCommand(50)
    def on_pbRaisePlatform_released(self):
        print("Raise Platform Released")
        self.controller.SetNavCommand(0x2e)


    #__________________________________________________________________________
    #
    # Gate and Arm Functions for GUI
    #__________________________________________________________________________

    def on_pbArmExtend_pressed(self):
        print("Arm is Extending")
        self.controller.SetSortCommand(3)
    def on_pbArmExtend_released(self):
        self.controller.SetSortCommand(40)

    def on_pbArmRetract_pressed(self):
        print("Arm is Retracting")
        self.controller.SetSortCommand(4)
    def on_pbArmRetract_released(self):
        self.controller.SetSortCommand(40)

    def on_pbGateLift_pressed(self):
        print("Gate is Lifting")
        self.controller.SetSortCommand(5)
    def on_pbGateLift_released(self):
        self.controller.SetSortCommand(40)

    def on_pbGateLower_pressed(self):
        print("Gate is Lowering")
        self.controller.SetSortCommand(6)
    def on_pbGateLower_released(self):
        self.controller.SetSortCommand(40)

    # Explain what the robot is doing
    def updateAutoLabel(self, s):
        self.lbAuto.setText(s)


    #__________________________________________________________________________
    #
    # Block Handling Commands for GUI
    #__________________________________________________________________________

    def on_pbClearCommand_pressed(self):
        self.controller.SetSortCommand(40)

    def on_rbFullBlock_clicked(self):
        self.rbHalfBlock.setChecked(False)

    def on_rbHalfBlock_clicked(self):
        self.rbFullBlock.setChecked(False)

    def on_pbEjectAll_pressed(self):
        print("Retracting All Rows")
        if self.rbFullBlock.isChecked() == True:
            # Do command to retract a full block
            print("Full Block")
            self.controller.SetSortCommand(1)
        elif self.rbHalfBlock.isChecked() == True:
            # Do command to retract a half block
            print("Half Block")
            self.controller.SetSortCommand(40)

    def on_pbRetractAll_pressed(self):
        print("Retracting All Rows")
        if self.rbFullBlock.isChecked() == True:
            # Do command to retract a full block
            print("Full Block")
            self.controller.SetSortCommand(2)
        elif self.rbHalfBlock.isChecked() == True:
            # Do command to retract a half block
            print("Half Block")
            self.controller.SetSortCommand(40)
        
    def on_pbC1TE_pressed(self):
        print("Ejecting Top Row of Channel 1")
        if (self.rbFullBlock.isChecked() == True):
            # Do command to eject a full block
            self.controller.SetSortCommand(13)
            print("Full Block")
        elif (self.rbHalfBlock.isChecked() == True):
            # Do command to eject a half block
            print("Half Block")
            self.controller.SetSortCommand(29)

    def on_pbC1TR_pressed(self):
        print("Retracting Top Row of Channel 1")
        if (self.rbFullBlock.isChecked() == True):
            # Do command to retract a full block
            print("Full Block")
            self.controller.SetSortCommand(14)
        elif (self.rbHalfBlock.isChecked() == True):
            # Do command to retract a half block
            print("Half Block")
            self.controller.SetSortCommand(30)

    def on_pbC1BE_pressed(self):
        print("Ejecting Bottom Row of Channel 1")
        if (self.rbFullBlock.isChecked() == True):
            # Do command to eject a full block
            print("Full Block")
            self.controller.SetSortCommand(21)
        elif (self.rbHalfBlock.isChecked() == True):
            # Do command to eject a half block
            print("Half Block")
            self.controller.SetSortCommand(37)

    def on_pbC1BR_pressed(self):
        print("Retracting Bottom Row of Channel 1")
        if (self.rbFullBlock.isChecked() == True):
            # Do command to retract a full block
            print("Full Block")
            self.controller.SetSortCommand(22)
        elif (self.rbHalfBlock.isChecked() == True):
            # Do command to retract a half block
            print("Half Block")
            self.controller.SetSortCommand(38)



    def on_pbC2TE_pressed(self):
        print("Ejecting Top Row of Channel 2")
        if (self.rbFullBlock.isChecked() == True):
            # Do command to eject a full block
            print("Full Block")
            self.controller.SetSortCommand(11)
        elif (self.rbHalfBlock.isChecked() == True):
            # Do command to eject a half block
            print("Half Block")
            self.controller.SetSortCommand(27)

    def on_pbC2TR_pressed(self):
        print("Retracting Top Row of Channel 2")
        if (self.rbFullBlock.isChecked() == True):
            # Do command to retract a full block
            print("Full Block")
            self.controller.SetSortCommand(12)
        elif (self.rbHalfBlock.isChecked() == True):
            # Do command to retract a half block
            print("Half Block")
            self.controller.SetSortCommand(28)

    def on_pbC2BE_pressed(self):
        print("Ejecting Bottom Row of Channel 2")
        if (self.rbFullBlock.isChecked() == True):
            # Do command to eject a full block
            print("Full Block")
            self.controller.SetSortCommand(19)
        elif (self.rbHalfBlock.isChecked() == True):
            # Do command to eject a half block
            print("Half Block")
            self.controller.SetSortCommand(35)

    def on_pbC2BR_pressed(self):
        print("Retracting Bottom Row of Channel 2")
        if (self.rbFullBlock.isChecked() == True):
            # Do command to retract a full block
            print("Full Block")
            self.controller.SetSortCommand(20)
        elif (self.rbHalfBlock.isChecked() == True):
            # Do command to retract a half block
            print("Half Block")
            self.controller.SetSortCommand(36)



    def on_pbC3TE_pressed(self):
        print("Ejecting Top Row of Channel 3")
        if (self.rbFullBlock.isChecked() == True):
            # Do command to eject a full block
            print("Full Block")
            self.controller.SetSortCommand(9)
        elif (self.rbHalfBlock.isChecked() == True):
            # Do command to eject a half block
            print("Half Block")
            self.controller.SetSortCommand(25)

    def on_pbC3TR_pressed(self):
        print("Retracting Top Row of Channel 3")
        if (self.rbFullBlock.isChecked() == True):
            # Do command to retract a full block
            print("Full Block")
            self.controller.SetSortCommand(10)
        elif (self.rbHalfBlock.isChecked() == True):
            # Do command to retract a half block
            print("Half Block")
            self.controller.SetSortCommand(26)

    def on_pbC3BE_pressed(self):
        print("Ejecting Bottom Row of Channel 3")
        if (self.rbFullBlock.isChecked() == True):
            # Do command to eject a full block
            print("Full Block")
            self.controller.SetSortCommand(17)
        elif (self.rbHalfBlock.isChecked() == True):
            # Do command to eject a half block
            print("Half Block")
            self.controller.SetSortCommand(33)

    def on_pbC3BR_pressed(self):
        print("Retracting Bottom Row of Channel 3")
        if (self.rbFullBlock.isChecked() == True):
            # Do command to retract a full block
            print("Full Block")
            self.controller.SetSortCommand(18)
        elif (self.rbHalfBlock.isChecked() == True):
            # Do command to retract a half block
            print("Half Block")
            self.controller.SetSortCommand(34)



    def on_pbC4TE_pressed(self):
        print("Ejecting Top Row of Channel 4")
        if (self.rbFullBlock.isChecked() == True):
            # Do command to eject a full block
            print("Full Block")
            self.controller.SetSortCommand(7)
        elif (self.rbHalfBlock.isChecked() == True):
            # Do command to eject a half block
            print("Half Block")
            self.controller.SetSortCommand(23)

    def on_pbC4TR_pressed(self):
        print("Retracting Top Row of Channel 4")
        if (self.rbFullBlock.isChecked() == True):
            # Do command to retract a full block
            print("Full Block")
            self.controller.SetSortCommand(8)
        elif (self.rbHalfBlock.isChecked() == True):
            # Do command to retract a half block
            print("Half Block")
            self.controller.SetSortCommand(24)

    def on_pbC4BE_pressed(self):
        print("Ejecting Bottom Row of Channel 4")
        if (self.rbFullBlock.isChecked() == True):
            # Do command to eject a full block
            print("Full Block")
            self.controller.SetSortCommand(15)
        elif (self.rbHalfBlock.isChecked() == True):
            # Do command to eject a half block
            print("Half Block")
            self.controller.SetSortCommand(31)

    def on_pbC4BR_pressed(self):
        print("Retracting Bottom Row of Channel 4")
        if (self.rbFullBlock.isChecked() == True):
            # Do command to retract a full block
            print("Full Block")
            self.controller.SetSortCommand(16)
        elif (self.rbHalfBlock.isChecked() == True):
            # Do command to retract a half block
            print("Half Block")
            self.controller.SetSortCommand(32)


if __name__=='__main__':
    main(BotControl)
