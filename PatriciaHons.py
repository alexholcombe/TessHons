#Alex Holcombe alex.holcombe@sydney.edu.au
#See the github repository for more information: https://github.com/alexholcombe/
from psychopy import monitors, visual, event, data, logging, core, gui, sound
import psychopy.info
useSound = True
import random
import numpy as np
from math import atan, log, ceil
import copy, time, datetime, sys, os, string, shutil, platform
#try:
#    from noiseStaircaseHeapers import printStaircase, toStaircase, outOfStaircase, createNoise, plotDataAndPsychometricCurve
#except ImportError:
#    print('Could not import from noiseStaircaseHelpers.py (you need that file to be in the same directory)')
try:
    import pylink  
    from eyetrackingCode import EyeLinkCoreGraphicsPsychoPyAlex #imports from subfolder
except Exception as e:
    print("An exception occurred: {str(e)}")
    print('Could not import EyeLinkCoreGraphicsPsychoPyAlex.py (you need that file to be in the eyetrackingCode subdirectory, which needs an __init__.py file in it too)')
try:
    import stringResponse
except ImportError:
    print('Could not import stringResponse.py (you need that file to be in the same directory)')
try:
    import letterLineupResponse
except ImportError:
    print('Could not import letterLineupResponse.py (you need that file to be in the same directory)')
showClickedRegion= True

try:
    from authorRecognitionLineup import doAuthorLineup
except ImportError:
    print('Could not import authorRecognitionLineup.py (you need that file to be in the same directory)')

topDir = '.'
sys.path.append( os.path.join(topDir,'PISandConsentForm') )   #because current working directory ends up being the PSYC1002 grasp folder, NOT the folder with PSYC1002.py in it
try:
    from PISandConsentForm import doParticipantInformationStatement, doConsentForm
except ImportError:
    print('Could not import PISandConsentForm.py (you need that file to be in the same directory)')
try:
    from getpass import getuser
    from socket import gethostname
except ImportError:
    print('ERROR Could not import getpass')

pointsEachCond = [ [3,3], [1,5] ]

#Change the following number to match the participant's condition
condNum = 0
    
trackEyes = False
if trackEyes:
    eyetracker_dummy_mode = False # Set this variable to True to run eyetracking in "Dummy Mode"
    eyetrackFileGetFromEyelinkMachine = True
    timeAndDateStr = time.strftime("%H%M_%d%b%Y", time.localtime())
    subject = 'subjectNameUnknownSetLater'
    #edf_fname= 'results' #EyeTrack_'+subject+'_'+timeAndDateStr+'.EDF'  #Too long, on eyetracker PC, filename is limited to 8 chars!!
    edf_fname_short = timeAndDateStr[0:8] #tesschange from timeAndDateStr[0:8] #+ '.EDF' #on eyetracker PC, filename is limited to 8 chars!!
    print('Eyetracking file will be called',edf_fname_short)
    # Step 1: Connect to the EyeLink Host PC
    # The Host IP address, by default, is "100.1.1.1".
    # the "el_tracker" objected created here can be accessed through the Pylink
    # Set the Host PC address to "None" (without quotes) to run the script
    # in "Dummy Mode"
    if eyetracker_dummy_mode:
        el_tracker = pylink.EyeLink(None)
    else:
        try:
            el_tracker = pylink.EyeLink("100.1.1.1")
        except RuntimeError as error:
            print('ERROR:', error)
            core.quit()
            sys.exit()
    
    # Step 2: Open an EDF data file on the EyeLink PC
    try:
        el_tracker.openDataFile(edf_fname_short)
    except RuntimeError as err:
        print('ERROR:', err)
        # close the link if we have one open
        if el_tracker.isConnected():
            el_tracker.close()
        core.quit()
        sys.exit()
        
    # We download EDF data file from the EyeLink Host PC to the local hard drive at the end of each testing session

    # Add a header text to the EDF file to identify the current experiment name
    # This is optional. If your text starts with "RECORDED BY " it will be
    # available in DataViewer's Inspector window by clicking
    # the EDF session node in the top panel and looking for the "Recorded By:"
    # field in the bottom panel of the Inspector.
    preamble_text = 'RECORDED BY %s' % os.path.basename(__file__)
    el_tracker.sendCommand("add_file_preamble_text '%s'" % preamble_text)
    
    # Step 3: Configure the tracker
    #
    # Put the tracker in offline mode before we change tracking parameters
    el_tracker.setOfflineMode()

    # Get the software version:  1-EyeLink I, 2-EyeLink II, 3/4-EyeLink 1000,
    # 5-EyeLink 1000 Plus, 6-Portable DUO
    eyelink_ver = 0  # set version to 0, in case running in Dummy mode
    if not eyetracker_dummy_mode:
        vstr = el_tracker.getTrackerVersionString()
        eyelink_ver = int(vstr.split()[-1].split('.')[0])
        # print out some version info in the shell
        print('Running experiment on %s, version %d' % (vstr, eyelink_ver))
    
    # File and Link data control
    # what eye events to save in the EDF file, include everything by default
    file_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
    # what eye events to make available over the link, include everything by default
    link_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'
    # what sample data to save in the EDF data file and to make available
    # over the link, include the 'HTARGET' flag to save head target sticker
    # data for supported eye trackers
    if eyelink_ver > 3:
        file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,HTARGET,GAZERES,BUTTON,STATUS,INPUT'
        link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,HTARGET,STATUS,INPUT'
    else:
        file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,GAZERES,BUTTON,STATUS,INPUT'
        link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT'
    el_tracker.sendCommand("file_event_filter = %s" % file_event_flags)
    el_tracker.sendCommand("file_sample_data = %s" % file_sample_flags)
    el_tracker.sendCommand("link_event_filter = %s" % link_event_flags)
    el_tracker.sendCommand("link_sample_data = %s" % link_sample_flags)
    
    # Optional tracking parameters
    # Sample rate, 250, 500, 1000, or 2000, check your tracker specification
    # if eyelink_ver > 2:
    #     el_tracker.sendCommand("sample_rate 1000")
    # Choose a calibration type, H3, HV3, HV5, HV13 (HV = horizontal/vertical),
    el_tracker.sendCommand("calibration_type = HV9")
    # Set a gamepad button to accept calibration/drift check target
    # You need a supported gamepad/button box that is connected to the Host PC
    el_tracker.sendCommand("button_function 5 'accept_target_fixation'")

wordEccentricity= 3 #tesschange from 0.9
tasks=['T1']; task = tasks[0]
#same screen or external screen? Set scrn=0 if one screen. scrn=1 means display stimulus on second screen.
#widthPix, heightPix
quitFinder=False 
autopilot= False  #tesschange temp
demo=False #False
exportImages= False #quits after one trial
user=getuser()  #In PSYC1002, participant logged into computer so subject was their username https://stackoverflow.com/a/842096/302378
networkMachineName = gethostname()
subject = '38_prac' #for pat: change before practice trial & for each part of the experiment (e.g., exp1 or exp2)
if autopilot: subject='auto'
cwd = os.getcwd()
print('current working directory =',cwd)
if sys.platform == "win32":
    pathToData = 'dataRaw'  
else:
    pathToData = 'dataRaw'
if os.path.isdir(pathToData):
    dataDir='dataRaw'
else:
    print('"dataRaw" directory does not exist, so trying to save to a directory called abgdj')
    dataDir='abgdj'
    if not os.path.isdir(dataDir):
        print("Error, no ",dataDir," directory")
        core.quit()
timeDateStart = time.strftime("%d%b%Y_%H-%M-%S", time.localtime()) #used for filename
now = datetime.datetime.now() #used for JSON

showRefreshMisses=True #flicker fixation at refresh rate, to visualize if frames missed
feedback=True 
autoLogging=False
refreshRate = 85
if demo:
   refreshRate = 85.;  #100

numWordsInStream = 1
myFont =  'Arial' # 'Sloan' # 

#Set up the list of experiments, then allocate one to the subject
experimentTypesStim = ['letter']  #'digit']
experimentTypesSpatial = ['horiz','vert']
#experimentTypesNumletters
#create dictionary of all combinations
experimentsList = []
#Creating the list of experiments
#Implement the fully factorial part of the design by creating every combination of the following conditions
oneTargetConditions = [False] #[False,False,True] #1/3 of trials single-target
for stim in experimentTypesStim:
    ISIms = 100 # 100 for Pat #51 for Tess
    for spatial in experimentTypesSpatial:
        experimentsList.append( {'numSimultaneousStim': 2, 'stimType':stim, 'flipped':False, 'spatial':spatial, 'ori':0, 'ISIms':ISIms, 'oneTargetConditions':oneTargetConditions} )
#add Patricia's experiment to list, making it number 2
experimentsList.append( {'numSimultaneousStim': 2, 'stimType':'letter', 'flipped':False, 'spatial':'horiz', 'ori':0, 'ISIms':ISIms, 'oneTargetConditions':oneTargetConditions } )

seed = int( np.floor( time.time() ) )
random.seed(seed); np.random.seed(seed) #https://stackoverflow.com/a/48056075/302378
import json
otherData= {} #stuff to record in authors data file
otherData.update( {'user': user} )
otherData.update( {'networkMachineName': networkMachineName} )
otherData.update( {'datetime':now.isoformat()} )
otherData.update( {'seed':seed} )

#Allocate experiment to subject
experimentNum = 2 #abs(  hash(subject)   ) % len(experimentsList)   #https://stackoverflow.com/a/16008760/302378
experiment = experimentsList[ experimentNum ]
print('Experiment characteristics=',experiment)
otherData.update(experiment)

#Determine stimuli for this participant
if experiment['stimType'] == 'trigram': #For Tess' experiment
    ltrList =  list(string.ascii_lowercase)
    toRemove = []#['d','b','l','i','o','q','p','v','w','x'] #because symmetrical, see rotatedLettersAndSymbols.jpg 
    for ltr in toRemove:
        ltrList.remove(ltr)
    
    stimList = list()
    for i in ltrList: #[0:1]:
        for j in ltrList: #[0:5]:
            for k in ltrList: #[0:10]:
                if i != j and i != k and j != k:
                    trigram = i + j + k
                    stimList.append(trigram)
    #Each participant will get a different random subset, so permute and truncate
    random.shuffle(stimList) 
    #How many stimuli do we need?
    stimList = stimList[0:500]
if experiment['stimType'] == 'letter':
    stimList =  list(string.ascii_lowercase)
    toRemove = ['d','b','l','i','o','q','p','v','w','x'] #because symmetrical, see rotatedLettersAndSymbols.jpg 
    for ltr in toRemove:
        stimList.remove(ltr)
elif experiment['stimType'] == 'digit':
    stimList = ['0','1','2','3','4','5','6','7','8','9']

print('stimlist=',stimList)
bgColor = [-.7,-.7,-.7] # [-1,-1,-1]
cueColor = [-.7,-.7,-.7] #originally [1.,1.,1.]
ltrColor = .9 # .9 for Pat #[.9,.9,.9]# [-.3,-.3,-.3] 
cueRadius = 7 #6 deg in Goodbourn & Holcombe
#1920 x 1080 for psyc lab OTC machines
widthPix= 1920 #monitor width in pixels of Agosta  [1280]
heightPix= 1080 #800 #monitor height in pixels [800]
monitorwidth = 57 #38.7 #monitor width in cm [was 38.7]
scrn=0 #1 to use main screen, 1 to use external screen connected to computer
fullscr=True #True to use fullscreen, False to not. Timing probably won't be quite right if fullscreen = False
allowGUI = False
if demo: monitorwidth = 23#18.0
if exportImages:
    widthPix = 600; heightPix = 600
    monitorwidth = 13.0
    fullscr=False; scrn=1
    framesSaved=0
if demo:    
    scrn=1; fullscr=False
    widthPix = 800; heightPix = 600
    monitorname='testMonitor'
    allowGUI = True
viewdist = 57 #50. #cm
pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) /np.pi*180)
    
doStaircase = True
stopStaircaseAfterFirstBlock = False #If your experiment uses staircasing (doStaircase=True), only do it for the first block (which will be practice trials) because otherwise
    #different conditions might have different average duration/luminances, because the staircase adjusts after potentially every trial
checkRefreshEtc = True 
if quitFinder and sys.platform != "win32":  #Don't know how to quitfinder on windows
    import os
    applescript="\'tell application \"Finder\" to quit\'"
    shellCmd = 'osascript -e '+applescript
    os.system(shellCmd)
    
letterDurMs = 34
ISIms = experiment['ISIms'] #multiply the last value for ISIframes with 11.76 to get the value for ISIms AFTER the break
letterDurFrames = int( np.floor(letterDurMs / (1000./refreshRate)) )
cueDurFrames = letterDurFrames
ISIframes = int( np.floor(ISIms / (1000./refreshRate)) )
#have set ISIframes and letterDurFrames to integer that corresponds as close as possible to originally intended ms
rateInfo = 'base total SOA=' + str(round(  (ISIframes + letterDurFrames)*1000./refreshRate, 2)) + ' or ' + str(ISIframes + letterDurFrames) + ' frames, comprising\n'
rateInfo+=  'base ISIframes ='+str(ISIframes)+' or '+str(ISIframes*(1000./refreshRate))+' ms and letterDurFrames ='+str(letterDurFrames)+' or '+str(round( letterDurFrames*(1000./refreshRate), 2))+'ms'
#rateInfo logged down below after set up logfile

monitorname = 'testmonitor'
waitBlank = False
mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#relying on  monitorwidth cm (39 for Mitsubishi to do deg calculations) and gamma info in calibratn
mon.setSizePix( (widthPix,heightPix) )
units='deg' #'cm'

trialsPerCondition = 200 #tesschange from 23, patriciachange from Tess's 17
defaultNoiseLevel = 0
if not demo:
    allowGUI = False

#set up output data file, log file,  copy of program code, and logging
infix = ''
fileName = os.path.join(dataDir, subject + '_' + infix+ timeDateStart)
if not demo and not exportImages:
    dataFile = open(fileName+'.txt', 'w')
    #save copy of this script so no mistaking the version of the code run by this subject
    #saveCodeCmd = 'cp \'' + sys.argv[0] + '\' '+ fileName + '.py'    #only works on OSX
    #os.system(saveCodeCmd)  #save a copy of the code as it was when that subject was run   #only works on OSX
    thisScriptName = sys.argv[0]
    scriptDestination = os.path.join(fileName + '.py')
    #print('thisScriptName=', thisScriptName, 'scriptDestination=',scriptDestination)
    shutil.copyfile(thisScriptName, scriptDestination)
    logFname = fileName+'.log'
    ppLogF = logging.LogFile(logFname, 
        filemode='w',#if you set this to 'a' it will append instead of overwriting
        level=logging.INFO)#errors, data and warnings will be sent to this logfile
if demo or exportImages: 
  dataFile = sys.stdout; logFname = sys.stdout
  logging.console.setLevel(logging.ERROR)  #only show this level  messages and higher
logging.console.setLevel(logging.ERROR) #DEBUG means set  console to receive nearly all messges, INFO next level, EXP, DATA, WARNING and ERROR 
logging.info(rateInfo); #print(rateInfo)
logging.info('current working directory is ' + cwd)

includeConsentDemographics = False
if includeConsentDemographics:
        requirePassword = False
        if requirePassword:
            succeeded = False
            attempts = 0
            while attempts < 3 and not succeeded:
                    info = {'\n\n\n\nPassword\n\n\n':'', '':''}
                    infoDlg = gui.DlgFromDict(dictionary=info, title='Research Report Experiment',
                        tip={'\n\n\n\n\nPassword\n\n\n': 'Famous psychologist'}, 
                        fixed=['']
                    )
                    word = ''
                    if infoDlg.OK:  # this will be True (user hit OK) or False (cancelled)
                        word = info['\n\n\n\nPassword\n\n\n']
                        word = word.upper()
                        if word == 'LOFTUS':
                            succeeded = True
                        else:
                            print('Password incorrect.')
                    else:
                        print('User cancelled')
                        core.quit()
                    attempts += 1
            if not succeeded:
                core.quit()
        
def openMyStimWindow(): #make it a function because if do it multiple times, want to be sure is identical each time
    myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor
    return myWin
myWin = openMyStimWindow()
myMouse = None
if includeConsentDemographics:
    myMouse = event.Mouse(visible=True) #the mouse absolutely needs to be reset, it seems, otherwise maybe it returns coordinates in wrong units or with wrong scaling?
    dir = os.path.join(topDir,'PISandConsentForm')
    page1 = os.path.join(dir,'PIS2underlined.png') #"PISandConsentForm/PIS2underlined.png" 
    page2 = os.path.join(dir,'PIS2underlined_p2.png')  #  PISandConsentForm/PIS2underlined_p2.png   
    page3 = os.path.join(dir,'PIS2underlined_p3.png')  #  PISandConsentForm/PIS2underlined_p3.png  
    page4 = os.path.join(dir,'PIS2underlined_p4.png')  #  PISandConsentForm/PIS2underlined_p4.png    tesschange
    clickedContinue = doParticipantInformationStatement(page1,page2, myWin, myMouse, exportImages)
    clickedContinue = doParticipantInformationStatement(page3,page4, myWin, myMouse, exportImages)

    page = os.path.join(dir,'consentForm.png') #"PISandConsentForm/'consentForm.png'
    secretKeyPressed, choiceDicts = doConsentForm(page, subject, myWin, myMouse, exportImages)
    for c in choiceDicts:
        print(c['name']," ['checked']=",c['checked'])
        otherData.update(  {   (c['name'],  c['checked'])    } )#add to json data file
    if secretKeyPressed:
        core.quit()

myWin.close() #have to close window to show pop-up to display dlg

# Collect demographic variables
# Use a gui.Dlg and so you can avoid labeling the cancel button , but can't avoid showing it
# This approach gives more control, eg, text color.
questions = ['What is your age?', 'Which of the following best describes your gender?', 'What is the first language you learned to read?', 'Are you fluent in English?']
dlg = gui.Dlg(title="PatHons", labelButtonOK=u'         OK         ', labelButtonCancel=u'', pos=(200, 400)) # Cancel (decline to answer all)
dlg.addField(questions[0])
dlg.addField(questions[1], choices=[ 'Man','Woman','Trans and/or gender diverse','I use a different term','Decline to answer'])
dlg.addField(questions[2], choices=[ 'English','Arabic','Pali','Hebrew','Farsi','Chinese','Korean','Japanese','Other','Decline to answer'])
dlg.addField(questions[3], choices=[ 'Yes','No','Decline to answer'])
thisInfo = dlg.show()  # you have to call show() for a Dlg (automatic with a DlgFromDict)
    
demographics = {q: 'Decline to answer (pressed unlabeled cancel button)' for q in questions}  #Assume pressed cancel unless get values
if dlg.OK:
    print(thisInfo)
    demographics = dict([ (questions[0], thisInfo[0]), (questions[1], thisInfo[1]), (questions[2], thisInfo[2]), (questions[3], thisInfo[3])])
otherData.update(demographics)
#end demographics collection 

auxiliaryDataFileName = os.path.join(dataDir, subject + '_' + timeDateStart + 'auxiliaryData' + '.json')
with open(auxiliaryDataFileName, 'w') as outfile:  
        json.dump(otherData, outfile)

myWin = openMyStimWindow()

if fullscr and not demo and not exportImages:
    runInfo = psychopy.info.RunTimeInfo(
        win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
        refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
        verbose=True, ## True means report on everything 
        userProcsDetailed=True,  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
        )
    #print('runInfo='); print(runInfo)
    logging.info(runInfo)
    print('Finished runInfo- which assesses the refresh and processes of this computer') 

if checkRefreshEtc and (not demo) and (myWin.size != [widthPix,heightPix]).any():
    msgWrongResolution = 'Screen apparently NOT the desired resolution of '+ str(widthPix)+'x'+str(heightPix)+ ' pixels!!'
    logging.error(msgWrongResolution)
    print(msgWrongResolution)

if checkRefreshEtc and (not demo):
    #check screen refresh is what assuming it is ##############################################
    Hzs=list()
    myWin.flip(); myWin.flip();myWin.flip()
    myWin.setRecordFrameIntervals(True) #otherwise myWin.fps won't work
    print('About to measure frame flips') 
    for i in range(50):
        myWin.flip()
        Hzs.append( myWin.fps() )  #varies wildly on successive runs!
    myWin.setRecordFrameIntervals(False)
    # end testing of screen refresh########################################################
    Hzs = np.array( Hzs );     Hz= np.median(Hzs)
    msPerFrame= 1000./Hz
    refreshMsg1= 'Frames per second ~='+ str( np.round(Hz,1) )
    refreshMsg2 = ''
    refreshRateTolerancePct = 3
    pctOff = abs( (np.median(Hzs)-refreshRate) / refreshRate)
    refreshRateWrong =  pctOff > (refreshRateTolerancePct/100.)
    if refreshRateWrong:
        refreshMsg1 += ' BUT'
        refreshMsg1 += ' program assumes ' + str(refreshRate)
        refreshMsg2 =  'which is off by more than' + str(round(refreshRateTolerancePct,0)) + '%!!'
    else:
        refreshMsg1 += ', which is close enough to desired val of ' + str( round(refreshRate,1) )
    if refreshRateWrong:
        logging.error(refreshMsg1+refreshMsg2)
    else: logging.info(refreshMsg1+refreshMsg2)
logging.flush()

def closeEyeTracker(tracker):
    #Clean everything up, save data and close connection to tracker
    if tracker != None:
        # File transfer and cleanup!
        tracker.setOfflineMode();
        core.wait(0.5)

        tracker.close();
        #Close the experiment graphics
        pylink.closeGraphics()
        return "Eyelink connection closed."
    else:
        return "Tried to close eyetracker but Eyelink not available"

def stopEyeTracking(tracker):
    #Stop recording: adds 100 msec of data to catch final events
    pylink.endRealTimeMode()
    pylink.pumpDelay(100)
    tracker.stopRecording()

if trackEyes:
    # get the native screen resolution used by PsychoPy
    scn_width, scn_height = myWin.size
    # Set this variable to True if you use the built-in retina screen as your
    # primary display device on macOS. If have an external monitor, set this
    # variable True if you choose to "Optimize for Built-in Retina Display"
    # in the Displays preference settings.
    use_retina = False
    # resolution fix for Mac retina displays
    if 'Darwin' in platform.system():
        if use_retina:
            scn_width = int(scn_width/2.0)
            scn_height = int(scn_height/2.0)

    # Pass the display pixel coordinates (left, top, right, bottom) to the tracker
    # see the EyeLink Installation Guide, "Customizing Screen Settings"
    el_coords = "screen_pixel_coords = 0 0 %d %d" % (scn_width - 1, scn_height - 1)
    logging.info("screen coords being sent to eyetrakcer = " + el_coords); #print(rateInfo)
    print("myWin screen_pixel_coords being sent to eyetracker =",el_coords)
    el_tracker.sendCommand(el_coords)

    # Write a DISPLAY_COORDS message to the EDF file
    # Data Viewer needs this piece of info for proper visualization, see Data
    # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
    dv_coords = "DISPLAY_COORDS  0 0 %d %d" % (scn_width - 1, scn_height - 1)
    el_tracker.sendMessage(dv_coords)
    
    # Configure a graphics environment (genv) for tracker calibration
    genv = EyeLinkCoreGraphicsPsychoPyAlex.EyeLinkCoreGraphicsPsychoPy(el_tracker, myWin)
    print(genv)  #It's a class with a print method so this prints out the info including version number of the CoreGraphics library
    
    # Set background and foreground colors for the calibration target
    # in PsychoPy, (-1, -1, -1)=black, (1, 1, 1)=white, (0, 0, 0)=mid-gray
    foreground_color = (-1, -1, -1)
    background_color = myWin.color
    genv.setCalibrationColors(foreground_color, background_color)
    
    # Set up the calibration target
    #
    # The target could be a "circle" (default), a "picture", a "movie" clip,
    # or a rotating "spiral". To configure the type of calibration target, set
    # genv.setTargetType to "circle", "picture", "movie", or "spiral", e.g.,
    # genv.setTargetType('picture')
    #
    # Use gen.setPictureTarget() to set a "picture" target
    # genv.setPictureTarget(os.path.join('images', 'fixTarget.bmp'))
    #
    # Use genv.setMovieTarget() to set a "movie" target
    # genv.setMovieTarget(os.path.join('videos', 'calibVid.mov'))
    
    # Use a picture as the calibration target
    genv.setTargetType('picture')
    genv.setPictureTarget(os.path.join('eyetrackingCode','images', 'fixTarget.bmp'))

    # Configure the size of the calibration target (in pixels)
    # this option applies only to "circle" and "spiral" targets
    # genv.setTargetSize(24)
    
    # Beeps to play during calibration, validation and drift correction
    # parameters: target, good, error
    #     target -- sound to play when target moves
    #     good -- sound to play on successful operation
    #     error -- sound to play on failure or interruption
    # Each parameter could be ''--default sound, 'off'--no sound, or a wav file
    genv.setCalibrationSounds('', '', '')
    
    # resolution fix for macOS retina display issues
    if use_retina:
        genv.fixMacRetinaDisplay()
    
    # Request Pylink to use the PsychoPy window we opened above for calibration
    pylink.openGraphicsEx(genv)

    # Step 5: Set up the camera and calibrate the tracker
    
    # Show the task instructions
    task_msg = 'I think the calibration is meant to start next, but maybe have to press ENTER twice'
    if eyetracker_dummy_mode:
        task_msg = task_msg + '\nNow, press ENTER to start the task'
    else:
        task_msg = task_msg + '\nNow, press ENTER twice to calibrate tracker'

    msg = visual.TextStim(myWin, task_msg,
                          color=genv.getForegroundColor(),
                          wrapWidth=scn_width/2)
    myWin.fillColor = genv.getBackgroundColor()
    myWin.flip()
    msg.draw()
    myWin.flip()

    # wait indefinitely, terminates upon any key press
    event.waitKeys()
    #clear screen
    myWin.fillColor = genv.getBackgroundColor()
    myWin.flip()
    msg.draw()
    myWin.flip()
            
    # skip this step if running the script in Dummy Mode
    if not eyetracker_dummy_mode:
        try:
            el_tracker.doTrackerSetup() #calibrate and validate tracker
            #Why does calibrate work but sometimes validation fail by not showing the stimulus at right place on display PC?
        except RuntimeError as err:
            print('When trying to calibrate eyetracker, ERROR:', err)
            el_tracker.exitCalibration()
           
    # close the PsychoPy window
    #myWin.close()

    # quit PsychoPy
    #core.quit()
    #sys.exit()

def calcStimPos(trial,i):
    #i is position index, either 0, 1, or 2.  Just 0 or 1 unless Humby experimnet with 3 positions
    global experiment
    offset = 0
    meridianOrOffset = False
    if meridianOrOffset:
        offset = 3 #tesschange from 3, this is the distance from fixation point 
        if not trial['whichSide']: #To vary in vertically arrayed case whether left or right side, and in horizontally arrayed case whether top or bottom side
            offset *= -1
    amountNeedToCompensateForRotation = 0.08 #when text rotated by 90 deg, not centered at x-coord any more
    if trial['horizVert']:  #vertically arrayed
        if experiment['ori'] == 90:
            x = offset+ amountNeedToCompensateForRotation
        elif experiment['ori'] == -90:
            x = offset - amountNeedToCompensateForRotation
        elif experiment['ori'] == 0: #normal unrotated condition
            x = offset
        positions =     [ [x,-wordEccentricity], [x,wordEccentricity] ]
    else:  #horizontally arrayed     left      ,        right 
        positions = [ [-wordEccentricity,offset], [wordEccentricity,offset] ]
        
    #insert 3rd position of 3 stimuli
    if experiment['numSimultaneousStim'] == 3:
        positions.insert( 1, [0,0] )  #put 0,0 into middle (index 1) of list, so will present a letter at fovea
    else:
        positions.append( [0,0] ) #For two-stimuli experiments, will draw third noise in middle
    return positions[i]

stimuliStream1 = list()
stimuliStream2 = list() #used for second, simultaneous RSVP stream
stimuliStream3 = list()
checkAlignment = False
if checkAlignment:
    alignmentCheck = visual.Line(myWin, start=(-1, 0), end=(1, 0), fillColor = (0,1,0)) 

def calcAndPredrawStimuli(stimList,spacing,i,j,k):
   global stimuliStream1, stimuliStream2, stimuliStream3
   del stimuliStream1[:]
   del stimuliStream2[:]
   del stimuliStream3[:] #only used for Humby's experiment
   #draw the stimuli that will be used on this trial, the first numWordsInStream of the shuffled list
   indices = [i,j,k]
   textStimuli = list()
   for i in range(3):
        mytext = stimList[indices[i]]
        #if spacing:
        #    mytext = mytext[0] + spacing*' ' + mytext[1]
        stim = visual.TextStim(myWin, text=mytext,
                                           height=ltrHeight,font=myFont,colorSpace='rgb',color=ltrColor, 
                                           ori=experiment['ori'],alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging)
        textStimuli.append( stim )
        
   stimuliStream1.append( textStimuli[0] )
   stimuliStream2.append( textStimuli[1] )
   stimuliStream3.append( textStimuli[2] )
#end calcAndPredrawStimuli
   
#create click sound for keyboard
clickSound = None; badSound = None
if useSound:
    try:
        clickSound=sound.Sound('406__tictacshutup__click-1-d.wav')
    except: #in case file missing, create inferiro click manually
        logging.warn('Could not load the desired click sound file, instead using manually created inferior click')
        clickSound=sound.Sound('D',octave=4, sampleRate=22050, secs=0.015)
    badSound = None
    try:
        badSound = sound.Sound('A', secs=0.02, stereo=True, hamming=True) #sound.Sound('A',octave=5, sampleRate=22050, secs=0.08)
    except:
        badSound = None
        print('Could not create an invalid key sound for typing feedback')
if showRefreshMisses:
    fixSizePix = 36 #2.6  #make fixation bigger so flicker more conspicuous
else: fixSizePix = 36
fixColor = (1,-.5,-.5)
if exportImages: fixColor= [0,0,0]
fixationPoint= visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=fixColor,size=4,units='pix',autoLog=autoLogging)
taskInstructionString1 = 'Which side you are asked to report varies.\n Be sure to report the side asked for.'
taskInstructionString2 = 'Sometimes you may not be able to see any ' + experiment['stimType'] + 's.\nIn those cases, guess.\n\nPlease do your best!'
taskInstructionPos = (0,0)
taskInstructionStim1 = visual.TextStim(myWin,pos=taskInstructionPos,colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.5,units='deg',autoLog=autoLogging)
taskInstructionStim2 = visual.TextStim(myWin,pos=taskInstructionPos,colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.5,units='deg',autoLog=autoLogging)
taskInstructionStim1.setText(taskInstructionString1,log=False)
taskInstructionStim2.setText(taskInstructionString2,log=False)
trialInstructionString = 'Keep your eyes on the red dot'
trialInstructionPos = (0,1)
trialInstructionStim = visual.TextStim(myWin,pos=trialInstructionPos,colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.5,units='deg',autoLog=autoLogging)
trialInstructionStim.setText(trialInstructionString,log=False)
respPromptStim1 = visual.TextStim(myWin,pos=(0, -.9),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.5,units='deg',autoLog=autoLogging)
respPromptStim2 = visual.TextStim(myWin,colorSpace='rgb',color=(.8,.8,0),wrapWidth=999,alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
respPromptStim3 = visual.TextStim(myWin,colorSpace='rgb',color=(.8,.8,0),wrapWidth=999,alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
feedbackPointsReminder = visual.TextStim(myWin, colorSpace='rgb',color=(.8,.8,0),wrapWidth=999,alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
totalPointsText = visual.TextStim(myWin, colorSpace='rgb',color=(.8,.8,0),wrapWidth=999,alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)

if condNum == 0:
    experimentInstructionMsg = 'If you get the left letter correct, you will receive 3 points.\n\n If you get the right letter correct, you will receive 3 points. \n\n Your points for each trial and your total points at the end will be shown.'
elif condNum == 1:
    experimentInstructionMsg = 'If you get the left letter correct, you will receive 1 points. \n\n If you get the right letter correct, you will receive 5 points. \n\n Your points for each trial and your total points at the end will be shown.'

experimentInstructionText = visual.TextStim(myWin, text=experimentInstructionMsg,colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.3,units='deg',autoLog=autoLogging)


#promptLtrsStimuli = list()
#for s in stimList:
#    respPromptStim2 = visual.TextStim(myWin,colorSpace='rgb',color=(.8,.8,0),wrapWidth=999,alignHoriz='center', alignVert='center',height=1.2,units='deg',autoLog=autoLogging)
    
promptText =''  #was originally usedd for line-up, now not used for nothin'
respPromptStim2.setText(promptText); respPromptStim3.setText(promptText)
if experiment['stimType']=='word' or experiment['numSimultaneousStim']==3:
    respPromptStim2.setText(''); respPromptStim3.setText(''); 
respPromptStim2.ori = experiment['ori']; respPromptStim3.ori = experiment['ori']
if experiment['flipped']:
    respPromptStim2.flipHoriz = True; respPromptStim3.flipHoriz = True

acceptTextStim = visual.TextStim(myWin,pos=(0, -.8),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.05,units='norm',autoLog=autoLogging)
acceptTextStim.setText('Hit ENTER to accept. Backspace to edit')
respStim = visual.TextStim(myWin,pos=(0,0),colorSpace='rgb',color=(.8,.8,0),alignHoriz='center', alignVert='center',height=1,units='deg',
                                            ori =  experiment['ori'] , autoLog=autoLogging)
#clickSound, badSound = stringResponse.setupSoundsForResponse()
requireAcceptance = False
nextText = visual.TextStim(myWin,pos=(0, .1),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
NextRemindCountText = visual.TextStim(myWin,pos=(0,.2),colorSpace='rgb',color= (1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
screenshot= False; screenshotDone = False
conditionsList = []
if experiment['spatial'] == 'vert':
    horizVert = True
else: horizVert = False
#SETTING THE CONDITIONS
#Implement the fully factorial part of the design by creating every combination of the following conditions
for rightResponseFirst in [False,True]: #does double-duty as which position when one-target. Don't forget that means each position effectively half as often
 #for trialInstructionPos in [(0,-1), (0,1)]: #half of trials instruction to fixate above fixation, half of trials below
 trialInstructionPos = -99 #not counterbalancing, just choose randomly on each trial
 for oneTarget in experiment['oneTargetConditions']: #whether only one target presented
    for whichSide in [0]: #[0,1] To vary in vertically arrayed case whether stimuli are on left or right side, and in horizontally arrayed case whether top or bottom side
     for spacing in [0]: #spacing NOT WORKING
        #oneTarget=True; horizVert=1;whichSide=1; rightResponseFirst=True
        conditionsList.append( {'rightResponseFirst':rightResponseFirst, 'leftStreamFlip':experiment['flipped'], 'trialInstructionPos':trialInstructionPos,'spacing':spacing,
                                'oneTarget':oneTarget, 'horizVert':horizVert, 'whichSide':whichSide, 'rightStreamFlip':experiment['flipped'], 'probe':'both', 'ISIframes':ISIframes} )
numConditions = len(conditionsList)
print('numConditions = ',numConditions,' trialsPerCondition=',trialsPerCondition)
trials = data.TrialHandler(conditionsList,trialsPerCondition) #method of constant stimuli

def numberToLetter(number): #0 = A, 25 = Z
    #if it's not really a letter, return @
    if number < 0 or number > 25:
        return ('@')
    else: #it's probably a letter
        try:
            return chr( ord('A')+number )
        except:
            return('@')

def letterToNumber(letter): #A = 0, Z = 25
    #if it's not really a letter, return -999
    #HOW CAN I GENERICALLY TEST FOR LENGTH. EVEN IN CASE OF A NUMBER THAT' SNOT PART OF AN ARRAY?
    try:
        #if len(letter) > 1:
        #    return (-999)
        if letter < 'A' or letter > 'Z':
            return (-999)
        else: #it's a letter
            return ord(letter)-ord('A')
    except:
        return (-999)

def stimToIdx(stim,stimList):
    #if it's not in the list of stimuli, return -999
    try:
        #http://stackoverflow.com/questions/7102050/how-can-i-get-a-python-generator-to-return-none-rather-than-stopiteration
        firstMatchIdx = next((i for i, val in enumerate(stimList) if val.upper()==stim), None) #return i (index) unless no matches, in which case return None
        #print('Looked for ',word,' in ',stimList,'\nfirstMatchIdx =',firstMatchIdx)
        return firstMatchIdx
    except:
        print('Unexpected error in stimToIdx with stim=',stim)
        return (None)
        
maxNumRespsWanted = 3

#print header for data file
print('experimentPhase\ttrialnum\tsubject\ttask\toneTarget\t',file=dataFile,end='')
print('noisePercent\tISIframes\tltrColorThis\tleftStreamFlip\trightStreamFlip\toneTarget\thorizVert\twhichSide\trightResponseFirst\tprobe\ttrialInstructionPos\t',end='',file=dataFile)
print('totalFramesBeforeStim',end='\t',file=dataFile)
for i in range( experiment['numSimultaneousStim'] ): #range(maxNumRespsWanted):
   dataFile.write('responseOrder'+str(i)+'\t')
   dataFile.write('answer'+str(i)+'\t')
   dataFile.write('response'+str(i)+'\t')
   dataFile.write('correct'+str(i)+'\t')
#   dataFile.write('responsePosRelative'+str(i)+'\t')
print('timingBlips',file=dataFile)
#end of header

def oneFrameOfStim( n,cue,seq1,seq2,seq3,cueDurFrames,letterDurFrames,thisTrial,textStimuliStream1,textStimuliStream2,textStimuliStream3,
                                       ltrColorThis,noise,proportnNoise,allFieldCoords,numNoiseDots): 
#defining a function to draw each frame of stim.
#seq1 is an array of indices corresponding to the appropriate pre-drawn stimulus, contained in textStimuli
  
  SOAframes = letterDurFrames+thisTrial['ISIframes']
  cueFrames = 0 
  stimN = int( np.floor(n/SOAframes) )
  frameOfThisLetter = n % SOAframes #every SOAframes, new letter
  timeToShowStim = frameOfThisLetter < letterDurFrames #if true, it's not time for the blank ISI.  it's still time to draw the letter
  #print 'n=',n,' SOAframes=',SOAframes, ' letterDurFrames=', letterDurFrames, ' (n % SOAframes) =', (n % SOAframes)  #DEBUGOFF
  if seq1 is not None:
    thisStimIdx = seq1[stimN] #which letter, from A to Z (1 to 26), should be shown?
  if seq2 is not None:
    thisStim2Idx = seq2[stimN]
  if seq3 is not None:
    thisStim3idx = seq3[stimN]
  #so that any timing problems occur just as often for every frame, always draw the letter and the cue, but simply draw it in the bgColor when it's not meant to be on
  cue.setLineColor( bgColor )
  if type(cueFrames) not in [tuple,list,np.ndarray]: #scalar. But need collection to do loop based on it
    cueFrames = list([cueFrames])
  for cueFrame in cueFrames: #check whether it's time for any cue
      if n>=cueFrame and n<cueFrame+cueDurFrames:
         cue.setLineColor( cueColor )
  if checkAlignment:
      alignmentCheck.setPos( calcStimPos(thisTrial,0) ); alignmentCheck.draw()
      alignmentCheck.setPos( calcStimPos(thisTrial,1) ); alignmentCheck.draw()
  if timeToShowStim: #time to show critical stimulus
        #print('thisStimIdx=',thisStimIdx, ' seq1 = ', seq1, ' stimN=',stimN)
        if seq1 is not None:
            stimuliStream1[thisStimIdx].setPos( calcStimPos(thisTrial,0) )
            stimuliStream1[thisStimIdx].setColor( ltrColorThis )
        if seq2 is not None:
            stimuliStream2[thisStim2Idx].setColor( ltrColorThis )
            stimuliStream2[thisStim2Idx].setPos( calcStimPos(thisTrial,1) )
        if seq3 is not None:
            stimuliStream3[thisStim2Idx].setColor( ltrColorThis )
            stimuliStream3[thisStim2Idx].setPos( calcStimPos(thisTrial,2) )
  else:
    if seq1 is not None:
        stimuliStream1[thisStimIdx].setColor( bgColor )
    if seq2 is not None:
        stimuliStream2[thisStim2Idx].setColor( bgColor )
    if seq3 is not None:
        stimuliStream3[thisStim2Idx].setColor( bgColor )
  if seq1 is not None:
      stimuliStream1[thisStimIdx].flipHoriz = thisTrial['leftStreamFlip']
      stimuliStream1[thisStimIdx].draw()
  if seq2 is not None:
      stimuliStream2[thisStim2Idx].flipHoriz = thisTrial['rightStreamFlip']
      stimuliStream2[thisStim2Idx].draw()
  if seq3 is not None:
    stimuliStream3[thisStim2Idx].draw()
  cue.draw()
  refreshNoise = False #Not recommended because takes longer than a frame, even to shuffle apparently. Or may be setXYs step
  if proportnNoise>0 and refreshNoise: 
    if frameOfThisLetter ==0: 
        np.random.shuffle(allFieldCoords) 
        dotCoords = allFieldCoords[0:numNoiseDots]
        noise.setXYs(dotCoords)
  if proportnNoise>0:
    noise.draw()
  return True
# #######End of function definition that displays the stimuli!!!! #####################################
#############################################################################################################################
  thisProbe = thisTrial['probe']
  #if thisProbe=='both':
  #  numRespsWanted = 1
  #else: numRespsWanted = 0
  
cue = visual.Circle(myWin, 
     radius=cueRadius,#Martini used circles with diameter of 12 deg
     lineColorSpace = 'rgb',
     lineColor=bgColor,
     lineWidth=4.0, #in pixels. Was thinner (2 pixels) in letter AB experiments
     units = 'deg',
     fillColorSpace = 'rgb',
     fillColor=None, #beware, with convex shapes fill colors don't work
     pos= [0,0], #the anchor (rotation and vertices are position with respect to this)
     interpolate=True,
     autoLog=False)#this stim changes too much for autologging to be useful
     
ltrHeight =  1 #0.7 
#All noise dot coordinates ultimately in pixels, so can specify each dot is one pixel 
noiseFieldWidthDeg=ltrHeight *1.0
noiseFieldWidthPix = int( round( noiseFieldWidthDeg*pixelperdegree ) )

def timingCheckAndLog(ts,trialN):
    #check for timing problems and log them
    #ts is a list of the times of the clock after each frame
    interframeIntervs = np.diff(ts)*1000
    #print '   interframe intervs were ',around(interframeIntervs,1) #DEBUGOFF
    frameTimeTolerance=.3 #proportion longer than refreshRate that will not count as a miss
    longFrameLimit = np.round(1000/refreshRate*(1.0+frameTimeTolerance),2)
    idxsInterframeLong = np.where( interframeIntervs > longFrameLimit ) [0] #frames that exceeded 150% of expected duration
    numCasesInterframeLong = len( idxsInterframeLong )
    if numCasesInterframeLong >0 and (not demo):
       longFramesStr =  'ERROR,'+str(numCasesInterframeLong)+' frames were longer than '+str(longFrameLimit)+' ms'
       if demo: 
         longFramesStr += 'not printing them all because in demo mode'
       else:
           longFramesStr += ' apparently screen refreshes skipped, interframe durs were:'+\
                    str( np.around(  interframeIntervs[idxsInterframeLong] ,1  ) )+ ' and was these frames: '+ str(idxsInterframeLong)
       if longFramesStr != None:
                logging.error( 'trialnum='+str(trialN)+' '+longFramesStr )
                if not demo:
                    flankingAlso=list()
                    for idx in idxsInterframeLong: #also print timing of one before and one after long frame
                        if idx-1>=0:
                            flankingAlso.append(idx-1)
                        else: flankingAlso.append(np.NaN)
                        flankingAlso.append(idx)
                        if idx+1<len(interframeIntervs):  flankingAlso.append(idx+1)
                        else: flankingAlso.append(np.NaN)
                    flankingAlso = np.array(flankingAlso)
                    flankingAlso = flankingAlso[~(np.isnan(flankingAlso))]  #remove nan values
                    flankingAlso = flankingAlso.astype(np.integer) #cast as integers, so can use as subscripts
                    logging.info( 'flankers also='+str( np.around( interframeIntervs[flankingAlso], 1) )  ) #because this is not an essential error message, as previous one already indicates error
                      #As INFO, at least it won't fill up the console when console set to WARNING or higher
    return numCasesInterframeLong
    #end timing check
    
trialClock = core.Clock()
numTrialsCorrect = 0; 
numTrialsApproxCorrect = 0;
numTrialsEachCorrect= np.zeros( experiment['numSimultaneousStim'] )
numTrialsEachApproxCorrect= np.zeros( experiment['numSimultaneousStim'] )

def do_RSVP_stim(thisTrial, seq1, seq2, seq3, ltrColorThis, proportnNoise,trialN,thisProbe):
    #relies on global variables:
    #   textStimuli, logging, bgColor, trialInstructionStim
    global framesSaved #because change this variable. Can only change a global variable if you declare it
    global totalFramesBeforeStim
    cuesPos = [] #will contain the positions in the stream of all the cues (targets)
    cuesPos.append(0)
    cuesPos = np.array(cuesPos)
    noise = None; allFieldCoords=None; numNoiseDots=0
    if proportnNoise > 0: #generating noise is time-consuming, so only do it once per trial. Then shuffle noise coordinates for each letter
        (noise,allFieldCoords,numNoiseDots) = createNoise(proportnNoise,myWin,noiseFieldWidthPix, bgColor)
    preDrawStimToGreasePipeline = list() #I don't know why this works, but without drawing it I previously have had consistent timing blip first time that draw 
    cue.setLineColor(bgColor)
    preDrawStimToGreasePipeline.extend([cue])
    for stim in preDrawStimToGreasePipeline:
        stim.draw()
    trialInstructionStim.draw(); myWin.flip(); trialInstructionStim.draw(); myWin.flip()
    trialDurFrames = int( numWordsInStream*(thisTrial['ISIframes']+letterDurFrames) ) #trial duration in frames
    logging.info( 'numtrials=' + str(trials.nTotal) + ' and this trialDurFrames='+str(trialDurFrames)+' or '+str(trialDurFrames*(1000./refreshRate))+ \
               ' ms' + '  task=' + task)
               
    noiseTexture = np.random.rand(8,8)*2.0-1
    myNoise1 = visual.GratingStim(myWin, tex=noiseTexture, size=(1.5,1), units='deg', interpolate=False,
             pos = calcStimPos(thisTrial,0), autoLog=False)#this stim changes too much for autologging to be useful
    myNoise2 = visual.GratingStim(myWin, tex=noiseTexture, size=(1.5,1), units='deg', interpolate=False,
             pos = calcStimPos(thisTrial,1), autoLog=False)
    #if experiment['numSimultaneousStim'] == 3:
    myNoise3 = visual.GratingStim(myWin, tex=noiseTexture, size=(1.5,1), units='deg', interpolate=False,
                                                          pos = calcStimPos(thisTrial,2), autoLog=False)
    #end preparation of stimuli
    
    core.wait(.1)
    trialClock.reset()
    fixatnPeriodMin = 0
    fixatnPeriodFrames = int(   (np.random.rand(1)/4.+fixatnPeriodMin)   *refreshRate)  #random interval between fixatnPeriodMin and 1/4 seconds
    ts = list(); #to store time of each drawing, to check whether skipped frames
    instructionFrames = 50
    if trialN > 2: 
        instructionFrames = 20
    for i in range(instructionFrames):
        trialInstructionStim.draw()
        if i%4 > 1: fixationPoint.draw()
        myWin.flip()
    for i in range(fixatnPeriodFrames):  #prestim fixation interval
        #if i%4>=2 or demo or exportImages: #flicker fixation on and off at framerate to see when skip frame
        #      fixation.draw()
        #else: fixationBlank.draw()
        if i%4 > 1: fixationPoint.draw()
        myWin.flip()  #end fixation interval
    #myWin.setRecordFrameIntervals(True);  #can't get it to stop detecting superlong frames
    t0 = trialClock.getTime()

    midDelay = 0.4 #0.5
    midDelayFrames = int(midDelay *refreshRate)
    #insert a pause to allow the window and python all to finish initialising (avoid initial frame drops)
    for i in range(midDelayFrames):
        if i%4 > 1: fixationPoint.draw()
        myWin.flip()
    totalFramesBeforeStim = midDelayFrames + fixatnPeriodFrames + instructionFrames
    if trackEyes:
        el_tracker.sendMessage('totalFramesBeforeStim='+str(totalFramesBeforeStim))

    for n in range(trialDurFrames): #this is the loop for this trial's stimulus!
            worked = oneFrameOfStim( n,cue,seq1,seq2,seq3,cueDurFrames,letterDurFrames,thisTrial,stimuliStream1,stimuliStream2,stimuliStream3,
                                                         ltrColorThis, noise,proportnNoise,allFieldCoords,numNoiseDots ) #draw letter and possibly cue and noise on top
            #fixationPoint.draw()
            if exportImages:
                myWin.getMovieFrame(buffer='back') #for later saving
                framesSaved +=1
            myWin.flip()
            t=trialClock.getTime()-t0;  ts.append(t);

    #draw the noise mask
    thisProbe = thisTrial['probe']
    if thisProbe == 'long':
        noiseMaskMin = .2
    else: noiseMaskMin = .2
        
    noiseMaskFrames = int(noiseMaskMin *refreshRate)
    for i in range(noiseMaskFrames):
        myNoise1.phase = np.random.rand(1); myNoise2.phase = np.random.rand(1); myNoise3.phase = np.random.rand(1)
        if seq1:
            myNoise1.draw(); 
        if seq2:
            myNoise2.draw()
        #if seq1 and seq2: #if left or right (two stimuli presented), also draw middle noise (only don't draw it if only one stim presented)
        #    myNoise3.draw()
        fixationPoint.draw()
        if exportImages:
            myWin.getMovieFrame(buffer='back') #for later saving
            framesSaved +=1
        myWin.flip()
    #myWin.flip() #Need this
    if thisProbe == 'long':
        probeDelay = 1.5
    else: probeDelay = 0.0
    
    probeDelayFrames = int(probeDelay *refreshRate)
    #insert a pause to allow the window and python all to finish initialising (avoid initial frame drops)
    for i in range(probeDelayFrames):
         myWin.flip()
           
    #end of big stimulus loop
    myWin.setRecordFrameIntervals(False);
    
    if task=='T1':
        respPromptStim1.setText('What was the underlined word?',log=False)   
    else: respPromptStim1.setText('Error: unexpected task',log=False)
    
    return ts

pctCompletedBreak = -99 #no break

def handleAndScoreResponse(passThisTrial,response,responseAutopilot,task,correctAnswer):
    #Handle response, calculate whether correct, ########################################
    #responses are actual characters
    #correctAnswer is index into stimSequence
    #autopilot is global variable
    #print('response=',response)
    if autopilot or passThisTrial:
        response = responseAutopilot
    correct = 0
    #approxCorrect = 0

    correctAnswer = correctAnswer.upper()
    responseString= ''.join(['%s' % char for char in response])
    responseString= responseString.upper()
    #print('correctAnswer=',correctAnswer ,' responseString=',responseString)
    if correctAnswer == responseString:
        correct = 1
    #print('correct=',correct)
    
    print(correctAnswer, '\t', end='', file=dataFile) #answerN
    print(responseString, '\t', end='', file=dataFile) #responseN
    print(correct, '\t', end='',file=dataFile)  #correctN
    return correct
    #end handleAndScoreResponses
    
def play_high_tone_correct_low_incorrect(correct, playIncorrectSound, passThisTrial=False):
    highA = sound.Sound('G',octave=5, sampleRate=6000, secs=.3)
    low = sound.Sound('F',octave=3, sampleRate=6000, secs=.3)
    highA.setVolume(0.9)
    low.setVolume(1.0)
    if correct:
        highA.play()
    elif passThisTrial:
        high= sound.Sound('G',octave=4, sampleRate=2000, secs=.08)
        for i in range(2): 
            high.play();  low.play(); 
    elif playIncorrectSound: #incorrect
        low.play()

def doAuthorRecognitionTest(autopilot):
    oneThirtyEight =['Agatha Christie', 'Aimee Dorr', 'Alex Lumsden', 'Alice Munro', 'Alvin Toffler', 'Amy Tan', 'Andrew Greeley', 'Anne Rice', 'Arthur C. Clarke', 'Barbara Cartland', 'Brian Bigelow', 'C.S. Lewis', 'Caleb Lim', 'Carl Corter', 'Carla Grinton', 'Carol Berg', 'Carol Shields', 'Carter Anvari', 'Charles Condie', 'Christopher Barr', 'Christopher Moore', 'Dale Blyth', 'Dan Brown', 'Daniel Quinn', 'Danielle Steel', 'David Baldacci', 'David Perry', 'David Singer', 'Dean Koontz', 'Denise Daniels', 'Devon Chang', 'Diana Gabaldon', 'Diane Cuneo', 'Edward Cornell', 'Elizabeth George', 'Elliot Blass', 'Eric Amsel', 'Erica Jong', 'Frances Fincham', 'Frank Gresham', 'Frank Herbert', 'Frank Kiel', 'Frank Manis', 'Gary Beauchamp', 'George R.R. Martin', 'Geraldine Dawson', 'Harrison Boldt', 'Hilda Borko', 'Hugh Lytton', 'Isaac Asimov', 'Jackie Collins', 'James Clavell', 'James Michener', 'James Morgan', 'Janet Evanovich', 'Janice Taught', 'Jean M. Auel', 'Jeffery Eugenides', 'Jennifer Butterworth', 'Jennifer Marshal', 'John Condry', 'John Grisham', 'John Jakes', 'Judith Krantz', 'Judy Blume', 'Julia Connerty', 'K. Warner Schaie', 'Kate Grenville', 'Kate Pullinger', 'Katherine Carpenter', 'Kirby Kavanagh', 'Lauren Benjamin', 'Laurie King', 'Lena Johns', 'Lilly Jack', "Louis L'Amour", 'Lynn Liben', 'M. Scott Peck', 'Maeve Binchy', 'Margaret Atwood', 'Margaret Laurence', 'Margarita Azmitia', 'Mark Elder', 'Mark Strauss', 'Martin Ford', 'Michael Moore', 'Mimi Hall', 'Miriam Sexton', 'Miriam Toews', 'Mordecai Richler', 'Morton Mendelson', 'Naomi Choy', 'Naomi Klein', 'Noam Chomsky', 'Oscar Barbary', 'Patricia Cornwell', 'Peter Carey', 'Peter Rigg', 'Pierre Berton', 'Pricilla Levy', 'Reed Larson', 'Reuben Baron', 'Richard Passman', 'Robert Emery', 'Robert Fulghum', 'Robert Inness', 'Robert J. Sawyer', 'Robert Jordan', 'Robert Ludlum', 'Robert Siegler', 'Robertson Davies', 'Rohinton Mistry', 'Russell Banks', 'Ryan Gilbertson', 'Ryan Morris', 'S.E. Hinton', 'Samuel Paige', 'Scott Paris', 'Sheryl Green', 'Sidney Sheldon', 'Sophia Martin', 'Sophie Kinsella', 'Stephen Coonts', 'Stephen J. Gould', 'Stephen King', 'Stirling King', 'Sue Grafton', 'Susan Kormer', 'Suzanne Clarkson', 'Thomas Bever', 'Timothy Findley', 'Tom Clancy', 'Tracy Tomes', 'Ursula LeGuin', 'V.C. Andrews', 'W. Patrick Dickson', 'Wayne Johnston', 'Wayson Choy']
    oneThirtyFive = oneThirtyEight[0:-3]
    possibleResps = oneThirtyFive #oneThirtyEight #sixteen
    #print('num authors = ',len(possibleResps))
    myWin.flip()
    expStop = False
    myMouse = event.Mouse(visible=True) #the mouse absolutely needs to be reset, it seems, otherwise maybe it returns coordinates in wrong units or with wrong scaling?
    expStop,timedout,selected,selectedAutopilot = \
                doAuthorLineup(myWin, bgColor,myMouse, clickSound, badSound, possibleResps, autopilot)
    if autopilot:
        selected = selectedAutopilot
    return expStop,timedout,selected

expStop=False
#Do authors task
myWin.allowGUI =True
#myWin.close() #Seems to work better if close and open new window (even though units the same), both in terms of dimensions (even though same here!) and double-clicking
#take a couple extra seconds to close and reopen window unfortunately
#myWin = visual.Window(fullscr=True,monitor=mon,colorSpace='rgb',color=bgColor,units='deg')

experimentClock = core.Clock()
expTimeLimit = 60*17
expTimedOut = False
nDoneMain = -1 #change to zero once start main part of experiment
if doStaircase:
    #create the staircase handler
    #Change the activated bracket depending on practice/actual experiment
    stepSizesLinear = [.001] #[.6,.6,.5,.5,.4,.3,.3,.1,.1,.1,.1,.05] #for practice trials, use [.001]
    minVal = bgColor[0]+.15
    maxMoreFramesAllowed = 6
    #lumRange = 1 - minVal
    staircase = data.StairHandler(
        startVal=ltrColor,
        stepType='lin',
        stepSizes=stepSizesLinear,  # reduce step size every two reversals
        minVal=minVal, 
        maxVal=maxMoreFramesAllowed + .99, 
        nUp=1, nDown=2,  # 1-up 3-down homes in on the 80% threshold. Gravitates toward a value that has an equal probability of getting easier and getting harder.
        #See Wetherill & Levitt 1965, 1 up 2 down goes for 71% correct. And if 2 letters are independent, each correct = sqrt(.71) = 84% correct.
        nTrials=500)
    print('Created conventional staircase')
        
    #phasesMsg = ('Doing '+str(prefaceStaircaseTrialsN)+'trials with noisePercent= '+str(prefaceStaircaseNoise)+' then doing a max '+str(staircaseTrials)+'-trial staircase')
    #print(phasesMsg); logging.info(phasesMsg)

    #printStaircase(staircase, descendingPsycho, briefTrialUpdate=True, printInternalVal=True, alsoLog=False) 
    #print('staircase.quantile=',round(staircase.quantile(),2),' sd=',round(staircase.sd(),2))

noisePercent = defaultNoiseLevel
phasesMsg = 'Experiment will have '+str(trials.nTotal)+' trials. Letters will be drawn with superposed noise of ' + "{:.2%}".format(defaultNoiseLevel)
print(phasesMsg); logging.info(phasesMsg)
myMouse = event.Mouse(visible=True,win=myWin)
nDoneMain =0
pointsTotalRight = 0; pointsTotalLeft = 0

experimentInstructionText = visual.TextStim(myWin, text=experimentInstructionMsg, pos=(0, 0), color='white')
experimentInstructionText.draw()
myWin.flip()
event.waitKeys() #Show points total message until a key is pressed

while nDoneMain < trials.nTotal and expStop!=True: #MAIN EXPERIMENT LOOP
    #print('nDoneMain=',nDoneMain)
    expStop = False
    whichStim0 = np.random.randint(0, len(stimList) )
    whichStim1 = np.random.randint(0, len(stimList) ) 
    #check that whichStim0 and whichStim1 don't have letters in common. If they do generate a new pair
    whichStim2 = np.random.randint(0, len(stimList) ) #only used in Humby experiment
    trial = trials.next()
    calcAndPredrawStimuli(stimList,trial['spacing'],whichStim0,whichStim1,whichStim2)
    thisTrial = copy.deepcopy(trial) #so that can change its values, otherwise messing with it screws up the trialhandler
    ltrColorThis = ltrColor
    howManyMoreFrames = 0
    event.clearEvents(); keyPressed = False; f =0
    if nDoneMain <=1:
        while f < 500 and not keyPressed:
            if nDoneMain == 0:
                taskInstructionStim1.draw()
            elif nDoneMain ==1:
                taskInstructionStim2.draw()
            myWin.flip(); f += 1
            keyPressed = event.getKeys() #keyList=list(string.ascii_lowercase))
    if doStaircase:
        if (not stopStaircaseAfterFirstBlock) or (nDoneMain <= numConditions*3):
            print('staircase.stepSizeCurrent = ',staircase.stepSizeCurrent, 'staircase._nextIntensity=',staircase._nextIntensity, 'howManyMoreFrames=',howManyMoreFrames)
            howManyMoreFrames = np.floor( staircase.next() )
            print('changed howManyMoreFrames to ', howManyMoreFrames)
            #I THINK THE BELOW IS NOT WORKING PROPERLY, using change rather than absolute value
            #Why is this in terms of a change rather than the absolute value suggested by the staircase output?
            thisTrial['ISIframes'] += howManyMoreFrames #increase duration by however much it is greater than 1
            if howManyMoreFrames>0:
                #Just change the brightness of the letter because need the base brightness when longer frames to be pretty high
                #need the base brightness when longer frames to be pretty high, otherwise they might never get back to lower number of frames
                ltrColorThis = min(1,   0 + (ltrColorThis - howManyMoreFrames)   ) #For each bit greater 1, increase luminance
                print('staircase has changed number of frames to thisTrial[ISIframes]=', thisTrial['ISIframes'], ' and now ltrColorThis =',ltrColorThis)
            ltrColorThis = round(ltrColorThis,2)
            print('staircase.stepSizeCurrent = ',staircase.stepSizeCurrent, 'staircase._nextIntensity=',staircase._nextIntensity,'ltrColorThis=',ltrColorThis)
            #trialInstructionStim.setText('lum=' + str(ltrColorThis)+ ' f='+ str(howManyMoreFrames), log=False) #debug
    if thisTrial['trialInstructionPos']==-99: #pick randomly
        trialInstructionPositions = [(0,-1), (0,1)]
        random.shuffle(trialInstructionPositions)
        thisTrial['trialInstructionPos'] = trialInstructionPositions[0]
    trialInstructionStim.setPos( thisTrial['trialInstructionPos'] )
    myMouse.setVisible(False) #because showing the stimulus is next

    if trackEyes:
        doDriftCorrect = False
        if doDriftCorrect:
            # we recommend drift correction at the beginning of each trial
            # the doDriftCorrect() function requires target position in integers
            # the last two arguments:
            # draw_target (1-default, 0-draw the target then call doDriftCorrect)
            # allow_setup (1-press ESCAPE to recalibrate, 0-not allowed)        
            while not eyetracker_dummy_mode: # Skip drift-check if running the script in Dummy Mode
                # terminate the task if no longer connected to the tracker or
                # user pressed Ctrl-C to terminate the task
                if not el_tracker.isConnected():
                    print('Eyetracker not connected')
                    expStop = True
                if el_tracker.breakPressed():
                    print('CTRL-C pressed to terminate')
                    expStop = True
        
                # drift-check and re-do camera setup if ESCAPE is pressed
                try:
                    error = el_tracker.doDriftCorrect(int(scn_width/2.0),
                                                      int(scn_height/2.0), 1, 1)
                    # break following a successful drift-check, which I guess just continues? IF so, bad coding practice I think
                    if error is not pylink.ESC_KEY:
                        print('Something went wrong with doDriftCorrect')
                        expStop = True
                        #break
                except:
                    print('Something except-ional went wrong with doDriftCorrect')
                    expStop = True
    
        # put tracker in idle/offline mode before recording, which is what they recommend.
        # Maybe helps stop skipping trials due to not recording?
        el_tracker.setOfflineMode()
    
        # Start recording
        # arguments: sample_to_file, events_to_file, sample_over_link, event_over_link (1-yes, 0-no)
        try:
            el_tracker.startRecording(1, 1, 1, 1)
        except RuntimeError as error:
            print("ERROR:", error)
    
        # Allocate some time for the tracker to cache some samples
        pylink.pumpDelay(100)

    if nDoneMain <= 1: #For first trial, give extra long instruction
        for i in range(70):
            trialInstructionStim.draw()
            if i > 30:
                fixationPoint.draw()
            myWin.flip()
    thisProbe = thisTrial['probe']
    if thisProbe=='both':
      numRespsWanted = experiment['numSimultaneousStim']
    else: numRespsWanted = 1
    
    #Determine which letters/words will be drawn
    idxsStream1 = [0]; idxsStream2 = [0]
    if thisTrial['oneTarget']:
        idxsStream3 = None #no middle target (3-letter condition)
        if thisTrial['rightResponseFirst']: #in oneTarget condition, rightResponseFirst controls which is shown
            idxsStream1 = None 
        else:
            idxsStream2 = None
        print('oneTarget and idxsStream1=',idxsStream1,' idxsStream2=',idxsStream2)
    idxsStream3 = None
    if experiment['numSimultaneousStim'] == 3:
       idxsStream3 = [0]
    ts  =  do_RSVP_stim(thisTrial, idxsStream1, idxsStream2, idxsStream3, ltrColorThis, noisePercent/100.,nDoneMain,thisProbe)
    numCasesInterframeLong = timingCheckAndLog(ts,nDoneMain)

    if trackEyes:
        #Send a 'TRIAL_RESULT' message to mark the end of trial. See Data Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
        el_tracker.sendMessage('TRIAL_RESULT %d' % pylink.TRIAL_OK)
        stopEyeTracking(el_tracker) #just until the next trial

    #call for each response
    #if myMouse == None:  #mouse sometimes freezes if don't call event.Mouse certain number of times I think, no idea why
        #myMouse = event.Mouse(visible=True,win=myWin)
    myMouse.setVisible(True)
    fixationPoint.setColor([.6,.6,.6]) #white not red so person doesn't feel they have to look at it

    possibleResps = stimList
    doLineupBothSides = True
    
    numCharsInResponse = len(stimList[0])
    dL = [None]*numRespsWanted #dummy list for null values, because want one per response
    expStop = [expStop]*numRespsWanted
    expStop = copy.deepcopy(expStop); responses = copy.deepcopy(dL); responsesAutopilot = copy.deepcopy(dL); passThisTrial=copy.deepcopy(dL)
    if thisProbe == 'both': #Either have word on both sides or letter on both sides
        if thisTrial['oneTarget']:
            numToReport = 1
            doLineupBothSides = False
        else:
            numToReport =  experiment['numSimultaneousStim']
            doLineupBothSides = True
        responseOrder = list( range(numToReport) )
        if (numToReport == 3): #not counterbalanced, so just shuffle
            random.shuffle(responseOrder)
        elif thisTrial['rightResponseFirst']: #change order of indices depending on rightResponseFirst. response0, answer0 etc refer to which one had to be reported first
            responseOrder.reverse()
        respI = 0
        #print("thisTrial = ",thisTrial)
        print(" numToReport=",numToReport, "thisTrial[rightResponseFirst] =",thisTrial['rightResponseFirst'],'responseOrder= ',responseOrder)
        while respI < numToReport and not np.array(expStop).any(): #iterate through number of responses needed
          lineupResponse = True #Tess experiments
          if lineupResponse:
            leftRightCentralBottomTop = thisTrial['horizVert']*3  + thisTrial['rightResponseFirst']
            print("thisTrial['horizVert']=",thisTrial['horizVert'],'respI = ',respI, ' about to call doLineup with doLineupBothSides= ',doLineupBothSides,', leftRightCentralBottomTop=', leftRightCentralBottomTop)
            
            expStop[0],passThisTrial,responses,buttons,responsesAutopilot = \
                    letterLineupResponse.doLineup(myWin,bgColor,myMouse,useSound,clickSound,badSound,possibleResps,doLineupBothSides,
                                                    leftRightCentralBottomTop,showClickedRegion,autopilot)
            print('Finished one doLineup', " responses=", responses)
            if autopilot: print("responsesAutopilot = ",responsesAutopilot)
            if numToReport ==1:
                side = thisTrial['rightResponseFirst'] * 2 - 1 #-1 for left/bottom, 1 for right/top
            elif numToReport == 2:
                side = responseOrder[respI] * 2 -1  #-1 for left/bottm, 1 for right/top
            elif numToReport == 3:
                side = (responseOrder[respI] - 1)  #-1 for left/bottom, 0 for middle, 1 for right/top
            
            if doLineupBothSides: #doLineup collected two responses already
                respI += 2
            else: #doLineup collected only one response
                respI += 1
          else: #type in response rather than click on lineup
            devRespPrompt = 2*wordEccentricity * side #put response prompt farther out than stimulus, so participant is sure which is left and which right
            if numToReport == 1 or numToReport == 2:
                locationNames= [ 'the left', 'the right',  'the bottom','top' ]
                numLocations = 2
            elif numToReport == 3:
                locationNames = [ 'the left', 'at centre', 'the right',  'the bottom', 'at centre', 'top' ]
                numLocations = 3
            respPromptString = 'Type the ' + experiment['stimType']
            if numToReport == 1:
                respPromptString += ' that was presented'
                #locationName = locationNames[   thisTrial['horizVert'] * numLocations + int((side+1)/2)   ]
            else:
                locationName  = locationNames[      thisTrial['horizVert'] * numLocations  +   responseOrder[respI]      ]
                respPromptString += ' that was on ' +  locationName
            respPromptStim1.setText(respPromptString,log=False)
            if thisTrial['horizVert']:
                x=0; y=devRespPrompt
                if numToReport == 3: #need an orthogonal offset, so doesn't overlap when at fixation
                    x = -wordEccenticity
                #x coordinate have to compensate if rotated, use calcStimPos to check
                pos  = calcStimPos(thisTrial,0)
                x = pos[0]                               
            else:
                x=devRespPrompt; y=0
                if numToReport == 3: #need an orthogonal offset, so doesn't overlap when at fixation
                    y = -wordEccentricity
            respStim.setPos([x,y])
            respStim.flipHoriz = experiment['flipped']
            
            #Set position of respPromptStim
            xPrompt =  x*2 if thisTrial['horizVert'] else x*4  #needs to be further out if horizontal to fit the text
            respPromptStim1.setPos([xPrompt, y*2])
            #respPromptStim2, 3 will be at left and right, vertically arrayed if vertical stimuli arrangement,
            #  at top and bottom, horizontally arrayed if horizontal stimuli arrangement
            edge = .7
            if thisTrial['horizVert'] and experiment['ori'] != 0: # rotated, draw text left and right
                    respPromptStim2.setPos( [-edge,0] ) #left
                    respPromptStim3.setPos( [edge, 0] ) #right
            else:
                respPromptStim2.setPos( [0,-edge] ) #bottom
                respPromptStim3.setPos( [0, edge] ) #top
            #stringReponse was used for psyc1002
            expStop[respI],passThisTrial[respI],responses[respI],responsesAutopilot[respI] = stringResponse.collectStringResponse(
                                    numCharsInResponse,x,y,respPromptStim1,respPromptStim2,respPromptStim3,respStim,acceptTextStim,fixationPoint, (1 if experiment['stimType']=='digit' else 0), myWin,
                                clickSound,badSound, requireAcceptance,autopilot,changeToUpper,responseDebug=True )
        fixationPoint.setColor(fixColor)
        expStop = np.array(expStop).any(); passThisTrial = np.array(passThisTrial).any()
    
    if not expStop:
        print('main\t', end='', file=dataFile) #first thing printed on each line of dataFile to indicate main part of experiment
        print(nDoneMain,'\t', end='', file=dataFile)
        print(subject,'\t',task,'\t', thisTrial['oneTarget'], '\t', round(noisePercent,3),'\t', end='', file=dataFile)
        print(thisTrial['ISIframes'],'\t', end='', file=dataFile)
        print(ltrColorThis,'\t', end='', file=dataFile)
        print(thisTrial['leftStreamFlip'],'\t', end='', file=dataFile)
        print(thisTrial['rightStreamFlip'],'\t', end='', file=dataFile)
        print(thisTrial['oneTarget'],'\t', end='', file=dataFile)
        print(thisTrial['horizVert'],'\t', end='', file=dataFile)
        print(thisTrial['whichSide'],'\t', end='', file=dataFile)
        print(thisTrial['rightResponseFirst'],'\t', end='', file=dataFile)
        print(thisTrial['probe'],'\t', end='', file=dataFile)
        print(thisTrial['trialInstructionPos'],'\t', end='', file=dataFile)
        print(totalFramesBeforeStim,end='\t',file=dataFile)
        eachCorrect = np.ones(numRespsWanted)*-999

        numToPrint = numRespsWanted
        print('getting ready to score response, numToPrint=',numToPrint, "thisTrial[oneTarget]=",thisTrial['oneTarget'])
        
        if not thisTrial['oneTarget']: #normal case of more than one target
            for streami in range(numToPrint): #scored and printed to dataFile in left first, right second order even if collected in different order
                print(responseOrder[streami],'\t', end='', file=dataFile)
                if streami==0:
                    sequenceStream = idxsStream1; correctAnswerIdx = whichStim0
                elif streami==1: 
                    sequenceStream = idxsStream2; correctAnswerIdx = whichStim1
                elif streami==2:
                    sequenceStream = idxsStream2; correctAnswerIdx = whichStim2
                    
                correctAnswer = stimList[correctAnswerIdx]
                print(" correctAnswer =",correctAnswer, ", correctAnswerIdx = ", correctAnswerIdx, ' streami=',streami,' whichStim0/1= ',whichStim0,',',whichStim1)
                
                respThisStreamI = responseOrder.index(streami)
                print('respThisStreamI = ',respThisStreamI, 'responses=',responses)
                if autopilot:
                    respThisStream = responsesAutopilot[respThisStreamI]
                else:
                    respThisStream = responses[respThisStreamI]
                print ("responses = ", responses, " responsesAutopilot=", responsesAutopilot, ' respThisStream = ', respThisStream)   #responseOrder
    
                correct = handleAndScoreResponse(passThisTrial,respThisStream,responsesAutopilot,task,correctAnswer)
                eachCorrect[streami] = correct
        else: #thisTrial['oneTarget'] so only one response so there's only one response to score, but need to print out both to datafile still
                print(responseOrder[0],'\t', end='', file=dataFile)
                if autopilot:
                    respThisStream = responsesAutopilot[0]
                else:
                    respThisStream = responses[0]
                
                if thisTrial['rightResponseFirst']==0:
                    correctAnswerIdx = whichStim0
                if thisTrial['rightResponseFirst']==1:
                    correctAnswerIdx = whichStim1
                correctAnswer = stimList[correctAnswerIdx]
                
                correct = handleAndScoreResponse(passThisTrial,respThisStream,responsesAutopilot,task,correctAnswer)
                eachCorrect = np.array([correct, -99]) #correct always first, unlike when 2 targets where position tells you something
                print('correct= ',correct, 'responses=',responses, 'correctAnswer=',correctAnswer, ", correctAnswerIdx = ", correctAnswerIdx, ' whichStim0/1= ',whichStim0,',',whichStim1)

                #kludge to pad with null datafile spaces when only one target presented
                for i in range(experiment['numSimultaneousStim']-1):
                    print(-99, '\t', end='', file=dataFile) #responseOrderN
                    print(-99, '\t', end='', file=dataFile) #answerN
                    print(-99, '\t', end='', file=dataFile) #responseN
                    print(-99, '\t', end='',file=dataFile)  #correctN
    
        print(numCasesInterframeLong, file=dataFile) #timingBlips, last thing recorded on each line of dataFile
        #Don't want to feed allCorrect into staircase because then for e.g. a staircase targeting 70% correct, they will get 84% correct on each if two letters but even higher if 3 letters
        #Instead, average and round. This means that if get 1 out of 2 correct, counts as correct. If get 2 out of 3 correct, counts as correct but one is not enough.
        correctForStaircase = round( np.mean(eachCorrect) )
        if thisTrial['oneTarget']:
            not99idx = np.where(eachCorrect != -99)[0][0]
            #not99idx = not eachCorrect.index(-99)
            correctForStaircase = eachCorrect[not99idx]
        print('eachCorrect=',eachCorrect, 'correctForStaircase=',correctForStaircase)
        if doStaircase and nDoneMain>4:
            staircase.addResponse( correctForStaircase )
        numTrialsCorrect += eachCorrect.all() #so count -1 as 0
        numTrialsEachCorrect += eachCorrect #list numRespsWanted long
            
        if exportImages:  #catches one frame of response
             myWin.getMovieFrame() #I cant explain why another getMovieFrame, and core.wait is needed
             framesSaved +=1; core.wait(.1)
             myWin.saveMovieFrames('images_sounds_movies/frames.png') #mov not currently supported 
             expStop=True
        #core.wait(.1)
        if eachCorrect[0] == 0 and eachCorrect[1] == 0:
            pointsLeft = 0; pointsRight = 0
        elif eachCorrect[0] == 1 and eachCorrect[1] == 0:
            pointsLeft = pointsEachCond[condNum][0]; pointsRight = 0
        elif eachCorrect[0] == 0 and eachCorrect[1] == 1:
            pointsLeft = 0; pointsRight = pointsEachCond[condNum][1]
        elif eachCorrect[0] == 1 and eachCorrect[1] == 1:
            pointsLeft = pointsEachCond[condNum][0]; pointsRight = pointsEachCond[condNum][1]
        pointsTotalLeft += pointsLeft
        pointsTotalRight += pointsRight

        if feedback and useSound: 
            playIncorrectSound = False
            play_high_tone_correct_low_incorrect(correctForStaircase, playIncorrectSound, passThisTrial=False)
            blankInBetween = "       "
            msg = str( pointsLeft ) + blankInBetween + str( pointsRight )

            feedbackPointsReminder.setText(msg)
            feedbackDur = 1
            for frameN in range(int(feedbackDur*refreshRate)):
                feedbackPointsReminder.draw()
                myWin.flip()
        nDoneMain+=1
        dataFile.flush(); logging.flush()
        print('nDoneMain=', nDoneMain,' trials.nTotal=',trials.nTotal, 'expStop=',expStop) #' trials.thisN=',trials.thisN
        #check whether time for break
        if (trials.nTotal > 6 and nDoneMain > 2 and nDoneMain %
             ( trials.nTotal*pctCompletedBreak/100. ) ==1 ):  #dont modulus 0 because then will do it for last trial
                nextText.setText('Press "SPACE" to continue!')
                nextText.draw()
                progressMsg = 'Completed ' + str(nDoneMain) + ' of ' + str(trials.nTotal) + ' trials'
                NextRemindCountText.setText(progressMsg)
                NextRemindCountText.draw()
                myWin.flip() # myWin.flip(clearBuffer=True) 
                waiting=True
                while waiting:
                   if autopilot: break
                   elif expStop == True:break
                   for key in event.getKeys():      #check if pressed abort-type key
                         if key in ['space','ESCAPE']: 
                            waiting=False
                         if key in ['ESCAPE']:
                            expStop = True
                myWin.clearBuffer()
        #end break
        core.wait(.05);  time.sleep(.05)
        if experimentClock.getTime() > expTimeLimit:
            expTimedOut = True
        print('got to end of loop')
        #end main trials loop

pointsTotalMsg = 'Total points = ' + str(pointsTotalLeft + pointsTotalRight)
totalPointsText.setText(pointsTotalMsg)
totalPointsText.draw()
myWin.flip()
print(pointsTotalMsg)
event.waitKeys() #Show points total message until a key is pressed

if trackEyes:
  el_tracker.closeDataFile()
  if eyetrackFileGetFromEyelinkMachine:
    eyetrackerFileWaitingText = visual.TextStim(myWin,pos=(-.1,0),colorSpace='rgb',color = (1,1,1),anchorHoriz='center', anchorVert='center', units='norm',autoLog=autoLogging)
    eyetrackerFileWaitingText.setText('Waiting for eyetracking file from Eyelink computer. Do not abort eyetracking machine or file will not be saved?')
    eyetrackerFileWaitingText.draw()
    myWin.flip()
    try:
        # Download the EDF data file from the Host PC to a local data folder
        # parameters: source_file_on_the_host, destination_file_on_local_drive
        el_tracker.receiveDataFile(edf_fname_short,edf_fname_short) 
    except RuntimeError as error:
        print('when trying to get EDF file from eyetracker computer, ERROR:', error)
  else: 
    print('You will have to get the Eyelink EDF file off the eyetracking machine by hand')
        
  msg = closeEyeTracker(el_tracker)
  print(msg); logging.info(msg) #""Eyelink connection closed successfully" or "Eyelink not available, not closed properly"

timeAndDateStr = time.strftime("%H:%M on %d %b %Y", time.localtime())
msg = 'Stopping at '+timeAndDateStr
print(msg); logging.info(msg)
if expStop:
    msg = 'user aborted experiment on keypress with trials done=' + str(nDoneMain) + ' of ' + str(trials.nTotal+1)
    print(msg); logging.error(msg)
if expTimedOut:
    msg = 'Experiment timed out with trials done=' + str(nDoneMain) + ' of ' + str(trials.nTotal+1)
    print(msg); logging.info(msg)
if nDoneMain >0:
    trialsExactlyCorrectPct = numTrialsCorrect*1.0/nDoneMain*100.
    proportnCorrectMsg =  'Of '+str(nDoneMain)+' trials, on '+str(round(trialsExactlyCorrectPct,2))+ '% of all trials all targets reported exactly correct'
    print(proportnCorrectMsg)
    logging.info(proportnCorrectMsg)
    #for i in range(numRespsWanted): #Doesn't work because oneTarget trials screws up numTrialsEachCorrect
    #    print('stream',i,': ',round(numTrialsEachCorrect[i]*1.0/nDoneMain*100.,2), '% correct',sep='')
dataFile.flush(); logging.flush(); dataFile.close()

logging.info("Program terminating normally."); print("Terminated normally.")
core.quit()
