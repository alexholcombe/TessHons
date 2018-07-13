from __future__ import division
from psychopy import visual, event

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

consentImage = visual.ImageStim(myWin, image='consentForm.png', pos=(0,0), units='norm')
consentImage.size=(1,2)

OKpos = (-.2,-.92)
OKrespZone = visual.GratingStim(myWin, tex="sin", mask="gauss", texRes=256, color=[1,.5,.5], units='norm', size=[2.3, .2], sf=[0, 0], pos=OKpos, name='OKrespZone')
OKtextStim = visual.TextStim(myWin,pos=OKpos,colorSpace='rgb',color=(.5,-1,-1),alignHoriz='center', alignVert='center',height=.07,units='norm',autoLog=False)
OKtextStim.setText('Please read and then CLICK HERE to continue')

myMouse = event.Mouse(win=myWin, visible=True) #, newPos=(-.5,-.5))
myMouse.setPos( (-.5, -.5) ) #Bizarrely, while the documentatoin it says 0,0 is the center and units are the same as the window, I've found that 0,0 is the top right and negative means down and left

clickedContinue = False
key = None
while not key and not clickedContinue:
    key = event.getKeys(keyList=['z'], modifiers=True)
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

print('key=',key)
consentImage.draw()
myWin.flip()
