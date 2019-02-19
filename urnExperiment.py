
#-----ELSBERG URN REPLICATION--- a few notes

#  - The number of red and blue marbles in the unknown urn is randomised every time the program runs
#  - The txt file 'conditionCount.txt' saves the history of allocations of each condition.
#  - The program allocates the condition once the participant gives consent, but the results and condition count
#   only update after the program has chosen a marble and shown the result.
#  - For the marble choice, the original experiment just states "each participant drew a ball from the chosen urn",
#   so I have used a similar randomisation process (shuffle list and then random choice)as used to decide the number
#   of marbles in the unknown urn.
#  - The participant is only asked for their contact details if they get a blue marble

#-----SET UP AND IMPORT FUNCTIONS-----

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from urnExpUI import *

app = QApplication(sys.argv)
window = QMainWindow()

ui = Ui_urnExpWindow()
ui.setupUi(window)

import random
from myWidgets import ClickableLabel

#Sets stacked widget to centre of window
width = 520
height = 650
windowCentreH = window.width()/2
windowCentreV = window.height()/2
ui.stackedWidget.setGeometry(windowCentreH-width/2,windowCentreV-height/2, width, height)

#Moves to next page in stacked widget - used many times throughout program
def nextPage():
    ui.stackedWidget.setCurrentIndex(ui.stackedWidget.currentIndex() + 1)

#-----CONSENT PAGE AND ALLOCATING THE CONDITION-----

# Allocates participant to 2,10 or 100 marble condition and sets number of marbles in unknown urn.
# Called after participant gives consent
def allocateCondition():

    # Reads txt file for history of previous trials
    file = open("conditionCount.txt", "r", encoding="utf8")
    contents = file.read()
    contentsLst = contents.split("\n")
    file.close()

    window.condCount2 = int(contentsLst[0])
    window.condCount10 = int(contentsLst[1])
    window.condCount100 = int(contentsLst[2])

    condSum = window.condCount2 + window.condCount10 + window.condCount100

    #Adds condition to list only if its proportion of previous trials is equal to or less than 1/3
    #Then condition chosen randomly from that list

    condLst = []


    if window.condCount100 <= condSum / 3:
        condLst.append(100)

    window.cond = random.choice(condLst)

    # Function to set number of marbles in unknown urn
    # This mimics experiment description where numbers were written on paper, shuffled and then drawn at random
    def unknownUrnRatio(marbleCount):

        marbleLst = []
        for i in range(0, marbleCount + 1):
            marbleLst.append(i)

        random.shuffle(marbleLst)

        window.condBlue = random.choice(marbleLst)
        window.condRed = marbleCount - window.condBlue

    unknownUrnRatio(window.cond)

#If consent box is checked, allocates marble condition and moves to next page
def checkConsent():
    if ui.consentBox.isChecked():
        nextPage()
        allocateCondition()

ui.consentConfirm.clicked.connect(checkConsent)

#Randomly sets urn A and B to the unknown or 50:50 marble ratio
urnRatios = ("unknown ratio", "50:50 ratio")
urnPosChoice = random.choice(urnRatios)

if urnPosChoice == "unknown ratio":
    urnA = urnRatios[0]
    urnB = urnRatios[1]
    urnPosition = 1

else:
    urnA = urnRatios[1]
    urnB = urnRatios[0]
    urnPosition = 0

#-------DEMOGRAPHICS, SETTING INSTRUCTIONS AND URN LABELS------------------

ui.labelErrorAge.hide()
ui.labelErrorEducation.hide()
ui.labelErrorGender.hide()

#Checks whether demographic info is entered correctly. Called when participant clicks continue button
def checkDemog():
    emptyFieldCount = 0

    if int(ui.Age.text()) <18:
        ui.labelErrorAge.show()
        emptyFieldCount += 1
    else:
        ui.labelErrorAge.hide()
        window.participantAge = ui.Age.text()

    if ui.Education.currentText() == "":
        ui.labelErrorEducation.show()
        emptyFieldCount += 1
    else:
        ui.labelErrorEducation.hide()
        window.participantEducation = ui.Education.currentText()

    if ui.Female.isChecked() is True:
        ui.labelErrorGender.hide()
        window.participantGender = "Female"
    elif ui.Male.isChecked() is True:
        ui.labelErrorGender.hide ()
        window.participantGender = "Male"
    else:
        ui.labelErrorGender.show()
        emptyFieldCount += 1

    # Sets the instructions only if there are no errors on demographics page
    if emptyFieldCount == 0:
        nextPage()

        if urnPosition == 0:
            setInstructions("Urn A","Urn B",window.cond)
        else:
            setInstructions("Urn B", "Urn A",window.cond)

ui.demogConfirm.clicked.connect(checkDemog)

# Sets instructions depending on condition and whether urn A or B is 50:50 or unknown
def setInstructions(urn5050, urnUnknown, condition):

    if window.cond != 2:
        ui.labelExpInstructions_2.setText(
            urn5050 + " contains " + str(int(condition / 2)) + " red marbles and " + str(int(condition / 2))
            + " blue marbles. " + urnUnknown + " contains " + str(condition) + " marbles in an unknown color ratio,"
            " from " + str(condition) + " red marbles and 0 blue marbles to 0 red marbles and "
            + str(condition) + " blue marbles.")

        ui.labelExpInstructions_3.setText("The mixture of red and blue marbles in " +urnUnknown +
            " has been decided by writing the numbers 0, 1, 2, ...," + str(condition) +
            " on separate slips of paper, shuffling the slips thoroughly, and then drawing one of them at random.")
    else:
        ui.labelExpInstructions_2.setText(
            urn5050 + " contains 1 red marble and 1 blue marble. " + urnUnknown + " contains 2 marbles in an "
            "unknown color ratio, from 2 red marbles and 0 blue marbles to 0 red marbles and 2 blue marbles.")

        ui.labelExpInstructions_3.setText("The mixture of red and blue marbles in " + urnUnknown +
            " has been decided by writing the numbers 0, 1 and 2 on separate slips of paper, shuffling the slips"
            " thoroughly, and then drawing one of them at random.")

    ui.labelExpInstructions_4.setText(
        "The number chosen was used to determine the number of blue marbles to be put into " +
        urnUnknown + ", but you do not know the number. Every possible mixture of red and blue marbles in " +
        urnUnknown + " is equally likely.")

#Sets labels under urns to 50:50 or unknown ratio and shows the clickable urns, after participant has seen instructions
def setUrnLabelText():
    ui.labelUrnAratio.setText(urnA)
    ui.labelUrnBratio.setText(urnB)
    clickableUrnA.show()
    clickableUrnB.show()
    ui.labelUrnChoice.hide()
    ui.labelUrnError.hide()
    nextPage()

ui.instructionConfirm.clicked.connect(setUrnLabelText)

#------URN CHOICE AND SHOWING MARBLE RESULT-------

#Shows a message to confirm to participant what urn they chose, after they've clicked on urn
window.urnChoice = 0

def showUrnChoice(urn):
    ui.labelUrnChoice.setText("You chose the urn with the " +urn)
    ui.labelUrnChoice.show()
    ui.labelUrnError.hide()
    window.urnChoice = urn

#Two clickable labels for Urn A and B -  I've used lambda to pass a parameter (i.e. urnA or urnB) to the slot function
clickableUrnA = ClickableLabel(window)
clickableUrnA.setPixmap(QtGui.QPixmap("urn.jpg"))
clickableUrnA.setGeometry(QtCore.QRect(190, 200, 100, 160))
clickableUrnA.setScaledContents(True)
clickableUrnA.hide()
clickableUrnA.clicked.connect(lambda: showUrnChoice(urnA))

clickableUrnB = ClickableLabel(window)
clickableUrnB.setPixmap(QtGui.QPixmap("urn.jpg"))
clickableUrnB.setGeometry(QtCore.QRect(380, 200, 100, 160))
clickableUrnB.setScaledContents(True)
clickableUrnB.hide()
clickableUrnB.clicked.connect(lambda: showUrnChoice(urnB))

# Animation that moves hand into urn, after participant confirms their urn choice
def animateHand():
    currentY = ui.hand.y()

    if currentY < ui.bigUrn.y():
        ui.hand.setGeometry(210, currentY + 5, 71, 161)
    else:
        window.timer.stop()
        marbleChoice()
        nextPage()

def timerSetup():
    if window.urnChoice != 0:
        nextPage()
        clickableUrnA.hide()
        clickableUrnB.hide()

        window.timer = QTimer()
        window.timer.timeout.connect(animateHand)
        window.timer.start(50)
    else:
        ui.labelUrnError.show()

ui.urnConfirm.clicked.connect(timerSetup)

# Function to randomly choose a marble from selected urn and write results to csv - called when animated hand stops
def marbleChoice():

    # These loops add the correct number of red and blue marbles to each urn
    marbleUnknownLst = []
    for i in range(0,window.condBlue):
        marbleUnknownLst.append("blue")
    for i in range(0, window.condRed):
        marbleUnknownLst.append("red")

    marble5050Lst = []
    for i in range(0, int(window.cond/2)):
        marble5050Lst.append("blue")
        marble5050Lst.append("red")

    # This conditional chooses a marble at random, depending on the urn choice
    if window.urnChoice == "unknown ratio":
        random.shuffle(marbleUnknownLst)
        window.marble = random.choice(marbleUnknownLst)
        window.urnChoice = 0
    else:
        random.shuffle(marble5050Lst)
        window.marble = random.choice(marble5050Lst)
        window.urnChoice = 1

    ui.labelMarbleChoice.setText("You drew a " + window.marble + " marble")

    #Shows picture of the marble picked from the urn and the relevant message
    if window.marble == "blue":
        ui.redMarble.hide()
        ui.blueMarble.show()
        ui.labelPrize.setText("Congratulations. You've been entered into the £30 lottery draw.")

    else:
        ui.blueMarble.hide()
        ui.redMarble.show()
        ui.labelPrize.setText("Sorry, you haven't been entered into the lottery draw.\n\n Click 'Continue'")
        ui.emailWidget.hide()

    #Updates the count of conditions in the txt file
    def writeCondition():

        if window.cond == 2:
            window.condCount2 += 1
        elif window.cond == 10:
            window.condCount10 += 1
        else:
            window.condCount100 += 1

        window.participantNum = window.condCount2 + window.condCount10 + window.condCount100

        file = open("conditionCount.txt", "w", encoding="utf8")
        file.write(str(window.condCount2) + "\n" + str(window.condCount10) + "\n" + str(window.condCount100))
        file.close()

    # Writes the line of participant results to the csv
    def writeResults():

        headingsForCsv = "Participant Number,Age,Gender,Education Level,Condition,Urn Position,Urn Selection,Marble," \
                         "Contact Details"

        participantResults = "\n" + str(window.participantNum) + "," + str(window.participantAge) + "," \
                             + window.participantGender + "," + window.participantEducation + "," + str(window.cond)\
                             + "," + str(urnPosition) + "," + str(window.urnChoice) + "," + window.marble

        # If it is the first participant, adds the column headings
        if window.participantNum == 1:
            resultsCsv = open("results.csv", "w")
            resultsCsv.write(headingsForCsv)
            resultsCsv.write(participantResults)
            resultsCsv.close

        else:
            resultsCsv = open("results.csv", "a")
            resultsCsv.write(participantResults)
            resultsCsv.close

    writeCondition()
    writeResults()

# Asks participant to add email if they go into lottery draw, after they click continue button. Then adds email to csv
ui.labelEmailError.hide()

def writeEmail():

    if window.marble == "blue":
        contactEmail = ui.inputEmail.text()

        if "@" in contactEmail:
            resultsCsv = open("results.csv","a")
            resultsCsv.write("," + contactEmail)
            resultsCsv.close
            nextPage()
        else:
            ui.labelEmailError.show()
    else:
        nextPage()

ui.continueButton.clicked.connect(writeEmail)

ui.endButton.clicked.connect(window.close)

window.show()
sys.exit(app.exec_())





