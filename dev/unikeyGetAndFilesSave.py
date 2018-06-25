from __future__ import absolute_import, division, print_function
from psychopy import gui  #fetch default gui handler (qt if available)
## you can explicitly choose one of the qt/wx backends like this:
## from psychopy.gui import wxgui as gui
## from psychopy.gui import qtgui as gui
import subprocess
import time
subject = subprocess.check_output('whoami')
print('subject ="',subject,'"', sep='') #for some reason it has a lot of padding spaces and a newline
subject = subject.strip()
print('subject stripped down="',subject,'"', sep='') #for some reason it has a lot of padding spaces and a newline
#Check whether the 'submission' folder is availble.
#How do I get the current directory?
import os
currDir = os.getcwd()
dataDir = 'Submission'
#Check whether path exists
if os.path.isdir('.'+os.sep+dataDir):
    print('Great,',dataDir,' directory exists')
else:
    print(dataDir,' directory does not exist, therefore not saving data ')
    dataDir='.'

print(os.path.isdir(dataDir))

timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime())
fileName = os.path.join(dataDir, subject + '_' + timeAndDateStr)
print('fileName=',fileName)