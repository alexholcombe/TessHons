from __future__ import division
from psychopy import visual, event
import numpy as np

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
#mousePos = convertXYtoNormUnits(mousePosRaw,myWin.units,myWin)

#PIS
# Create a window to draw in
#psych labs screen is 1920 x 1080, but my program sets it to 1920 x 1080
subject = 'aholcombe'
fullscr=True 
myWin = visual.Window((1920, 1080), allowGUI=False, winType='pyglet',
            monitor='testMonitor', fullscr=fullscr, units ='norm', screen=0)
myWin.recordFrameIntervals = True

#Display multiple pages side by side
PISp1 = visual.ImageStim(myWin, image='PIS2underlined.png', pos=(-.5,0), units='norm')
PISp2 = visual.ImageStim(myWin, image='PIS2underlined_p2.png', pos=(.5,0), units='norm')
#From the aspect ratio of the images, I should be able to scale their size into norm units that will fit.
PISp1.size=(1,2)
PISp2.size=(1,2)

OKpos = (-.2,-.92)
OKrespZone = visual.GratingStim(myWin, tex="sin", mask="gauss", texRes=256, color=[1,.5,.5], units='norm', size=[2.3, .2], sf=[0, 0], pos=OKpos, name='OKrespZone')
OKtextStim = visual.TextStim(myWin,pos=OKpos,colorSpace='rgb',color=(.5,-1,-1),alignHoriz='center', alignVert='center',height=.07,units='norm',autoLog=False)
OKtextStim.setText('Please read and then CLICK HERE to continue')


myMouse = event.Mouse(win=myWin, visible=True) #, newPos=(-.5,-.5))
myMouse.setPos( (-.5, -.5) ) #Bizarrely, while the documentatoin it says 0,0 is the center and units are the same as the window, I've found that 0,0 is the top right and negative means down and left

clickedContinue = False
secretKeyPressed = False
while not secretKeyPressed and not clickedContinue:
    key = event.getKeys(keyList=['z'], modifiers=True) #secret key is shift ctrl Z
    if key: #z must have been pressed
        modifiers = key[0][1]
        if modifiers['shift'] and modifiers['ctrl']: #secret key is shift-ctrl-Z
            secretKeyPressed = True
    #if key[0][0] == 'z' and key[0][1]['shift'] and key[0][1]['ctrl']:
    PISp1.draw()
    PISp2.draw()
    OKrespZone.draw()
    OKtextStim.draw()
    mousePos = myMouse.getPos()
    #event.clearEvents(); myMouse.clickReset()  #Because sometimes I'd click once on my laptop and it both selected and deselected, as if clicked twice
    #print('myWin.units=',myWin.units,'mousePosRaw=',mousePosRaw,'mousePos=',mousePos)
    pressed, times = myMouse.getPressed(getTime=True)
    if pressed[0] and OKrespZone.contains(mousePos):
        print('Clicked CONTINUE')
        clickedContinue = True
    myWin.flip()

#do Consent form
consentImage = visual.ImageStim(myWin, image='consentForm.png', pos=(0,0), units='norm')
consentImage.size=(1.1,2)
subjectPos = (-.45,.38)
subjectTextStim = visual.TextStim(myWin,pos=subjectPos,colorSpace='rgb',color=(-1,-1,-1),alignHoriz='center', alignVert='center',height=.04,units='norm',autoLog=False,
                                                        text=subject)

choiceTextColor = (-1,-1,-1)
choiceTextSz = .05
checkmarkText = u"\u2713" #checkmark
#For each box, need: pos, respZone, textStim, checkmark status, checkmarkStim. List of dictionaries a good way to do this?
No1pos = np.array( [-.1,-.42] )
No1respZone = visual.GratingStim(myWin, tex="sin", mask="gauss", texRes=256, color=[1,.5,.5], units='norm', size=[.3, .2], sf=[0, 0], pos=No1pos)
No1textStim = visual.TextStim(myWin,pos=No1pos,colorSpace='rgb',color=choiceTextColor,alignHoriz='center', alignVert='center',height=choiceTextSz,units='norm',text='NO',autoLog=False)
No1checkmark = visual.TextStim(myWin,pos=No1pos,colorSpace='rgb',color=choiceTextColor,alignHoriz='right', alignVert='center',height=choiceTextSz*2,units='norm',text=checkmarkText,autoLog=False)
Yes1pos = No1pos + np.array([-.3,0]) #left
Yes1respZone = visual.GratingStim(myWin, tex="sin", mask="gauss", texRes=256, color=[1,.5,.5], units='norm', size=[.3, .2], sf=[0, 0], pos=Yes1pos)
Yes1textStim = visual.TextStim(myWin,pos=Yes1pos,colorSpace='rgb',color=choiceTextColor,alignHoriz='center', alignVert='center',height=choiceTextSz,text='YES',units='norm',autoLog=False)
Yes1checkmark = visual.TextStim(myWin,pos=Yes1pos,colorSpace='rgb',color=choiceTextColor,alignHoriz='center', alignVert='center',height=choiceTextSz*2,text= checkmarkText,units='norm',autoLog=False)
No2pos = No1pos + np.array([0,-.3]) #lower down
No2respZone = visual.GratingStim(myWin, tex="sin", mask="gauss", texRes=256, color=[1,.5,.5], units='norm', size=[.3, .2], sf=[0, 0], pos=No2pos)
No2textStim = visual.TextStim(myWin,pos=No2pos,colorSpace='rgb',color=choiceTextColor,alignHoriz='center', alignVert='center',height=choiceTextSz,units='norm',text='NO',autoLog=False)
Yes2pos = No2pos + np.array([-.3,0])
Yes2respZone = visual.GratingStim(myWin, tex="sin", mask="gauss", texRes=256, color=[1,.5,.5], units='norm', size=[.3, .2], sf=[0, 0], pos=Yes2pos)
Yes2textStim = visual.TextStim(myWin,pos=Yes2pos,colorSpace='rgb',color=choiceTextColor,alignHoriz='center', alignVert='center',height=choiceTextSz,text='YES',units='norm',autoLog=False)

box1Selection = None
box2Selection = None
while not secretKeyPressed and (not box1Selection or not box2Selection):
    key = event.getKeys(keyList=['z'], modifiers=True) #secret key is shift-ctrl-Z
    if key: #z was pressed
        modifiers = key[0][1]
        if modifiers['shift'] and modifiers['ctrl']: #secret key is shift-ctrl-Z
            secretKeyPressed = True
    consentImage.draw()
    subjectTextStim.draw()
    No1respZone.draw()
    No1textStim.draw()
    if box1Selection == "no":
        No1checkmark.draw()
    Yes1respZone.draw()
    Yes1textStim.draw()
    if box1Selection == "yes":
        Yes1checkmark.draw()
    No2respZone.draw()
    No2textStim.draw()
    Yes2respZone.draw()
    Yes2textStim.draw()
    pressed, times = myMouse.getPressed(getTime=True)
    mousePos = myMouse.getPos()
    if pressed[0] and No1respZone.contains(mousePos):
        print('Clicked No1')
        box1Selection = "no"
    if pressed[0] and Yes1respZone.contains(mousePos):
        print('Clicked Yes1')
        box1Selection = "yes"
    if pressed[0] and No2respZone.contains(mousePos):
        print('Clicked No1')
        box2Selection = "no"
    if pressed[0] and Yes2respZone.contains(mousePos):
        print('Clicked Yes1')
        box2Selection = "yes"
    myWin.flip()
    
print('box1Selection=',box1Selection)
print('box2Selection=',box2Selection)


