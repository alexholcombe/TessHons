#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Demo to illustrate Dialog (Dlg) classes and usage.
"""
from __future__ import absolute_import, division, print_function
from psychopy import gui  #fetch default gui handler (qt if available)
## you can explicitly choose one of the qt/wx backends like this:
## from psychopy.gui import wxgui as gui
## from psychopy.gui import qtgui as gui

# create a DlgFromDict
info = {'Observer':'unikey', 
    'gender':['male', 'female', 'neither'],
    'Your age': ['17 or under', '18 or 19', '20 or 21', '22, 23, or 24', '24 to 30', '30 to 50', 'over 50'],
    'Which is your dominant hand, i.e. which\nhand do you favour for common tasks like\nwriting, throwing, and brushing your teeth?':['Left','Right','Neither (able to use both hands equally well'],
    'The first language you learned to read':[ 'English','Arabic','Pali','Hebrew','Farsi','Chinese','Korean','Japanese','Other'],
    'Did you take this seriously - \n(would you use the data, if you did this research?)':
        ['No','Definitely not','Not really','Yes','Nope']
    }
infoDlg = gui.DlgFromDict(dictionary=info, title='TestExperiment',
    order=['The first language you learned to read', 'Your age'],
    #tip={'Your ag': 'trained visual observer, initials'},
    )
if infoDlg.OK:  # this will be True (user hit OK) or False (cancelled)
    print(info)
else:
    print('User Cancelled')
    core.quit()

# This alternative uses a gui.Dlg and you manually extract the data.
# This approach gives more control, eg, text color.
dlg = gui.Dlg(title="My experiment", pos=(200, 400))
dlg.addText('Subject Info', color='Blue')
dlg.addField('Name:', tip='or subject code')
dlg.addField('Age:', 21)
dlg.addText('Experiment Info', color='Blue')
dlg.addField('', 45)

thisInfo = dlg.show()  # you have to call show() for a Dlg (automatic with a DlgFromDict)    
if dlg.OK:
    print(thisInfo)
else:
    print('User cancelled')

# The contents of this file are in the public domain.
