from __future__ import print_function
from psychopy import event, sound, logging
from psychopy import visual, event, sound, tools
import numpy as np
import string
from math import floor
from copy import deepcopy

def calcRespYandBoundingBox(possibleResps, horizVert, i):
    spacingCtrToCtr = 2.0 / len(possibleResps)
    charHeight = spacingCtrToCtr
    #coordinate will be interpreted as y if horizVert, x otherwise
    startCoordinate = 1-charHeight/2 #top , to bottom
    if horizVert==0:
        startCoordinate*= -1 #left to right
    increment = i*spacingCtrToCtr
    if horizVert==1:
        increment*=- 1 #go down from top
    coordinate = startCoordinate + increment
    boxWidth = spacingCtrToCtr #0.1
    boxHeight = spacingCtrToCtr
    return coordinate, boxWidth, boxHeight

def drawRespOption(myWin,bgColor,constantCoord,horizVert,color,drawBoundingBox,relativeSize,possibleResps,i):
        #constantCoord is x if horizVert=1 (vertical), y if horizontal
        #relativeSize multiplied by standard size to get desired size
        coord, w, h = calcRespYandBoundingBox( possibleResps, horizVert, i )
        x = constantCoord if horizVert else coord
        y = coord if horizVert else constantCoord
        if relativeSize != 1: #erase bounding box so erase old letter before drawing new differently-sized letter 
            boundingBox = visual.Rect(myWin,width=w,height=h, pos=(x,y), fillColor=bgColor, lineColor=None, units='norm' ,autoLog=False) 
            boundingBox.draw()
        option = visual.TextStim(myWin,colorSpace='rgb',color=color,anchorHoriz='center', anchorVert='center',
                                                                    height=h*relativeSize,units='norm',autoLog=False)
        option.setText(possibleResps[i])
        option.pos = (x, y)
        option.draw()
        if drawBoundingBox:
            boundingBox = visual.Rect(myWin,width=w,height=h, pos=(x,y))
            boundingBox.draw()
        
def drawArray(myWin,bgColor,possibleResps,horizVert,constCoord,lightness,drawBoundingBox):
    '''Draw possibleResps in position x with RGB lightness    
     constCoord is x if horizVert=1 (vertical), y if horizontal
    '''
    #print("lightness in drawArray=",lightness," x=",x)
    #Draw it vertically, from top to bottom
    for i in range(len(possibleResps)):
        drawRespOption(myWin,bgColor,constCoord,horizVert,(lightness,lightness,lightness),drawBoundingBox,1,possibleResps,i)

def drawResponseArrays(myWin,bgColor,horizVert,offsetAmount,possibleResps,bothSides,leftRightCentralBottomTop):
    '''If bothSides, draw array on both sides, with one side dimmed
    If leftRight=0, collect response from left side, and draw other side dim (if bothSides True). Otherwise if =1, from right side.
    possibleResps is usually an array of all the letters to populate the array with.
    offset is offset of center of response array relative to center of screen, in norm units
    '''
    print("leftRightCentralBottomTop=",leftRightCentralBottomTop, "horizVert=",horizVert, "offsetAmount=",offsetAmount)
    numResps = len(possibleResps)
    dimRGB = -.3
    drawBoundingBox = False #to debug to visualise response regions, make True
    if bothSides:
        if leftRightCentralBottomTop == 0:
            lightnessEachSide = (1,dimRGB) #lightness on left and right sides
        elif leftRightCentralBottomTop ==1:
            lightnessEachSide = (dimRGB,1)
        elif leftRightCentralBottomTop ==2:
            print("ERROR: Doesn't make sense to have bothSides=True if want lineup central (leftRightCentralTopBottom")
            quit()
        elif leftRightCentralBottomTop ==3:
            lightnessEachSide = (1,dimRGB)
        elif leftRightCentralBottomTop ==4:
            lightnessEachSide = (dimRGB,1)      
            
        drawArray(myWin,bgColor,possibleResps,horizVert, offsetAmount*-1, lightnessEachSide[0],drawBoundingBox)
        drawArray(myWin,bgColor,possibleResps,horizVert, offsetAmount, lightnessEachSide[1],drawBoundingBox)
        
    else: #only draw one side
        lightness = 1        
        if leftRightCentralBottomTop ==0 or leftRightCentralBottomTop==3:
            offset = -1*offsetAmount
        elif leftRightCentralBottomTop ==1 or leftRightCentralBottomTop==4:
            offset = offsetAmount
        elif leftRightCentralBottomTop==2:
            offset = 0
            
        drawArray(myWin,bgColor,possibleResps,horizVert, offset, lightness,drawBoundingBox)

def checkForOKclick(mousePos,respZone):
    OK = False
    if respZone.contains(mousePos):
            OK = True
    return OK

def convertXYtoNormUnits(XY,currUnits,win):
    factorProbablyToCorrectForMacRetinaScreen = 2
    if currUnits == 'norm':
        return (XY * factorProbablyToCorrectForMacRetinaScreen)
    else:
        widthPix = win.size[0]
        heightPix = win.size[1]
        if currUnits == 'pix':
            xNorm = XY[0]/ (widthPix )   * factorProbablyToCorrectForMacRetinaScreen
            yNorm = XY[1]/ (heightPix )  * factorProbablyToCorrectForMacRetinaScreen
        elif currUnits== 'deg':
            xPix = tools.monitorunittools.deg2pix(XY[0], win.monitor, correctFlat=False)
            yPix = tools.monitorunittools.deg2pix(XY[1], win.monitor, correctFlat=False)
            xNorm = xPix / (widthPix) * factorProbablyToCorrectForMacRetinaScreen
            yNorm = yPix / (heightPix) * factorProbablyToCorrectForMacRetinaScreen
            #print("Converted ",XY," from ",currUnits," units first to pixels: ",xPix,yPix," then to norm: ",xNorm,yNorm)
    return xNorm, yNorm

def collectOneLineupResponse(myWin,bgColor,myMouse,drawBothSides,leftRightCentralBottomTop,OKtextStim,OKrespZone,possibleResps,offset,useSound,
                             clickSound,badClickSound,showClickedRegion,clickedRegion):
   if leftRightCentralBottomTop == 0: #left
        horizVert = 1 #vertical
        constCoord = -1*offset
   elif leftRightCentralBottomTop == 1: #right
        horizVert = 1 #vertical
        constCoord = offset
   elif leftRightCentralBottomTop == 2: #central
        constCoord = 0
        OKrespZone.pos += [0,-.6]
        OKtextStim.pos+= [0,-.6]
        horizVert = 0 #horizontal
   elif leftRightCentralBottomTop == 3: #bottom
        horizVert = 0 #horizontal
        constCoord = -1*offset
   elif leftRightCentralBottomTop == 4: #top
        horizVert = 0 #horizontal
        constCoord = offset    
   else: print("Unexpected leftRightCentralBottomTop value of ",leftRightCentralBottomTop)
   myMouse.clickReset()
   
   showSideIndicator = False
   sideIndicator = visual.Rect(myWin, width=.14,height=.04,ori=90,fillColor=(1,1,1),fillColorSpace='rgb',lineColor=None,units='norm', autoLog=False)
   sideIndicatorCoord = .77*constCoord
   if horizVert:  #not working for vert for some reason
        sideIndicator.setPos(  [0, sideIndicatorCoord] )
        sideIndicator.ori=90
   else: 
        sideIndicator.setPos( [sideIndicatorCoord, 0] )
        sideIndicator.ori=0

   chosenLtr = visual.TextStim(myWin,colorSpace='rgb',color=(1,1,1),anchorHoriz='center', anchorVert='center',height=.4,units='norm',autoLog=False)
   if horizVert: #vertical array
    chosenLtr.setPos( [sideIndicatorCoord,0] )  #big drawing of chosen letter, offset from lineup
   else: #horizontal array
    chosenLtr.setPos( [0,sideIndicatorCoord] )  #big drawing of chosen letter, offset from lineup
   
   whichResp = -1
   state = 'waitingForFirstClick' 
   #waitingForClick means OK is on the screen, so can either click a lineup item, or click OK
   #'finished' exit this lineup, choice has been made
   expStop = False
   while state != 'finished' and not expStop:
        #draw everything corresponding to this state
        drawResponseArrays(myWin,bgColor,horizVert,offset,possibleResps,drawBothSides,leftRightCentralBottomTop)
        if state == 'waitingForClick':
            #draw selected one in green
            selectedColor = (-1,1,-1) #green
            buttonThis = np.where(pressed)[0] #assume only one button can be recorded as pressed
            if buttonThis == 0:
                selectedColor = (1,1,-1) #yellow for low confidence,
            drawRespOption(myWin,bgColor,constCoord,horizVert,selectedColor,False,1.5,possibleResps,whichResp)
            chosenLtr.setText(possibleResps[whichResp])
            chosenLtr.setColor( selectedColor )
            chosenLtr.draw()
            OKrespZone.draw()
            OKtextStim.draw()
        else:
            if showSideIndicator and leftRightCentralBottomTop != 2:
                sideIndicator.draw()
            
        myWin.flip()
        #poll keyboard and mouse

        #Used to use pressed,times = myMouse.getPressed(getTime=True) because it's supposed to return all presses since last call to clickReset. But, doesn't seem to work. So, now block
        #If getTime=True (False by default) then getPressed will return all buttons that have been pressed since the last call to mouse.clickReset as well as their time stamps:
        pressed,times = myMouse.getPressed(getTime=True)
        while not any(pressed): #wait until pressed
            pressed = myMouse.getPressed() 
        mousePosRaw = myMouse.getPos()
        mousePos = convertXYtoNormUnits(mousePosRaw,myWin.units,myWin)
        #Check what was clicked, if anything
        OK = False
        if any(pressed):
            if state == 'waitingForClick':
                OK = checkForOKclick(mousePos,OKrespZone)
                #print('OK=', OK)
                if OK:
                    state = 'finished'
            if not OK: #didn't click OK. Check whether clicked near response array item
                topmostCoord, topmostW, topmostH =  calcRespYandBoundingBox( possibleResps, horizVert, 0) #determine bounds of adjacent option
                topmostX = constCoord if horizVert else topmostCoord
                topmostY = topmostCoord if horizVert else constCoord
                btmmostCoord, btmmostW, btmmostH =  calcRespYandBoundingBox(possibleResps,horizVert, len(possibleResps)-1)
                btmmostX = constCoord if horizVert else btmmostCoord
                btmmostY = btmmostCoord if horizVert else constCoord
                w = topmostW
                h = topmostH
                if horizVert:
                    horizBounds = [ constCoord-w/2, constCoord+w/2 ]
                    vertBounds = [btmmostY - h/2, topmostY + h/2]
                else: #horizontal
                    horizBounds = [topmostX-w/2, btmmostX+w/2,]  #top letter in vertical is first in horizontal
                    vertBounds =  [constCoord-h/2, constCoord+w/2 ]
                #print("horizBounds=",horizBounds," vertBounds=",vertBounds, " constCoord=", constCoord)
                xValid = horizBounds[0] <= mousePos[0] <= horizBounds[1]  #clicked in a valid x-position
                yValid = vertBounds[0] <= mousePos[1] <= vertBounds[1]  #clicked in a valid y-position
                if xValid and yValid:
                        if useSound:
                            clickSound.play(); print('Tried to play clickSound')
                        relToBtm = mousePos[1] - vertBounds[0] #mouse coordinates go up from -1 to +1
                        relToLeft = mousePos[0] - horizBounds[0]
                        if horizVert: #vertical
                            whichResp = int (relToBtm / h)
                            #change from relToBtm to relative to top
                            whichResp = len(possibleResps) - 1- whichResp 
                        else: #horizontal
                            whichResp = int(relToLeft / w)
                            #print("whichResp from left hopefully = ",whichResp, " corresponding to ", possibleResps[whichResp])
                        #print("whichResp from top = ",whichResp, "offsetThis=",offsetThis, " About to redraw and draw one item in red")
                        lastValidClickButtons = deepcopy(pressed) #record which buttons pressed. Have to make copy, otherwise will change when pressd changes later
                        state = 'waitingForClick' 
                else: 
                    if useSound:
                        badClickSound.play(); print('Tried to play badClickSound')
                factorProbablyToCorrectForMacRetinaScreen = 0.5
                clickedRegion.setPos([mousePosRaw[0] * factorProbablyToCorrectForMacRetinaScreen, mousePosRaw[1] * factorProbablyToCorrectForMacRetinaScreen])
                clickedRegion.draw()
                #print('clicked at x,y= ',mousePosRaw[0]*factorProbablyToCorrectForMacRetinaScreen, mousePosRaw[1]*factorProbablyToCorrectForMacRetinaScreen)

            for key in event.getKeys(): #only checking keyboard if mouse was clicked, hoping to improve performance
                key = key.upper()
                if key in ['ESCAPE']:
                    expStop = True
                    #noResponseYet = False
   response = possibleResps[whichResp]
   
   #Determine which button was pressed
   if not ('lastValidClickButtons' in locals()): #variable doesn't exist, which can happen if participant presses ESC
       whichPressed = [-1]
       logging.warning('lastValidClickButtons not defined, maybe because participant pressed ESC')
   else:
       whichPressed = np.where(lastValidClickButtons)[0]
   if len(whichPressed)>1:
        print("Thought it was impossible to have pressed both buttons")
        print('whichPressed=',whichPressed)
   else:
        button = whichPressed[0]
   
   #print('Returning with response=',response,'button=',button,' expStop=',expStop)
   return response, button, expStop
        
def doLineup(myWin,bgColor,myMouse,useSound,clickSound,badClickSound,possibleResps,bothSides,leftRightCentralBottomTop,showClickedRegion,autopilot):
    #leftRightCentralBottomTop is 0 if draw on left side first (or only), 1 if draw right side first (or only), 2 if draw centrally only
    if type(leftRightCentralBottomTop) is str: #convert to 0,1,2,3,4
        if leftRightCentralBottomTop == 'right':
            leftRightCentralBottomTop = 1
        elif leftRightCentralBottomTop == 'left':
            leftRightCentralBottomTop = 0
        elif leftRightCentralBottomTop == 'central':
            leftRightCentralBottomTop = 2
        elif leftRightCentralBottomTop == 'bottom':
            leftRightCentralBottomTop = 3
        elif leftRightCentralBottomTop == 'top':
            leftRightCentralBottomTop = 4
        else:
            print("unrecognized leftRightCentralBottomTop value")
    expStop = False
    passThisTrial = False
    responsesAutopilot = []
    responses = []
    buttons = []
    #First collect one, then dim that one and collect the other
    offset = 0.7
    if autopilot: #I haven't bothered to make autopilot display the response screen
        responsesAutopilot.append('Z')
    else:
        OKrespZone = visual.GratingStim(myWin, tex="sin", mask="gauss", texRes=64, units='norm', size=[.5, .5], sf=[0, 0], name='OKrespZone')
        OKtextStim = visual.TextStim(myWin,pos=(0, 0),colorSpace='rgb',color=(-1,-1,-1),anchorHoriz='center', anchorVert='center',height=.13,units='norm',autoLog=False)
        OKtextStim.setText('OK')
        if showClickedRegion: #Optionally show location of most recent click
            clickedRegion = visual.Circle(myWin, radius=0.5, edges=32, colorSpace='rgb',lineColor=(-1,1,-1),fillColor=(-1,1,-1),autoLog=False) #to show clickable zones
            clickedRegion.setColor((.5,.5,-1)) #show in yellow
   
        whichResp0, whichButtonResp0, expStop = \
                collectOneLineupResponse(myWin,bgColor,myMouse,bothSides,leftRightCentralBottomTop,OKtextStim,OKrespZone,possibleResps,offset,
                                         useSound, clickSound, badClickSound,showClickedRegion,clickedRegion)
        responses.append(whichResp0)
        buttons.append(whichButtonResp0)
    if not expStop and bothSides:
        if autopilot:
            responsesAutopilot.append('Z')
        else:
            #Draw arrays again, with that one dim, to collect the other response
            if leftRightCentralBottomTop == 0:
                lrcbtThis = 1
            elif leftRightCentralBottomTop == 1:
                lrcbtThis = 0
            elif leftRightCentralBottomTop == 3:
                lrcbtThis = 4
            elif leftRightCentralBottomTop == 4:
                lrcbtThis = 3           
            whichResp1, whichButtonResp1, expStop =  \
                collectOneLineupResponse(myWin,bgColor,myMouse,bothSides,lrcbtThis,OKtextStim,OKrespZone,possibleResps,offset,
                                         useSound, clickSound, badClickSound,showClickedRegion,clickedRegion)
            responses.append(whichResp1)
            buttons.append(whichButtonResp0)
    return expStop,passThisTrial,responses,buttons,responsesAutopilot

def setupSoundsForResponse():
    print('Using %s (with %s) for sounds' % (sound.audioLib, sound.audioDriver))
    fileName = 'click.wav' #'406__tictacshutup__click-1-d.wav'
    try:
        clickSound=sound.Sound(fileName, secs=0.2)
    except:
        print('Could not load the desired click sound file, instead using manually created inferior click')
        try:
            clickSound=sound.Sound('D',octave=3, sampleRate=22050, secs=0.015, bits=8)
        except:
            clickSound = None
            print('Could not create a click sound for typing feedback')

    try:
    	badSound = sound.Sound('bad.wav')
        #badSound = sound.Sound('A', secs=0.02, stereo=True, hamming=True)
        #badSound.setVolume(1.0)
        #badKeySound = sound.Sound('A',octave=5, sampleRate=22050, secs=0.08, bits=8)
    except:
        badSound = None
        print('Could not create an invalid key sound for typing feedback')
    print('cdreated bad sound')

    return clickSound, badSound

if __name__=='__main__':  #Running this file directly, must want to test functions in this file
    from psychopy import monitors
    monitorname = 'testmonitor'
    mon = monitors.Monitor(monitorname,width=40.5, distance=57)
    windowUnits = 'deg' #purely to make sure lineup array still works when windowUnits are something different from norm units
    bgColor = [-.7,-.7,-.7] 
    myWin = visual.Window(monitor=mon,colorSpace='rgb',color=bgColor,units=windowUnits)
    #myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor

    logging.console.setLevel(logging.WARNING)
    autopilot = False
    showClickedRegion = True
    useSound = False
    
    clickSound = None; badClickSound = None;
    if useSound:
        clickSound, badClickSound = setupSoundsForResponse()
    alphabet = list(string.ascii_uppercase)
    possibleResps = alphabet
    #possibleResps.remove('C'); possibleResps.remove('V') #per Goodbourn & Holcombe, including backwards-ltrs experiments
    myWin.flip()
    passThisTrial = False
    myMouse = event.Mouse()

    if autopilot:
        print("autopilot TRUE so you WON'T SEE ANYTHING=") 

    #Do horiz top and bottom lineups
    responseDebug=False; responses = list(); responsesAutopilot = list();
    expStop = False
    bothSides = True
    leftRightCentralBottomTop = 4 #top first
    print('clickSound before second lineup =',clickSound)
    print('badSound before second lineup =',badClickSound)
    expStop,passThisTrial,responses,buttons,responsesAutopilot = \
        doLineup(myWin, bgColor,myMouse, useSound, clickSound, badClickSound, possibleResps, bothSides, leftRightCentralBottomTop, showClickedRegion, autopilot)

    print('autopilot=',autopilot, 'responses=',responses)
    print('expStop=',expStop,' passThisTrial=',passThisTrial,' responses=',responses, ' responsesAutopilot =', responsesAutopilot)

    #Do horiz top lineup only
    responseDebug=False; responses = list(); responsesAutopilot = list();
    expStop = False
    bothSides = False
    leftRightCentralBottomTop = 4 #top
    print('clickSound before second lineup =',clickSound)
    print('badSound before second lineup =',badClickSound)
    expStop,passThisTrial,responses,buttons,responsesAutopilot = \
        doLineup(myWin, bgColor,myMouse, useSound, clickSound, badClickSound, possibleResps, bothSides, leftRightCentralBottomTop, showClickedRegion, autopilot)

    print('autopilot=',autopilot, 'responses=',responses)
    print('expStop=',expStop,' passThisTrial=',passThisTrial,' responses=',responses, ' responsesAutopilot =', responsesAutopilot)

    #Do central horizontal lineup
    responseDebug=False; responses = list(); responsesAutopilot = list();
    expStop = False
    bothSides = False
    leftRightCentralBottomTop = 2 #central
    expStop,passThisTrial,responses,buttons,responsesAutopilot = \
        doLineup(myWin, bgColor, myMouse, useSound, clickSound, badClickSound, possibleResps, bothSides, leftRightCentralBottomTop, showClickedRegion, autopilot)
    
    print('responses=',responses)
    print('expStop=',expStop,' passThisTrial=',passThisTrial,' responses=',responses, ' responsesAutopilot =', responsesAutopilot)
    
    #Do vertical lineups
    responseDebug=False; responses = list(); responsesAutopilot = list();
    expStop = False
    bothSides = True
    leftRightCentralBottomTop = 0 #left first
    print('clickSound before second lineup =',clickSound)
    print('badSound before second lineup =',badClickSound)
    expStop,passThisTrial,responses,buttons,responsesAutopilot = \
        doLineup(myWin, bgColor,myMouse, useSound, clickSound, badClickSound, possibleResps, bothSides, leftRightCentralBottomTop, showClickedRegion, autopilot)

    print('autopilot=',autopilot, 'responses=',responses)
    print('expStop=',expStop,' passThisTrial=',passThisTrial,' responses=',responses, ' responsesAutopilot =', responsesAutopilot)
    
    
    print('Finished') 
