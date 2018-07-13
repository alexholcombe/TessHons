from __future__ import division

from psychopy import visual, event
#PIS
# Create a window to draw in
win = visual.Window((800.0, 800.0), allowGUI=False, winType='pyglet',
            monitor='testMonitor', units ='deg', screen=0)
win.recordFrameIntervals = True

longSentence = visual.TextStim(win,
    text = u"(1)	What is this study about?

In this class activity, you will identify letters, words and/or numbers that appear rapidly on the screen. If you consent to our using your data, our data analysis will aim to improve the understanding of cognitive processes underlying visual processing of letters, words, and numbers.

(2)	Who is running the study?

	The study is being conducted by Professor Alex Holcombe, Ms Kimbra Ransley, 
	Mr Charles Ludowici, and Mr Christopher Bush.

(3)	What will the study involve for me?

The class activity will involve making simple judgments about stimuli presented on a computer screen. For example, you might be asked to identify a letter or indicate whether a visual stimulus appeared on the left or the right of the screen. Responses will be made using a computer mouse or keyboard. Additionally, you may be asked some basic questions about your age, sex, handedness, and reading/language experience. If you do not wish to answer any of these questions you may decline to do so without consequence.

(4)	How much of my time will the study take?

The study is expected to take no more than 20 minutes in total. You may take a break at any time if you feel tired.
", 
    wrapWidth=0.4,
    units='norm', height=0.05, color='DarkSlateBlue',
    pos=[0, 0], alignHoriz='right', alignVert='bottom')

while not event.getKeys():
    longSentence.draw()
    win.flip()

win.close()
