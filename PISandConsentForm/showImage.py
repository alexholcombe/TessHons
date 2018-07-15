from __future__ import division
from __future__ import print_function
from psychopy import core, visual, event

# Create a window to draw in
win = visual.Window((800, 800), monitor='testMonitor', units='norm', allowGUI=True, color='black')

# Initialize some stimuli
beach = visual.ImageStim(win, image='PIS2underlined.png',  units='norm')

while not event.getKeys():
    beach.draw()
    win.flip()