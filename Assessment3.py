
#-- A partial replication of 'Do as I say, Don't Do as I Do...' (2015)
#-- A few notes --

#  - The order of the two experiments is randomised every time the program runs
#  - The txt file 'expOrderCount.txt' saves the history of the experiment orders.
#  - The program allocates the experiment order once the participant gives consent, but the results and condition
#  count only update after the program has completed both experiments and the rightness ratings.

#-----SET UP AND IMPORT FUNCTIONS-----

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from trolley import *
from myWidgets import ClickableLabel
import random

app = QApplication(sys.argv)
window = QMainWindow()

ui = Ui_trolleyWindow()
ui.setupUi(window)

# Sets stacked widget to centre of window
width = 670
height = 520
windowCentreH = window.width()/2
windowCentreV = window.height()/2
ui.stackedWidget.setGeometry(windowCentreH-width/2,windowCentreV-height/2, width, height)

# Function to randomly set the order of the two experiments
def experimentOrder():

    # Reads txt file for history of previous participants
    file = open("expOrderCount.txt", "r", encoding="utf8")
    contents = file.read()
    contentsLst = contents.split("\n")
    file.close()

    window.condSidetrack1st = int(contentsLst[0])
    window.condFootbridge1st = int(contentsLst[1])

    condSum = window.condSidetrack1st + window.condFootbridge1st

    expOrderLst = []

    if window.condSidetrack1st <= condSum / 2:
        expOrderLst.append(0)
    if window.condFootbridge1st <= condSum / 2:
        expOrderLst.append(1)

    window.expOrder = random.choice(expOrderLst)

#Functions to move to pages in stacked widget - used throughout program
def nextPage():
    ui.stackedWidget.setCurrentIndex(ui.stackedWidget.currentIndex() + 1)

def sidetrackPage():
    ui.stackedWidget.setCurrentIndex(4)
    # starts the timer for the animation in the first Demo of the Sidetrack scenario
    timerSetupSidetrackDemo1()

def footbridgePage():
    ui.stackedWidget.setCurrentIndex(8)
    # starts the timer for the animation in the first Demo of the Footbridge scenario
    timerSetupFootbridgeDemo1()

def debriefPage():
    ui.stackedWidget.setCurrentIndex(12)

#---- CONSENT, DEMOGRAPHICS, BROCHURE and INSTRUCTION PAGES---

#If consent box is checked, function allocates experiment order and moves to next page
def checkConsent():
    if ui.consentBox.isChecked():
        nextPage()
        experimentOrder()

ui.consentContinueButton.clicked.connect(checkConsent)

# Hides all the error messages for demographics
ui.labelErrorAge.hide()
ui.labelErrorEducation.hide()
ui.labelErrorGender.hide()

#Checks whether demographic info is entered correctly. Called when participant clicks continue button
def checkDemog():
    emptyFieldCount = 0

    # conditional for age
    if int(ui.Age.text()) <18:
        ui.labelErrorAge.show()
        emptyFieldCount += 1
    else:
        ui.labelErrorAge.hide()
        window.participantAge = ui.Age.text()

    # conditional for education status
    if ui.Education.currentText() == "":
        ui.labelErrorEducation.show()
        emptyFieldCount += 1
    else:
        ui.labelErrorEducation.hide()
        window.participantEducation = ui.Education.currentText()

    # conditional for gender
    if ui.Female.isChecked() is True:
        ui.labelErrorGender.hide()
        window.participantGender = "Female"
    elif ui.Male.isChecked() is True:
        ui.labelErrorGender.hide()
        window.participantGender = "Male"
    else:
        ui.labelErrorGender.show()
        emptyFieldCount += 1

    # Got to next page only if the count of errors on demographics page is 0
    if emptyFieldCount == 0:
        nextPage()

ui.demogContinueButton.clicked.connect(checkDemog)

# Instructions for each experiment
instructionsSidetrack = "In this scenario you have to decide whether to flick a switch to divert the ball before it" \
                        " crosses the line. You can only press the switch once and you cannot change your decision." \
                        " Before you make your decision, you will see two demonstrations, one where the switch" \
                        " is not pressed and one where it is. You must watch the demos in full before you can continue."

instructionsFootbridge = "In this scenario you have to decide whether to push a child into the path of the ball before" \
                         " it crosses the line. To push the child you must click on their photo. You can only do this" \
                         " once and cannot change your decision.  Before you make your decision, you will see two" \
                         " demonstrations, one where the child is pushed and one where it is not." \
                         " You must watch the demos in full before you can continue."

#  Function to set text in instructions page, based on the order set by ExperimentOrder
def setInstructions():
    nextPage()
    if window.expOrder == 0:
        ui.instructionsExp1.setText(instructionsSidetrack)
        ui.instructionsExp2.setText(instructionsFootbridge)
    else:
        ui.instructionsExp1.setText(instructionsFootbridge)
        ui.instructionsExp2.setText(instructionsSidetrack)

ui.brochureContinueButton.clicked.connect(setInstructions)

# Function to go to first experiment, depending on order. Connects after instructions.
def firstExperiment():
    if window.expOrder == 0:
        sidetrackPage()
    else:
        footbridgePage()

ui.instructContinueButton.clicked.connect(firstExperiment)

# --- FUNCTIONS USED ACROSS DEMOS AND EXPERIMENTS ----

# Text used in label boxes during demos and experiment
continueDemoText = "Press 'Continue' to go the next demonstration."
continueExpText = "Press 'Continue' to make your decision."

# Function to set up timer to animate ball moving across screen - used in every demo and experiment
def setupBallTimer():
    window.timer = QTimer()
    window.timer.start(20)

# Function to flick switch or push in the second demos, after a set interval (currently 5 seconds)
def setupDemoTimer(action):
    window.timerDemo2 = QTimer()
    window.timerDemo2.timeout.connect(action)
    window.timerDemo2.start(2000)
    window.timerDemo2.setSingleShot(True)

# Timer which fires every ms, used in both experiments to update repsonse time
def setupResponseTimer(responseUpdate):
     window.timerResponse = QTimer()
     window.timerResponse.timeout.connect(responseUpdate)
     window.timerResponse.start(1)

# -----SIDE-TRACK -----#

# Function to start ball moving across screen in sidetrack - used in both demos and experiment
# Arguments are all the relevant objects in the window. Label = 0 because there is no label in the actual experiment.
# Label is just updated in the demos.

def startBallSidetrack(ball,line,showbutton,defaultGroup,sidetrack,label = 0):

    currentX = ball.x()
    currentY = ball.y()

    # Ball moves to left, until it gets to line
    if currentX > line.x():
        ball.setGeometry(currentX - 1,130,41,41)
    else:

        # Diverts ball towards the default group if user does not press switch
        if window.ballpathSidetrack == 0:
            if currentX > (defaultGroup.x() + defaultGroup.width() - ball.width()/2):
                ball.setGeometry(currentX - 2, currentY - 1, 41, 41)
            else:
                window.timer.stop()
                showbutton.show() #Once the ball stops, shows the continue button and sets text in label
                if label is not 0:
                    label.setText(continueDemoText)

        # Diverts ball towards the sidetrack group if user has pressed switch
        else:
            if currentX > (sidetrack.x() + sidetrack.width() - ball.width()/2):
                ball.setGeometry(currentX - 2, currentY + 1, 41, 41)
            else:
                window.timer.stop() #Once the ball stops, shows the continue button and sets text in label
                showbutton.show()
                if label is not 0:
                    label.setText(continueExpText)

# -- Side-track DEMO 1 --

# Sets direction path of ball to 0 (i.e. to the default group) and hides continue button
window.ballpathSidetrack = 0
ui.continueSidetrackDemo1Button.hide()

# Function to start Demo 1
def timerSetupSidetrackDemo1():
    setupBallTimer()
    window.timer.timeout.connect(lambda: startBallSidetrack(ui.ballSidetrackDemo1,ui.lineSidetrackDemo1,
                                                   ui.continueSidetrackDemo1Button,ui.groupDefaultDemo1,
                                                    ui.groupSacrificeDemo1,ui.infoLabelSidetrackDemo1))
                                #lambda used here (and in other similar functions below) to pass the arguments
                                # to the function startBallSidetrack

# -- Side-track DEMO 2 --

# Hides the image of the switch (after its pressed)
ui.switchSidetrackDemo2.hide()
ui.continueSidetrackDemo2Button.hide()

# Function to start Demo 2
def timerSetupSideDemo2():
    nextPage()
    setupBallTimer()
    setupDemoTimer(flickSwitchDemo2)
    window.timer.timeout.connect(lambda: startBallSidetrack(ui.ballSidetrackDemo2, ui.lineSidetrackDemo2,
                                                   ui.continueSidetrackDemo2Button,ui.groupDefaultDemo2,
                                                            ui.groupSacrificeDemo2,ui.infoLabelSidetrackDemo2))


# Hides the first switch image and shows the second switch (after the switch press)
def flickSwitchDemo2():
    ui.switchSidetrackDemo2.show()
    ui.switchDefaultDemo2.hide()
    window.ballpathSidetrack = 1

ui.continueSidetrackDemo1Button.clicked.connect(timerSetupSideDemo2)

# -- Side-track EXPERIMENT --

# Hides switch and continue button
ui.switchSidetrackExp.hide()
ui.continueSidetrackExpButton.hide()

# Function to set up Sidetrack experiment
# Starts timer for ball animation and another timer that records the response time if user presses the Switch
def timerSetupSidetrackExp():
    nextPage()
    window.ballpathSidetrack = 0
    setupResponseTimer(updateSwitchTime)
    setupBallTimer()
    window.timer.timeout.connect(lambda: startBallSidetrack(ui.ballSidetrackExp,ui.lineSidetrackExp,
                                                   ui.continueSidetrackExpButton,ui.groupDefault,ui.personSidetrack))

ui.continueSidetrackDemo2Button.clicked.connect(timerSetupSidetrackExp)

# counter for response time of participant pressing Switch button.
window.switchButtonTime = 0

# adds 1 to counter after every ms of timer
def updateSwitchTime():
    window.switchButtonTime += 1

# Function to flick switch if ball has not crossed line - connects when switch button pressed
def flickSwitch():

    currentX = ui.ballSidetrackExp.x()

    #Changes switch and stops response time counter
    if currentX > ui.lineSidetrackExp.x():
        ui.switchSidetrackExp.show()
        ui.switchDefaultExp.hide()
        window.ballpathSidetrack = 1
        window.timerResponse.stop()

ui.switchButtonExp.clicked.connect(flickSwitch)

ui.continueSidetrackExpButton.clicked.connect(nextPage)

# -- Side-track RATING --

ui.labelSidetrackRatingError.hide()

# Function checks that one of the radio buttons is checked
# If yes, goes to debrief page (and writes results) or to footbridge, depending on trial order

def nextExperimentSidetrack():

    if ui.sidetrackButtonGroup.checkedButton() is not None:
        window.sidetrackRating = ui.sidetrackButtonGroup.checkedButton().text()

        if window.expOrder == 0:
            footbridgePage()
        else:
            debriefPage()
            writeResults()

    else:
        ui.labelSidetrackRatingError.show()

ui.confirmSidetrackRatingButton.clicked.connect(nextExperimentSidetrack)

# ----- FOOTBRIDGE -----#

# Function to start ball moving across screen in footbridge - used in both demos and experiment
# Arguments are all the relevant objects in the window. Label = 0 because there is no label in the actual experiment.
# Label is just updated in the demos.
def startBallFootbridge(ball,line,showbutton,group,label = 0):

    currentX = ball.x()

    # ball moves to left, until it gets to line
    if currentX > line.x():
        ball.setGeometry(currentX - 1,130,41,41)
    else:
        #If child not pushed, ball moves towards group
        if window.ballpathFootbridge == 0:
            if currentX > (group.x() + group.width() - ball.width()/2):
                ball.setGeometry(currentX - 1,130,41, 41)
            else:
                window.timer.stop()
                showbutton.show()
                if label is not 0:
                    label.setText(continueDemoText)

        # If child pushed, balls stop at the line
        else:
            window.timer.stop()
            showbutton.show()
            if label is not 0:
                label.setText(continueExpText)

# -- Footbridge DEMO 1 --

# Sets direction path of ball to 0 (i.e. to the default group) and hides continue button
window.ballpathFootbridge = 0
ui.continueFootbridgeDemo1Button.hide()

# Function to start Demo 1
def timerSetupFootbridgeDemo1():
    setupBallTimer()
    window.timer.timeout.connect(lambda: startBallFootbridge(ui.ballFootbridgeDemo1,ui.lineFootbridgeDemo1,
                                                             ui.continueFootbridgeDemo1Button,
                                                             ui.groupFootbridgeDemo1,ui.infoLabelFootbridgeDemo1))

# -- Footbridge DEMO 2 --

# Hides the picture of the pushed group and continue button
ui.groupSacrificeFootbridgeDemo2_2.hide()
ui.continueFootbridgeDemo2Button.hide()

# Function to start Demo 2
def timerSetupFootbridgeDemo2():
    nextPage()
    setupBallTimer()
    setupDemoTimer(pushDemo2)
    window.timer.timeout.connect(lambda: startBallFootbridge(ui.ballFootbridgeDemo2, ui.lineFootbridgeDemo2,
                                                             ui.continueFootbridgeDemo2Button,ui.groupFootbridgeDemo2,
                                                             ui.infoLabelFootbridgeDemo2))

# Shows the picture of the pushed group (and hides original picture)
def pushDemo2():
    ui.groupSacrificeFootbridgeDemo2_2.show()
    ui.groupSacrificeFootbridgeDemo2.hide()
    window.ballpathFootbridge = 1

ui.continueFootbridgeDemo1Button.clicked.connect(timerSetupFootbridgeDemo2)

# -- Footbridge EXPERIMENT --

# Hides picture of pushed child and continue button
ui.personFootbridgeSacrifice2.hide()
ui.continueFootbridgeExpButton.hide()

# Function to start experiment
def timerSetupFootbridgeExp():
    nextPage()
    window.ballpathFootbridge = 0
    setupResponseTimer(updatePushTime)
    setupBallTimer()
    clickableChild.show()
    window.timer.timeout.connect(lambda: startBallFootbridge(ui.ballFootbridgeExp,ui.lineFootbridgeExp,
                                                             ui.continueFootbridgeExpButton,ui.groupFootbridgeExp))

ui.continueFootbridgeDemo2Button.clicked.connect(timerSetupFootbridgeExp)

# counter for response time of participant if they press 'Push' button.
window.pushButtonTime = 0

def updatePushTime():
    window.pushButtonTime += 1

# Function to push person into path of ball and stops timer to record response time
# Only if ball has not crossed the line
def pushPerson():
    currentX = ui.ballFootbridgeExp.x()

    if currentX > ui.lineFootbridgeExp.x():
        ui.personFootbridgeSacrifice2.show()
        ui.personFootbridgeSacrifice1.hide()
        window.ballpathFootbridge = 1
        window.timerResponse.stop()

# Clickable label for child - connects to PushPerson function when clicked
clickableChild = ClickableLabel(ui.personFootbridgeSacrifice1)
clickableChild.setPixmap(QtGui.QPixmap("Boy2.png"))
clickableChild.setGeometry(QtCore.QRect(0, 0, 50, 50))
clickableChild.setScaledContents(True)
clickableChild.hide()
clickableChild.clicked.connect(pushPerson)

ui.continueFootbridgeExpButton.clicked.connect(nextPage)

# -- Footbridge RATING --

ui.labelFootbridgeRatingError.hide()

# Function checks that one of the radio buttons is checked
# If yes, goes to debrief page (and writes results) or to sidetrack depending on experiment order

def nextExperimentFootbridge():

    if ui.footbridgeButtonGroup.checkedButton() is not None:
        window.footbridgeRating = ui.footbridgeButtonGroup.checkedButton().text()

        if window.expOrder == 0:
            debriefPage()
            writeResults()
        else:
            sidetrackPage()

    else:
        ui.labelFootbridgeRatingError.show()

# After confirming rating, goes to next experiment
ui.confirmFootbridgeRatingButton.clicked.connect(nextExperimentFootbridge)

# ------UPDATING RESULTS FILE------

#Updates the count of conditions in the txt file
def writeCondition():
    
    if window.expOrder == 0:
        window.condSidetrack1st += 1
    else:
        window.condFootbridge1st += 1

    window.participantNum = window.condSidetrack1st + window.condFootbridge1st

    file = open("expOrderCount.txt", "w", encoding="utf8")
    file.write(str(window.condSidetrack1st) + "\n" + str(window.condFootbridge1st))
    file.close()

# Writes the line of participant results to the csv
def writeResults():

    writeCondition()

    headingsForCsv = "Participant Number,Age,Gender,Education Level,Experiment Order,Sidetrack Action,"\
                     "Sidetrack Response Time,Sidetrack Rightness Rating,Footbridge Action,"\
                     "Footbridge Response Time,Footbridge Rightness Rating"

    # sets switch and push response times to 0 if participant did not press switch or push
    if window.ballpathSidetrack == 0:
        window.switchButtonTime = 0

    if window.ballpathFootbridge == 0:
        window.pushButtonTime = 0

    participantResults = "\n" + str(window.participantNum) + "," + str(window.participantAge) + "," \
                       + window.participantGender + "," + window.participantEducation + "," + str(window.expOrder) \
                         + "," + str(window.ballpathSidetrack) + "," + str(window.switchButtonTime) + "," \
                        + str(window.sidetrackRating) + "," + str(window.ballpathFootbridge) + "," + \
                        str(window.pushButtonTime) + "," + str(window.footbridgeRating)


    # If it is the first participant, adds the column headings and results
    if window.participantNum == 1:
        resultsCsv = open("results.csv", "w")
        resultsCsv.write(headingsForCsv)
        resultsCsv.write(participantResults)
        resultsCsv.close
    
    # else adds results to next row
    else:
        resultsCsv = open("results.csv", "a")
        resultsCsv.write(participantResults)
        resultsCsv.close

#Closes the window if participant clicks 'End Experiment' button
ui.endButton.clicked.connect(window.close)

window.show()
sys.exit(app.exec_())





