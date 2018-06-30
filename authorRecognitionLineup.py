from __future__ import print_function, division
from psychopy import event, sound, logging
from psychopy import visual, event, sound, tools
import numpy as np
import string
from math import floor
from copy import deepcopy

def calcRespYandBoundingBox(possibleResps, i):
    x = -.95
    spacingCtrToCtr = 2.0 / len(possibleResps)
    charHeight = spacingCtrToCtr/2
    startY = 1-charHeight/2 #top , to bottom
    makeWayForInstructions = True
    if makeWayForInstructions:
        startY -= .1
    increment = i*spacingCtrToCtr
    increment*=- 1 #go down from top
    y = startY + increment
    boxWidth = .2 #0.1
    boxHeight = spacingCtrToCtr
    return x,y, boxWidth, boxHeight

def drawRespOption(myWin,bgColor,xStart,color,drawBoundingBox,relativeSize,possibleResps,i):
        #relativeSize multiplied by standard size to get desired size
        x,y, w, h = calcRespYandBoundingBox( possibleResps, i )
        alignHoriz = 'left'
        if alignHoriz == 'left':
            rectX= x+w/2
        if relativeSize != 1: #erase bounding box so erase old letter before drawing new differently-sized letter 
            boundingBox = visual.Rect(myWin,width=w,height=h, pos=(rectX,y), fillColor=bgColor, lineColor='red', units='norm' ,autoLog=False) 
            boundingBox.draw()
        option = visual.TextStim(myWin,colorSpace='rgb',color=color,alignHoriz=alignHoriz, alignVert='center',
                                                                    height=h*relativeSize,units='norm',autoLog=False)
        option.setText(possibleResps[i])
        option.pos = (x, y)
        option.draw()
        if drawBoundingBox:
            boundingBox = visual.Rect(myWin,width=w,height=h, pos=(rectX,y), units='norm')
            boundingBox.draw()
        
def drawResponseArray(myWin,bgColor,xStart,possibleResps,selected,selectedColor):
    '''selected indicated whether each is selected or not
    possibleResps is array of all the authors to populate the screen with.
    '''
    numResps = len(possibleResps)
    dimRGB = -.3
    drawBoundingBox = True #to debug to visualise response regions, make True

    #Draw it vertically, from top to bottom
    for i in xrange(len(possibleResps)):
        if selected[i]:
            color = selectedColor
        else: 
            color = (1,1,1)
        relativeHeight = .3
        drawRespOption(myWin,bgColor,xStart,color,drawBoundingBox,relativeHeight,possibleResps,i)

def checkForOKclick(mousePos,respZone):
    OK = False
    if respZone.contains(mousePos):
            OK = True
    return OK

def convertXYtoNormUnits(XY,currUnits,win):
    if currUnits == 'norm':
        return XY
    else:
        widthPix = win.size[0]
        heightPix = win.size[1]
        if currUnits == 'pix':
            xNorm = XY[0]/ (widthPix/2)
            yNorm = XY[1]/ (heightPix/2)
        elif currUnits== 'deg':
            xPix = tools.monitorunittools.deg2pix(XY[0], win.monitor, correctFlat=False)
            yPix = tools.monitorunittools.deg2pix(XY[1], win.monitor, correctFlat=False)
            xNorm = xPix / (widthPix/2)
            yNorm = yPix / (heightPix/2)
            #print("Converted ",XY," from ",currUnits," units first to pixels: ",xPix,yPix," then to norm: ",xNorm,yNorm)
    return xNorm, yNorm

def collectLineupResponses(myWin,bgColor,myMouse,minMustClick,maxCanClick,instructionStim,OKtextStim,OKrespZone,mustDeselectMsgStim,possibleResps,clickSound,badClickSound):
   
   myMouse.clickReset()
   whichResp = -1
   state = 'waitingForAnotherSelection' 
   #waitingForAnotherSelection means OK is  not on the screen, so must click a lineup item
   #'finished' exit this lineup, choice has been made
   expStop = False
   xStart = -.7
   #Calculate how many names in a column
   namesPerColumn = 16
   numColumns = len(possibleResps) / namesPerColumn
   #Need to maintain a list of selected. Draw those in another color
   selected = [0] * len(possibleResps)
   selectedColor = (1,1,-.5)

   while state != 'finished' and not expStop:
        #draw everything corresponding to this state
        #draw selecteds in selectedColor, remainder in white
        instructionStim.draw()
        #print('state = ',state)
        drawResponseArray(myWin,bgColor,xStart,possibleResps,selected,selectedColor)
        if state == 'waitingForAnotherSelection':
            #buttonThis = np.where(pressed)[0] #assume only one button can be recorded as pressed
            #drawRespOption(myWin,bgColor,constCoord,selectedColor,False,1.5,possibleResps,whichResp)
            
            #assume half are authors, therefore when have clicked half, have option to finish
            print('Summing selected, ',selected, ' minMustClick=',minMustClick)
            if sum(selected) >= minMustClick:
                print('drawing OKrespZone')
                OKrespZone.draw()
                OKtextStim.draw()
        myWin.flip()

        #Poll keyboard and mouse
        #Used to use pressed,times = myMouse.getPressed(getTime=True) because it's supposed to return all presses since last call to clickReset. But, doesn't seem to work. So, now loop
        #If getTime=True (False by default) then getPressed will return all buttons that have been pressed since the last call to mouse.clickReset as well as their time stamps:
        pressed,times = myMouse.getPressed(getTime=True)
        while not any(pressed): #wait until pressed
            pressed = myMouse.getPressed() 
        mousePos = myMouse.getPos()
        mousePos = convertXYtoNormUnits(mousePos,myWin.units,myWin)
        #Check what was clicked, if anything
        OK = False
        if any(pressed):
            if state == 'waitingForAnotherSelection':
                OK = False
                print('selected=',selected)
                if sum(selected) >= minMustClick:
                    OK = checkForOKclick(mousePos,OKrespZone)
                if OK:
                    state = 'finished'
            if not OK: #didn't click OK. Check whether clicked near a response array item
                #First calculate the entire array of response regions and see if falls within that
                #calculate top-most box
                x,topmostCoord, topmostW, topmostH =  calcRespYandBoundingBox( possibleResps, 0) #determine bounds of adjacent option
                topmostX = x
                topmostY = topmostCoord
                #calculate bottom-most box
                x,btmmostCoord, btmmostW, btmmostH =  calcRespYandBoundingBox(possibleResps, len(possibleResps)-1)
                btmmostX = x
                btmmostY = btmmostCoord
                w = topmostW
                h = topmostH
                horizBounds = [ x, x+w ] #because words are left-justified, they begin at x
                vertBounds = [btmmostY - h/2, topmostY + h/2]
                print("horizBounds=",horizBounds," vertBounds=",vertBounds)
                xValid = horizBounds[0] <= mousePos[0] <= horizBounds[1]  #clicked in a valid x-position
                yValid = vertBounds[0] <= mousePos[1] <= vertBounds[1]  #clicked in a valid y-position
                if xValid and yValid: #clicked near a response array item
                    relToBtm = mousePos[1] - vertBounds[0] #mouse coordinates go up from -1 to +1
                    relToLeft = mousePos[0] - horizBounds[0]
                    whichResp = int (relToBtm / h)
                    #change from relToBtm to relative to top
                    whichResp = len(possibleResps) - 1- whichResp
                    if (sum(selected) >= maxCanClick)   &   (selected[whichResp]==0): #Clicked on one that is already selected but already hit max allowed
                        badClickSound.play()
                        mustDeselectMsgStim.draw()
                    else:
                        clickSound.play()
                        selected[whichResp] = -1 * selected[whichResp] + 1 #change 0 to 1 and 1 to 0.   Can't use not because can't sum true/false
                        print('Changed selected #',whichResp,', selected=',selected)
                        print("whichResp from top = ",whichResp, " About to redraw")
                        lastValidClickButtons = deepcopy(pressed) #record which buttons pressed. Have to make copy, otherwise will change when pressd changes later
                        print('lastValidClickButtons=',lastValidClickButtons)
                    #state = 'waitingForAnotherSelection' 
                else: 
                    badClickSound.play()
            for key in event.getKeys(): #only checking keyboard if mouse was clicked, hoping to improve performance
                key = key.upper()
                if key in ['ESCAPE']:
                    expStop = True
                    #noResponseYet = False
   
   print('Returning with selected=',selected,' expStop=',expStop)
   return selected, expStop
        
def doLineup(myWin,bgColor,myMouse,clickSound,badClickSound,possibleResps,bothSides,leftRightCentral,autopilot):
    expStop = False
    passThisTrial = False
    minMustClick = 2   #len(possibleResps)[2]
    maxCanClick = 3
    selectedAutopilot = [0]*len(responses)
    if not autopilot: #I haven't bothered to make autopilot display the response screen
        OKrespZone = visual.GratingStim(myWin, tex="sin", mask="gauss", texRes=64, units='norm', size=[.5, .5], sf=[0, 0], name='OKrespZone')
        OKtextStim = visual.TextStim(myWin,pos=(0, 0),colorSpace='rgb',color=(-1,-1,-1),alignHoriz='center', alignVert='center',height=.13,units='norm',autoLog=False)
        OKtextStim.setText('OK')
        instructionStim = visual.TextStim(myWin,pos=(0, .95),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',
                                        height=.06,wrapWidth=3,font='Times',units='norm',autoLog=False)
        instructionStim.setText('Half of these are published authors. Select them with the mouse. When you\'re not sure, guess.')
        instructionStim.draw()

        mustDeselectMsgStim = visual.TextStim(myWin,pos=(0, .5),colorSpace='rgb',color=(0,-.9,-.9),alignHoriz='center', alignVert='center',height=.13,units='norm',autoLog=False)
        mustDeselectMsgStim.setText('You\'ve already selected half. You must deselect an author in order to select another.')
        selected, expStop = \
                collectLineupResponses(myWin,bgColor,myMouse,minMustClick,maxCanClick,instructionStim,OKtextStim,OKrespZone,mustDeselectMsgStim,possibleResps,clickSound,badClickSound)

    return expStop,passThisTrial,selected,selectedAutopilot

def setupSoundsForResponse():
    fileName = '406__tictacshutup__click-1-d.wav'
    try:
        clickSound=sound.Sound(fileName)
    except:
        print('Could not load the desired click sound file, instead using manually created inferior click')
        try:
            clickSound=sound.Sound('D',octave=3, sampleRate=22050, secs=0.015, bits=8)
        except:
            clickSound = None
            print('Could not create a click sound for typing feedback')
    try:
        badKeySound = sound.Sound('A',octave=5, sampleRate=22050, secs=0.08, bits=8)
    except:
        badKeySound = None
        print('Could not create an invalid key sound for typing feedback')
        
    return clickSound, badKeySound

if __name__=='__main__':  #Running this file directly, must want to test functions in this file
    from psychopy import monitors
    monitorname = 'testmonitor'
    mon = monitors.Monitor(monitorname,width=40.5, distance=57)
    windowUnits = 'deg' #purely to make sure lineup array still works when windowUnits are something different from norm units
    bgColor = [-1,-1,-1] 
    myWin = visual.Window(monitor=mon,colorSpace='rgb',color=bgColor,units=windowUnits)
    #myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor

    logging.console.setLevel(logging.WARNING)
    autopilot = False
    clickSound, badClickSound = setupSoundsForResponse()
    alphabet = list(string.ascii_uppercase)
    possibleResps = alphabet
    
    possibleResps = [ 'V.C. Andrews','Lauren Adamson', 'Eric Amsel', 'Carter Anvari', 'Isaac Asimov', 'Margaret Atwood','Russell Banks', 'David Baldacci', 'Carol Berg', 'Pierre Berton', 'Maeve Binchy', 'Judy Blume', 'Dan Brown','Agatha Christie', 'Robertson Davies','Charles Dickens' ]
    realAuthor =  [                   1,                     0,                      1       ]
    #possibleResps.remove('C'); possibleResps.remove('V') #per Goodbourn & Holcombe, including backwards-ltrs experiments
    myWin.flip()
    passThisTrial = False
    myMouse = event.Mouse()

    #Do vertical lineups
    responseDebug=False; responses = list(); responsesAutopilot = list();
    expStop = False
    
    bothSides = True
    leftRightFirst = False
    expStop,passThisTrial,selected,selectedAutopilot = \
                doLineup(myWin, bgColor,myMouse, clickSound, badClickSound, possibleResps, bothSides, leftRightFirst, autopilot)

    print('expStop=',expStop,' passThisTrial=',passThisTrial,' selected=',selected, ' selectedAutopilot =', selectedAutopilot)
    print('Names of selected=',end='')
    for i in xrange(len(selected)):
        if selected[i]:
            print(possibleResps[i],end=',')
    print('')
    print('Finished') 