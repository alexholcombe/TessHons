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

# This alternative uses a gui.Dlg and so you can avoid labeling the cancel button , but can't avoid showing it
# This approach gives more control, eg, text color.
dlg = gui.Dlg(title="PSYC1002 experiment", labelButtonOK=u'         OK         ', labelButtonCancel=u'') # Cancel (decline to answer all)
dlg.addField('The first language you learned to read:', choices=[ 'English','Arabic','Pali','Hebrew','Farsi','Chinese','Korean','Japanese','Other','Decline to answer'])
dlg.addField('Age:', choices = ['17 or under', '18 or 19', '20 or 21', '22, 23, or 24', '24 to 30', '30 to 50', 'over 50','Decline to answer'])
dlg.addField('Which is your dominant hand that you favour for common tasks,\nlike writing, throwing, and brushing your teeth?\n\n', choices=['Left','Right','Neither (able to use both hands equally well)','Decline to answer'])
#dlg.addFixedField(label='', initial='', color='', choices=None, tip='') #Just to create some space
#dlg.addField('Your gender (as listed on birth certificate):', choices=["male", "female"])

thisInfo = dlg.show()  # you have to call show() for a Dlg (automatic with a DlgFromDict)    
if dlg.OK:
    print(thisInfo)
else:
    print('User cancelled, output is ',thisInfo)

    
# create a DlgFromDict
info = {
    'Your gender (as listed on birth certificate)':['male', 'female'],
    'Your age': ['17 or under', '18 or 19', '20 or 21', '22, 23, or 24', '24 to 30', '30 to 50', 'over 50'],
    'Which is your dominant hand that you favour for common tasks,\nlike writing, throwing, and brushing your teeth?':['Left','Right','Neither (able to use both hands equally well'],
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



