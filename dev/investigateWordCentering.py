#investigate word centering
from psychopy import visual
from psychopy import event
#fm = textbox.getFontManager()  

myWin=visual.Window(   units='pix'      )

stim1string = "XXX"
stim2string = "XXX"
print('stim1string=',stim1string, 'stim2string=',stim2string)
ltrHeight = 50
wordEccentricity = 60
sans = ['Arial', 'Helvetica', 'Verdana']

textStimulus1 = visual.TextStim(myWin,text=stim1string,font=sans[0], height=ltrHeight,colorSpace='rgb',alignHoriz='center',alignVert='center',units='pix') #deg
textStimulus2 = visual.TextStim(myWin,text=stim2string,font=sans[0],height=ltrHeight,colorSpace='rgb',alignHoriz='center',alignVert='center',units='pix')
textStimulus1.setPos([0,-wordEccentricity]) 
textStimulus2.setPos([0,wordEccentricity]) 

textStimulus3 = visual.TextStim(myWin,text=stim1string,font=sans[0],height=ltrHeight,colorSpace='rgb',alignHoriz='center',alignVert='center',units='pix') #deg
textStimulus4 = visual.TextStim(myWin,text=stim2string,font=sans[0],height=ltrHeight,colorSpace='rgb',alignHoriz='center',alignVert='center',units='pix')
textStimulus3.setPos([2*wordEccentricity,-wordEccentricity]) 
textStimulus4.setPos([2*wordEccentricity,wordEccentricity]) 

fixatnPtSize = 2
fixatnPoint= visual.Circle(myWin,fillColorSpace='rgb',fillColor=(1,1,1),radius=fixatnPtSize,pos=[0,0],units='pix')
ctrPoint= visual.Circle(myWin,fillColorSpace='rgb',fillColor=(1,1,1),radius=fixatnPtSize,pos=[2*wordEccentricity,0],units='pix')


textStimulus1.draw()
textStimulus2.draw() #it's not totally centered. But what is the font?
fixatnPoint.draw()
textStimulus3.draw()
textStimulus4.draw()
ctrPoint.draw()
myWin.flip()
event.waitKeys()