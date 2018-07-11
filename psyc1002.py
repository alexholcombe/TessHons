#Alex Holcombe alex.holcombe@sydney.edu.au
#See the github repository for more information: https://github.com/alexholcombe/PSYC1002
from __future__ import print_function, division
from psychopy import monitors, visual, event, data, logging, core, gui
useSound = False
if useSound:
    from psychopy import sound
import psychopy.info
import scipy
import numpy as np
from math import atan, log, ceil
import shutil
import copy, time, sys, os, string
try:
    from noiseStaircaseHelpers import printStaircase, toStaircase, outOfStaircase, createNoise, plotDataAndPsychometricCurve
except ImportError:
    print('Could not import from noiseStaircaseHelpers.py (you need that file to be in the same directory)')
try:
    import stringResponse
except ImportError:
    print('Could not import stringResponse.py (you need that file to be in the same directory)')
#try:
#    import letterLineupResponse
#except ImportError:
#    print('Could not import letterLineupResponse.py (you need that file to be in the same directory)')
try:
    from authorRecognitionLineup import doAuthorLineup
except ImportError:
    print('Could not import authorRecognitionLineup.py (you need that file to be in the same directory)')
try:
    from getpass import getuser
except ImportError:
    print('ERROR Could not import getpass')

wordEccentricity=  0.9 #4
tasks=['T1']; task = tasks[0]
#same screen or external screen? Set scrn=0 if one screen. scrn=1 means display stimulus on second screen.
#widthPix, heightPix
quitFinder = False #if checkRefreshEtc, quitFinder becomes True
autopilot=False
demo=False #False
exportImages= False #quits after one trial
subject=getuser()  #https://stackoverflow.com/a/842096/302378
#subject = 'abajjjjd8333763' #debug
if autopilot: subject='auto'
cwd = os.getcwd()
print('current working directory =',cwd)
if os.path.isdir('.'+os.sep+'Submission'):
    dataDir='Submission'
else:
    print('"Submission" directory does not exist, so saving data in present working directory')
    dataDir='.'
timeDateStart = time.strftime("%d%b%Y_%H-%M", time.localtime())

showRefreshMisses=True #flicker fixation at refresh rate, to visualize if frames missed
feedback=True 
autoLogging=False
refreshRate = 60
if demo:
   refreshRate = 60.;  #100

numWordsInStream = 1
myFont =  'Arial' # 'Sloan' # 

#Set up the list of experiments, then allocate one to the subject
experimentTypesStim = ['word','letter','digit']
experimentTypesSpatial = ['horiz','vert']
#create dictionary of all combinations
experimentsList = []
#Creating the list of experiments
#Implement the fully factorial part of the design by creating every combination of the following conditions
for stim in experimentTypesStim:
    for spatial in experimentTypesSpatial:
        experimentsList.append( {'stimType':stim, 'spatial':spatial} )

experimentNum = abs(hash(subject)) % len(experimentsList)   #https://stackoverflow.com/a/16008760/302378
experiment = experimentsList[ experimentNum ]
logging.info(experiment); print(experiment)
import json
authorsData= {} #stuff to record in authors data file
authorsData.update(experiment)
#authorsData['stimType'] = stimType
#authorsData['spatial'] = spatial
print('authorsData=',authorsData)

numStimsWanted = 26
if experiment['stimType'] == 'letter':
    stimList = list(string.ascii_lowercase)
elif experiment['stimType'] == 'digit':
    stimList = ['0','1','2','3','4','5','6','7','8','9']
elif experiment['stimType'] == 'word':
    stimList = list()
    #read word list
    stimDir = 'inputFiles'
    stimFilename = os.path.join(stimDir,"BrysbaertNew2009_3ltrWords_don_deleted.txt")
    f = open(stimFilename)
    eachLine = f.readlines()
    if len(eachLine) < numStimsWanted:
        print("ERROR file doesn't have as many lines as expected, wanted more words.")
    for l in range(1,numStimsWanted):#skip first, header line, therefore start with line 1
        line = eachLine[l]
        values = line.split() #splits on tabs or whitespaces and trims leading,following including newlines
        word = values[0]
        stimList.append( word )
        print(word,'\t')

bgColor = [-.7,-.7,-.7] # [-1,-1,-1]
cueColor = [-.7,-.7,-.7] #originally [1.,1.,1.]
letterColor = [1.,1.,1.]
cueRadius = 7 #6 deg in Goodbourn & Holcombe
#1920 x 1080 for psyc lab OTC machines
widthPix= 1920 #monitor width in pixels of Agosta  [1280]
heightPix= 1080 #800 #monitor height in pixels [800]
monitorwidth = 57 #38.7 #monitor width in cm [was 38.7]
scrn=0 #0 to use main screen, 1 to use external screen connected to computer
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
print('pixelperdegree=',pixelperdegree)
    
doStaircase = False
checkRefreshEtc = True
if checkRefreshEtc:
    quitFinder = True 
if quitFinder:
    import os
    applescript="\'tell application \"Finder\" to quit\'"
    shellCmd = 'osascript -e '+applescript
    os.system(shellCmd)

#set location of stimuli
#letter size 2.5 deg
SOAms = 300
letterDurMs =   140
#Was 17. 23.6  in Martini E2 and E1b (actually he used 22.2 but that's because he had a crazy refresh rate of 90 Hz = 0
ISIms = SOAms - letterDurMs
letterDurFrames = int( np.floor(letterDurMs / (1000./refreshRate)) )
cueDurFrames = letterDurFrames
ISIframes = int( np.floor(ISIms / (1000./refreshRate)) )
#have set ISIframes and letterDurFrames to integer that corresponds as close as possible to originally intended ms
rateInfo = 'total SOA=' + str(round(  (ISIframes + letterDurFrames)*1000./refreshRate, 2)) + ' or ' + str(ISIframes + letterDurFrames) + ' frames, comprising\n'
rateInfo+=  'ISIframes ='+str(ISIframes)+' or '+str(ISIframes*(1000./refreshRate))+' ms and letterDurFrames ='+str(letterDurFrames)+' or '+str(round( letterDurFrames*(1000./refreshRate), 2))+'ms'
logging.info(rateInfo); print(rateInfo)
logging.info('current working directory is ' + cwd)
trialDurFrames = int( numWordsInStream*(ISIframes+letterDurFrames) ) #trial duration in frames

monitorname = 'testmonitor'
waitBlank = False
mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#relying on  monitorwidth cm (39 for Mitsubishi to do deg calculations) and gamma info in calibratn
mon.setSizePix( (widthPix,heightPix) )
units='deg' #'cm'

def openMyStimWindow(): #make it a function because have to do it several times, want to be sure is identical each time
    myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor
    return myWin
    

trialsPerCondition = 1
defaultNoiseLevel = 0
if not demo:
    allowGUI = False

myWin = openMyStimWindow()

#set up output data file, log file,  copy of program code, and logging
infix = ''
if doStaircase:
    infix = 'staircase_'
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
  dataFile = sys.stdout; logF = sys.stdout
  logging.console.setLevel(logging.ERROR)  #only show this level  messages and higher
logging.console.setLevel(logging.ERROR) #DEBUG means set  console to receive nearly all messges, INFO next level, EXP, DATA, WARNING and ERROR 

if fullscr and not demo and not exportImages:
    runInfo = psychopy.info.RunTimeInfo(
        # if you specify author and version here, it overrides the automatic detection of __author__ and __version__ in your script
        #author='<your name goes here, plus whatever you like, e.g., your lab or contact info>',
        #version="<your experiment version info>",
        win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
        refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
        verbose=True, ## True means report on everything 
        userProcsDetailed=True,  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
        #randomSeed='set:42', ## a way to record, and optionally set, a random seed of type str for making reproducible random sequences
            ## None -> default 
            ## 'time' will use experimentRuntime.epoch as the value for the seed, different value each time the script is run
            ##'set:time' --> seed value is set to experimentRuntime.epoch, and initialized: random.seed(info['randomSeed'])
            ##'set:42' --> set & initialize to str('42'), and will give the same sequence of random.random() for all runs of the script
        )
    print('runInfo='); print(runInfo)
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



def calcStimPos(trial,i):
    if trial['horizVert']:            # bottom,           top
        positions = [ [0,-wordEccentricity], [0,wordEccentricity] ]
    else:                                   #left      ,        right 
        positions = [ [-wordEccentricity,0], [wordEccentricity,0] ]
    return positions[i]

stimuliStream1 = list()
stimuliStream2 = list() #used for second, simultaneous RSVP stream
def calcAndPredrawStimuli(stimList,i,j):
   global stimuliStream1, stimuliStream2
   del stimuliStream1[:]
   del stimuliStream2[:]
   #draw the stimuli that will be used on this trial, the first numWordsInStream of the shuffled list
   stim1string = stimList[ i ]
   stim2string = stimList[ j ]
   print('stim1string=',stim1string, 'stim2string=',stim2string)
   textStimulus1 = visual.TextStim(myWin,text=stim1string,height=ltrHeight,font=myFont,colorSpace='rgb',color=letterColor,alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging)
   textStimulus2 = visual.TextStim(myWin,text=stim2string,height=ltrHeight,font=myFont,colorSpace='rgb',color=letterColor,alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging)

   #textStimulus1.setPos([-wordEccentricity,0]) #left
   stimuliStream1.append(textStimulus1)
   #textStimulus2.setPos([wordEccentricity,0]) #right
   stimuliStream2.append(textStimulus2)
   #end calcAndPredrawStimuli
   
#create click sound for keyboard
clickSound = None
if useSound:
    try:
        clickSound=sound.Sound('406__tictacshutup__click-1-d.wav')
    except: #in case file missing, create inferiro click manually
        logging.warn('Could not load the desired click sound file, instead using manually created inferior click')
        clickSound=sound.Sound('D',octave=4, sampleRate=22050, secs=0.015, bits=8)
badSound = None
if useSound:
    try:
        badSound = sound.Sound('A',octave=5, sampleRate=22050, secs=0.08, bits=8)
    except:
        badSound = None
        print('Could not create an invalid key sound for typing feedback')

if showRefreshMisses:
    fixSizePix = 36 #2.6  #make fixation bigger so flicker more conspicuous
else: fixSizePix = 36
fixColor = [1,1,1]
if exportImages: fixColor= [0,0,0]
fixationPoint= visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=(1,1,1),size=4,units='pix',autoLog=autoLogging)

respPromptStim = visual.TextStim(myWin,pos=(0, -.9),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.5,units='deg',autoLog=autoLogging)
acceptTextStim = visual.TextStim(myWin,pos=(0, -.8),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.05,units='norm',autoLog=autoLogging)
acceptTextStim.setText('Hit ENTER to accept. Backspace to edit')
respStim = visual.TextStim(myWin,pos=(0,0),colorSpace='rgb',color=(1,1,0),alignHoriz='center', alignVert='center',height=1,units='deg',autoLog=autoLogging)
#clickSound, badSound = stringResponse.setupSoundsForResponse()
requireAcceptance = False
nextText = visual.TextStim(myWin,pos=(0, .1),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
NextRemindCountText = visual.TextStim(myWin,pos=(0,.2),colorSpace='rgb',color= (1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
screenshot= False; screenshotDone = False
conditionsList = []
#SETTING THE CONDITIONS
#Implement the fully factorial part of the design by creating every combination of the following conditions
for rightResponseFirst in [False,True]:
      for bothWordsFlipped in [False]:
        for horizVert in [False]:
          for probe in ['both']:
            for indication in [False]: #pre stimulus indicator of locations
                conditionsList.append( {'rightResponseFirst':rightResponseFirst, 'leftStreamFlip':bothWordsFlipped,
                                                       'horizVert':horizVert, 'rightStreamFlip':bothWordsFlipped, 'probe':probe, 'indication':indication} )

trials = data.TrialHandler(conditionsList,trialsPerCondition) #constant stimuli method
trialsForPossibleStaircase = data.TrialHandler(conditionsList,trialsPerCondition) #independent randomization, just to create random trials for staircase phase

logging.info( 'numtrials=' + str(trials.nTotal) + ' and each trialDurFrames='+str(trialDurFrames)+' or '+str(trialDurFrames*(1000./refreshRate))+ \
               ' ms' + '  task=' + task)

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
        
maxNumRespsWanted = 2

#print header for data file
print('experimentPhase\ttrialnum\tsubject\ttask\t',file=dataFile,end='')
print('noisePercent\tleftStreamFlip\trightStreamFlip\trightResponseFirst\tprobe\t',end='',file=dataFile)

for i in range(maxNumRespsWanted):
   dataFile.write('answer'+str(i)+'\t')
   dataFile.write('response'+str(i)+'\t')
   dataFile.write('correct'+str(i)+'\t')
   

#   dataFile.write('responsePosRelative'+str(i)+'\t')
print('timingBlips',file=dataFile)
#end of header
    
def  oneFrameOfStim( n,cue,seq1,seq2,cueDurFrames,letterDurFrames,ISIframes,thisTrial,textStimuliStream1,textStimuliStream2,
                                       noise,proportnNoise,allFieldCoords,numNoiseDots): 
#defining a function to draw each frame of stim.
#seq1 is an array of indices corresponding to the appropriate pre-drawn stimulus, contained in textStimuli
  
  SOAframes = letterDurFrames+ISIframes
  cueFrames = 0 
  stimN = int( np.floor(n/SOAframes) )
  frameOfThisLetter = n % SOAframes #earvery SOAframes, new letter
  timeToShowStim = frameOfThisLetter < letterDurFrames #if true, it's not time for the blank ISI.  it's still time to draw the letter
  
  #print 'n=',n,' SOAframes=',SOAframes, ' letterDurFrames=', letterDurFrames, ' (n % SOAframes) =', (n % SOAframes)  #DEBUGOFF
  thisStimIdx = seq1[stimN] #which letter, from A to Z (1 to 26), should be shown?
  if seq2 is not None:
    thisStim2Idx = seq2[stimN]
  #so that any timing problems occur just as often for every frame, always draw the letter and the cue, but simply draw it in the bgColor when it's not meant to be on
  cue.setLineColor( bgColor )
  if type(cueFrames) not in [tuple,list,np.ndarray]: #scalar. But need collection to do loop based on it
    cueFrames = list([cueFrames])
  for cueFrame in cueFrames: #check whether it's time for any cue
      if n>=cueFrame and n<cueFrame+cueDurFrames:
         cue.setLineColor( cueColor )

  if timeToShowStim: #time to show critical stimulus
    #print('thisStimIdx=',thisStimIdx, ' seq1 = ', seq1, ' stimN=',stimN)
    stimuliStream1[thisStimIdx].setPos( calcStimPos(thisTrial,0) )
    stimuliStream1[thisStimIdx].setColor( letterColor )
    stimuliStream2[thisStim2Idx].setColor( letterColor )
    stimuliStream2[thisStim2Idx].setPos( calcStimPos(thisTrial,1) )
  else: 
    stimuliStream1[thisStimIdx].setColor( bgColor )
    stimuliStream2[thisStim2Idx].setColor( bgColor )
  stimuliStream1[thisStimIdx].flipHoriz = thisTrial['leftStreamFlip']
  stimuliStream2[thisStim2Idx].flipHoriz = thisTrial['rightStreamFlip']
  stimuliStream1[thisStimIdx].draw()
  stimuliStream2[thisStim2Idx].draw()
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
                 
ltrHeight =  0.7 #Martini letters were 2.5deg high
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
numTrialsEachCorrect= np.zeros( maxNumRespsWanted )
numTrialsEachApproxCorrect= np.zeros( maxNumRespsWanted )

def do_RSVP_stim(thisTrial, seq1, seq2, proportnNoise,trialN,thisProbe):
    #relies on global variables:
    #   textStimuli, logging, bgColor
    global framesSaved #because change this variable. Can only change a global variable if you declare it
    cuesPos = [] #will contain the positions in the stream of all the cues (targets)
    cuesPos.append(0)
    cuesPos = np.array(cuesPos)
    noise = None; allFieldCoords=None; numNoiseDots=0
    if proportnNoise > 0: #gtenerating noise is time-consuming, so only do it once per trial. Then shuffle noise coordinates for each letter
        (noise,allFieldCoords,numNoiseDots) = createNoise(proportnNoise,myWin,noiseFieldWidthPix, bgColor)

    preDrawStimToGreasePipeline = list() #I don't know why this works, but without drawing it I previously have had consistent timing blip first time that draw 
    cue.setLineColor(bgColor)
    preDrawStimToGreasePipeline.extend([cue])
    for stim in preDrawStimToGreasePipeline:
        stim.draw()
    myWin.flip(); myWin.flip()
    
    noiseTexture = scipy.random.rand(128,128)*2.0-1
    myNoise1 = visual.GratingStim(myWin, tex=noiseTexture,
             size=(1.5,1), units='deg',
             interpolate=False,
             pos = calcStimPos(thisTrial,0),
             autoLog=False)#this stim changes too much for autologging to be useful
    myNoise2 = visual.GratingStim(myWin, tex=noiseTexture,
             size=(1.5,1), units='deg',
             interpolate=False,
             pos = calcStimPos(thisTrial,1),
             autoLog=False)
    #end preparation of stimuli
    
    core.wait(.1)
    trialClock.reset()
    indicatorPeriodMin = 0.9 #was 0.3
    indicatorPeriodFrames = int(indicatorPeriodMin*refreshRate)
    fixatnPeriodMin = 0.1
    fixatnPeriodFrames = int(   (np.random.rand(1)/2.+fixatnPeriodMin)   *refreshRate)  #random interval between 800ms and 1.3s
    ts = list(); #to store time of each drawing, to check whether skipped frames

    for i in range(fixatnPeriodFrames+20):  #prestim fixation interval
        #if i%4>=2 or demo or exportImages: #flicker fixation on and off at framerate to see when skip frame
        #      fixation.draw()
        #else: fixationBlank.draw()
        fixationPoint.draw()
        myWin.flip()  #end fixation interval
    #myWin.setRecordFrameIntervals(True);  #can't get it to stop detecting superlong frames
    t0 = trialClock.getTime()

    midDelay = 0.5 #0.5
    
    midDelayFrames = int(midDelay *refreshRate)
    #insert a pause to allow the window and python all to finish initialising (avoid initial frame drops)
    for i in range(midDelayFrames):
         myWin.flip()

    indicator1 = visual.TextStim(myWin, text = u"####",pos=(wordEccentricity, 0),height=ltrHeight,colorSpace='rgb',color=letterColor,alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging )
    indicator2 = visual.TextStim(myWin, text = u"####",pos=(-wordEccentricity, 0),height=ltrHeight,colorSpace='rgb',color=letterColor,alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging)
    if thisTrial['indication']: #prior to stimulus appearance
        #if thisProbe=='both':
            for i in range(indicatorPeriodFrames+20):
                indicator1.draw()
                indicator2.draw()
                fixationPoint.draw()
                myWin.flip()
    else:
          indicator3 = visual.TextStim(myWin, text = u"       ",pos=(0, 0),height=ltrHeight,colorSpace='rgb',color=letterColor,alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging )
          for i in range(indicatorPeriodFrames+20):
                indicator3.draw()
                fixationPoint.draw()
                myWin.flip()

    #delay between pre-location indicators
    midDelay2 = 0.0 #0.5
    midDelay2Frames = int(midDelay2 *refreshRate)
    for i in range(midDelay2Frames):
         myWin.flip()
    
    for n in range(trialDurFrames): #this is the loop for this trial's stimulus!
            worked = oneFrameOfStim( n,cue,seq1,seq2,cueDurFrames,letterDurFrames,ISIframes,thisTrial,stimuliStream1,stimuliStream2,
                                                         noise,proportnNoise,allFieldCoords,numNoiseDots ) #draw letter and possibly cue and noise on top
            fixationPoint.draw()
            if exportImages:
                myWin.getMovieFrame(buffer='back') #for later saving
                framesSaved +=1
            myWin.flip()
            t=trialClock.getTime()-t0;  ts.append(t);

    #draw the noise mask
    thisProbe = thisTrial['probe']
    if thisProbe == 'long':
        noiseMaskMin = 0.8 #.2
    else: noiseMaskMin = 0.8 # .2
        
    noiseMaskFrames = int(noiseMaskMin *refreshRate)
    #myPatch1.phase += (1 / 128.0, 0.5 / 128.0)  # increment by (1, 0.5) pixels per frame
    #myPatch2.phase += (1 / 128.0, 0.5 / 128.0)  # increment by (1, 0.5) pixels per frame
    #myPatch1 = visual.TextStim(myWin, text = u"####",pos=(wordEccentricity, 0),height=ltrHeight,colorSpace='rgb',color=letterColor,alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging )
    #myPatch2 = visual.TextStim(myWin, text = u"####",pos=(-wordEccentricity, 0),height=ltrHeight,colorSpace='rgb',color=letterColor,alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging)
    for i in range(noiseMaskFrames):
         myNoise1.draw()
         myNoise2.draw()
         fixationPoint.draw()
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
        respPromptStim.setText('What was the underlined word?',log=False)   
    else: respPromptStim.setText('Error: unexpected task',log=False)
    
    return ts

def handleAndScoreResponse(passThisTrial,response,responseAutopilot,task,correctAnswer):
    #Handle response, calculate whether correct, ########################################
    #responses are actual characters
    #correctAnswer is index into stimSequence
    #autopilot is global variable
    print('response=',response)
    if autopilot or passThisTrial:
        response = responseAutopilot
    correct = 0
    #approxCorrect = 0

    correctAnswer = correctAnswer.upper()
    responseString= ''.join(['%s' % char for char in response])
    responseString= responseString.upper()
    print('correctAnswer=',correctAnswer ,' responseString=',responseString)
    if correctAnswer == responseString:
        correct = 1
    print('correct=',correct)
    
    #responseWordIdx = wordToIdx(responseString,stimList)
    
    print(correctAnswer, '\t', end='', file=dataFile) #answer0
    print(responseString, '\t', end='', file=dataFile) #response0
    print(correct, '\t', end='',file=dataFile) 
    return correct
    #end handleAndScoreResponses
def play_high_tone_correct_low_incorrect(correct, passThisTrial=False):
    highA = sound.Sound('G',octave=5, sampleRate=6000, secs=.3, bits=8)
    low = sound.Sound('F',octave=3, sampleRate=6000, secs=.3, bits=8)
    highA.setVolume(0.9)
    low.setVolume(1.0)
    if correct:
        highA.play()
    elif passThisTrial:
        high= sound.Sound('G',octave=4, sampleRate=2000, secs=.08, bits=8)
        for i in range(2): 
            high.play();  low.play(); 
    else: #incorrect
        low.play()

def doAuthorRecognitionTest(autopilot):
    oneThirtyEight = ['Agatha Christie', 'Aimee Dorr', 'Alex Lumsden', 'Alice Munro', 'Alvin Toffler', 'Amy Tan', 'Andrew Greeley', 'Ann Marie McDonald', 'Anne Rice', 'Arthur C. Clarke', 'Barbara Cartland', 'Brian Bigelow', 'C.S. Lewis', 'Caleb Lim', 'Carl Corter', 'Carla Grinton', 'Carol Berg', 'Carol Shields', 'Carter Anvari', 'Charles Condie', 'Christopher Barr', 'Christopher Moore', 'Dale Blyth', 'Dan Brown', 'Daniel Quinn', 'Danielle Steel', 'David Baldacci', 'David Perry', 'David Singer', 'Dean Koontz', 'Denise Daniels', 'Devon Chang', 'Diana Gabaldon', 'Diane Cuneo', 'Edward Cornell', 'Elizabeth George', 'Elliot Blass', 'Eric Amsel', 'Erica Jong', 'Frances Fincham', 'Frank Gresham', 'Frank Herbert', 'Frank Kiel', 'Frank Manis', 'Gary Beauchamp', 'George R.R. Martin', 'Geraldine Dawson', 'Harrison Boldt', 'Hilda Borko', 'Hugh Lytton', 'Isaac Asimov', 'Jackie Collins', 'James Clavell', 'James Michener', 'James Morgan', 'Janet Evanovich', 'Janice Taught', 'Jean M. Auel', 'Jeffery Eugenides', 'Jennifer Butterworth', 'Jennifer Marshal', 'John Condry', 'John Grisham', 'John Jakes', 'Judith Krantz', 'Judy Blume', 'Julia Connerty', 'K. Warner Schaie', 'Kate Grenville', 'Kate Pullinger', 'Katherine Carpenter', 'Kirby Kavanagh', 'Lauren Benjamin', 'Laurie King', 'Lena Johns', 'Lilly Jack', "Louis L'Amour", 'Lynn Liben', 'M. Scott Peck', 'Maeve Binchy', 'Margaret Atwood', 'Margaret Laurence', 'Margarita Azmitia', 'Mark Elder', 'Mark Strauss', 'Martin Ford', 'Michael Moore', 'Mimi Hall', 'Miriam Sexton', 'Miriam Toews', 'Mordecai Richler', 'Morton Mendelson', 'Naomi Choy', 'Naomi Klein', 'Noam Chomsky', 'Oscar Barbary', 'Patricia Cornwell', 'Peter Rigg', 'Pierre Berton', 'Pricilla Levy', 'Reed Larson', 'Reuben Baron', 'Richard Passman', 'Robert Emery', 'Robert Fulghum', 'Robert Inness', 'Robert J. Sawyer', 'Robert Jordan', 'Robert Ludlum', 'Robert Siegler', 'Robertson Davies', 'Rohinton Mistry', 'Russell Banks', 'Ryan Gilbertson', 'Ryan Morris', 'S.E. Hinton', 'Samuel Paige', 'Scott Paris', 'Sheryl Green', 'Sidney Sheldon', 'Sophia Martin', 'Sophie Kinsella', 'Stephen Coonts', 'Stephen J. Gould', 'Stephen King', 'Stirling King', 'Sue Grafton', 'Susan Kormer', 'Suzanne Clarkson', 'Thomas Bever', 'Timothy Findley', 'Tom Clancy', 'Tracy Tomes', 'Ursula LeGuin', 'V.C. Andrews', 'W. Patrick Dickson', 'Wayne Johnston', 'Wayson Choy']
    oneThirtyFive = oneThirtyEight[0:-3]
    possibleResps = oneThirtyFive #oneThirtyEight #sixteen
    print('num authors = ',len(possibleResps))
    myWin.flip()
    passThisTrial = False
    expStop = False
    bothSides = True
    leftRightFirst = False
    myMouse = event.Mouse() #the mouse absolutely needs to be reset, it seems, otherwise maybe it returns coordinates in wrong units or with wrong scaling?

    expStop,passThisTrial,selected,selectedAutopilot = \
                doAuthorLineup(myWin, bgColor,myMouse, clickSound, badSound, possibleResps, autopilot)
    if autopilot:
        selected = selectedAutopilot
    return expStop,selected

expStop=False



nDoneMain = -1 #change to zero once start main part of experiment
if doStaircase:
    #create the staircase handler
    useQuest = True
    if  useQuest:
        staircase = data.QuestHandler(startVal = 95, 
                              startValSd = 80,
                              stopInterval= 1, #sd of posterior has to be this small or smaller for staircase to stop, unless nTrials reached
                              nTrials = staircaseTrials,
                              #extraInfo = thisInfo,
                              pThreshold = threshCriterion, #0.25,    
                              gamma = 1./26,
                              delta=0.02, #lapse rate, I suppose for Weibull function fit
                              method = 'quantile', #uses the median of the posterior as the final answer
                              stepType = 'log',  #will home in on the 80% threshold. But stepType = 'log' doesn't usually work
                              minVal=1, maxVal = 100
                              )
        print('created QUEST staircase')
    else:
        stepSizesLinear = [.2,.2,.1,.1,.05,.05]
        stepSizesLog = [log(1.4,10),log(1.4,10),log(1.3,10),log(1.3,10),log(1.2,10)]
        staircase = data.StairHandler(startVal = 0.1,
                                  stepType = 'log', #if log, what do I want to multiply it by
                                  stepSizes = stepSizesLog,    #step size to use after each reversal
                                  minVal=0, maxVal=1,
                                  nUp=1, nDown=3,  #will home in on the 80% threshold
                                  nReversals = 2, #The staircase terminates when nTrials have been exceeded, or when both nReversals and nTrials have been exceeded
                                  nTrials=1)
        print('created conventional staircase')
        
    if prefaceStaircaseTrialsN > len(prefaceStaircaseNoise): #repeat array to accommodate desired number of easyStarterTrials
        prefaceStaircaseNoise = np.tile( prefaceStaircaseNoise, ceil( prefaceStaircaseTrialsN/len(prefaceStaircaseNoise) ) )
    prefaceStaircaseNoise = prefaceStaircaseNoise[0:prefaceStaircaseTrialsN]
    
    phasesMsg = ('Doing '+str(prefaceStaircaseTrialsN)+'trials with noisePercent= '+str(prefaceStaircaseNoise)+' then doing a max '+str(staircaseTrials)+'-trial staircase')
    print(phasesMsg); logging.info(phasesMsg)

    #staircaseStarterNoise PHASE OF EXPERIMENT
    corrEachTrial = list() #only needed for easyStaircaseStarterNoise
    staircaseTrialN = -1; mainStaircaseGoing = False
    while (not staircase.finished) and expStop==False: #staircase.thisTrialN < staircase.nTrials
        if staircaseTrialN+1 < len(prefaceStaircaseNoise): #still doing easyStaircaseStarterNoise
            staircaseTrialN += 1
            thisIncrement = prefaceStaircaseNoise[staircaseTrialN]
            noisePercent = 0
        else:
            if staircaseTrialN+1 == len(prefaceStaircaseNoise): #add these non-staircase trials so QUEST knows about them
                mainStaircaseGoing = True
                print('Importing ',corrEachTrial,' and intensities ',prefaceStaircaseNoise)
                staircase.importData(100-prefaceStaircaseNoise, np.array(corrEachTrial))
                printStaircase(staircase, descendingPsycho, briefTrialUpdate=False, printInternalVal=True, alsoLog=False)
            try: #advance the staircase
                printStaircase(staircase, descendingPsycho, briefTrialUpdate=True, printInternalVal=True, alsoLog=False)
                noisePercent = 0 - staircase.next()  #will step through the staircase, based on whether told it (addResponse) got it right or wrong
                thisIncrement = prefaceStaircaseNoise[staircaseTrialN]

                staircaseTrialN += 1
            except StopIteration: #Need this here, even though test for finished above. I can't understand why finished test doesn't accomplish this.
                print('stopping because staircase.next() returned a StopIteration, which it does when it is finished')
                break #break out of the trials loop
        #print('staircaseTrialN=',staircaseTrialN)
        calcAndPredrawStimuli(stimList)

        ts  = \
                                        do_RSVP_stim(cuePos, idxsStream1, idxsStream2, noisePercent/100.,staircaseTrialN)
        numCasesInterframeLong = timingCheckAndLog(ts,staircaseTrialN)
        #expStop,passThisTrial,responses,buttons,responsesAutopilot = \
        #      letterLineupResponse.doLineup(myWin,bgColor,myMouse,clickSound,badSound,possibleResps,showBothSides,sideFirstLeftRightCentral,autopilot) #CAN'T YET HANDLE MORE THAN 2 LINEUPS
        expStop,passThisTrial,responses,responsesAutopilot = \
                stringResponse.collectStringResponse(numRespsWanted,respPromptStim,respStim,acceptTextStim,myWin,clickSound,badSound,
                                                                               requireAcceptance,autopilot,responseDebug=False)
        print(responses)

        if not expStop:
            if mainStaircaseGoing:
                print('staircase\t', end='', file=dataFile)
            else: 
                print('staircase_preface\t', end='', file=dataFile)
             #header start      'trialnum\tsubject\ttask\t'
            print(staircaseTrialN,'\t', end='', file=dataFile) #first thing printed on each line of dataFile
            print(subject,'\t',task,'\t', round(noisePercent,2),'\t', end='', file=dataFile)
            correct,approxCorrect,responsePosRelative= handleAndScoreResponse(
                                                passThisTrial,responses,responseAutopilot,task,sequenceLeft,0,correctAnswerIdx,wordList )
            print(numCasesInterframeLong, file=dataFile) #timingBlips, last thing recorded on each line of dataFile
            core.wait(.06)
            if feedback and useSound:
                play_high_tone_correct_low_incorrect(correct, passThisTrial=False)
            print('staircaseTrialN=', staircaseTrialN,' noisePercent=',round(noisePercent,3),' T1approxCorrect=',T1approxCorrect) #debugON
            corrEachTrial.append(T1approxCorrect)
            if mainStaircaseGoing: 
                staircase.addResponse(T1approxCorrect, intensity = 100-noisePercent) #Add a 1 or 0 to signify a correct/detected or incorrect/missed trial
                #print('Have added an intensity of','{:.3f}'.format(100-noisePercent), 'T1approxCorrect =', T1approxCorrect, ' to staircase') #debugON
    #ENDING STAIRCASE PHASE
    if staircaseTrialN+1 < len(prefaceStaircaseNoise) and (staircaseTrialN>=0): #exp stopped before got through staircase preface trials, so haven't imported yet
        print('Importing ',corrEachTrial,' and intensities ',prefaceStaircaseNoise[0:staircaseTrialN+1])
        staircase.importData(100-prefaceStaircaseNoise[0:staircaseTrialN], np.array(corrEachTrial)) 
    print('framesSaved after staircase=',framesSaved) #debugON

    timeAndDateStr = time.strftime("%H:%M on %d %b %Y", time.localtime())
    msg = ('prefaceStaircase phase' if expStop else '')
    msg += ('ABORTED' if expStop else 'Finished') + ' staircase part of experiment at ' + timeAndDateStr
    logging.info(msg); print(msg)
    printStaircase(staircase, descendingPsycho, briefTrialUpdate=True, printInternalVal=True, alsoLog=False)
    #print('staircase.quantile=',round(staircase.quantile(),2),' sd=',round(staircase.sd(),2))
    threshNoise = round(staircase.quantile(),3)
    if descendingPsycho:
        threshNoise = 100- threshNoise
    threshNoise = max( 0, threshNoise ) #e.g. ff get all trials wrong, posterior peaks at a very negative number
    msg= 'Staircase estimate of threshold = ' + str(threshNoise) + ' with sd=' + str(round(staircase.sd(),2))
    logging.info(msg); print(msg)
    myWin.close()
    #Fit and plot data
    fit = None
    try:
        intensityForCurveFitting = staircase.intensities
        if descendingPsycho: 
            intensityForCurveFitting = 100-staircase.intensities #because fitWeibull assumes curve is ascending
        fit = data.FitWeibull(intensityForCurveFitting, staircase.data, expectedMin=1/26., sems = 1.0/len(staircase.intensities))
    except:
        print("Fit failed.")
    plotDataAndPsychometricCurve(staircase,fit,descendingPsycho,threshCriterion)
    #save figure to file
    pylab.savefig(fileName+'.pdf')
    print('The plot has been saved, as '+fileName+'.pdf')
    pylab.show() #must call this to actually show plot
else: #not staircase
    noisePercent = defaultNoiseLevel
    phasesMsg = 'Experiment will have '+str(trials.nTotal)+' trials. Letters will be drawn with superposed noise of ' + "{:.2%}".format(defaultNoiseLevel)
    print(phasesMsg); logging.info(phasesMsg)
    nDoneMain =0

    while nDoneMain < trials.nTotal and expStop==False: #MAIN EXPERIMENT LOOP
        whichStim0 = np.random.randint(0, len(stimList) )
        whichStim1 = np.random.randint(0, len(stimList) )
        calcAndPredrawStimuli(stimList,whichStim0,whichStim1)
        #stimuliStream1[0].draw; stimuliStream2[0].draw() #debug
        #myWin.flip()
        #event.waitKeys()
        if nDoneMain==0:
            msg='Starting main (non-staircase) part of experiment'
            logging.info(msg); print(msg)
        thisTrial = trials.next() #get a proper (non-staircase) trial
        thisProbe = thisTrial['probe']
        if thisProbe=='both':
          numRespsWanted = 2
        else: numRespsWanted = 1
        
        #Determine which words will be drawn
        idxsStream1 = [0]
        idxsStream2 = [0] 
        ts  =  do_RSVP_stim(thisTrial, idxsStream1, idxsStream2, noisePercent/100.,nDoneMain,thisProbe)
        numCasesInterframeLong = timingCheckAndLog(ts,nDoneMain)
        #call for each response
        myMouse = event.Mouse()
        #alphabet = list(string.ascii_lowercase)
        possibleResps = stimList
        showBothSides = True
        sideFirstLeftRightCentral = 0
        #possibleResps.remove('C'); possibleResps.remove('V
        
        expStop = list(); passThisTrial = list(); responses=list(); responsesAutopilot=list()
        numCharsInResponse = len(stimList[0])
        dL = [None]*numRespsWanted #dummy list for null values
        expStop = copy.deepcopy(dL); responses = copy.deepcopy(dL); responsesAutopilot = copy.deepcopy(dL); passThisTrial=copy.deepcopy(dL)
        if thisProbe == 'both':
            print("Doing both sides")
            responseOrder = [0,1]
            if thisTrial['rightResponseFirst']: #change order of indices depending on rightResponseFirst. response0, answer0 etc refer to which one had to be reported first
                    responseOrder.reverse()
            print('responseOrder=',responseOrder)
            
            for respI in [0,1]:
                side = responseOrder[respI] * 2 -1  #-1 for left/top, 1 for right/bottom
                dev = 2*wordEccentricity * side #put it farther out than stimulus, so participant is sure which is left and which right
                locations = [ 'the left', 'the right',  'the bottom','top' ]
                location     = locations[      thisTrial['horizVert'] * 2  +   responseOrder[respI]      ]
                respPromptString = 'Type the ' + experiment['stimType'] + ' that was on ' +  location
                respPromptStim.setText(respPromptString,log=False)
                if thisTrial['horizVert']:
                    x=0; y=dev
                else:
                    x=dev; y=0
                respStim.setPos([x,y])
                xPrompt =  x*2 if thisTrial['horizVert'] else x*4  #needs to be further out if horizontal to fit the text
                respPromptStim.setPos([xPrompt, y*2])

                #expStop,passThisTrial,responses,buttons,responsesAutopilot = \
                #        letterLineupResponse.doLineup(myWin,bgColor,myMouse,clickSound,badSound,possibleResps,showBothSides,sideFirstLeftRightCentral,autopilot) #CAN'T YET HANDLE MORE THAN 2 LINEUPS
                changeToUpper = False
                expStop[respI],passThisTrial[respI],responses[respI],responsesAutopilot[respI] = stringResponse.collectStringResponse(
                                        numCharsInResponse,x,y,respPromptStim,respStim,acceptTextStim,fixationPoint, (1 if experiment['stimType']=='digit' else 0), myWin,
                                        clickSound,badSound, requireAcceptance,autopilot,changeToUpper,responseDebug=True )
            expStop = np.array(expStop).any(); passThisTrial = np.array(passThisTrial).any()
        
        if not expStop:
                print('main\t', end='', file=dataFile) #first thing printed on each line of dataFile to indicate main part of experiment, not staircase
                print(nDoneMain,'\t', end='', file=dataFile)
                print(subject,'\t',task,'\t', round(noisePercent,3),'\t', end='', file=dataFile)
                print(thisTrial['leftStreamFlip'],'\t', end='', file=dataFile)
                print(thisTrial['rightStreamFlip'],'\t', end='', file=dataFile)
                print(thisTrial['rightResponseFirst'],'\t', end='', file=dataFile)
                print(thisTrial['probe'],'\t', end='', file=dataFile)
                i = 0
                eachCorrect = np.ones(numRespsWanted)*-999

                print("numRespsWanted = ",numRespsWanted, 'getting ready to score response')
                for streami in [0,1]:#range(numRespsWanted): #scored and printed to dataFile in left first, right second order even if collected in different order
                    if streami==0:
                        print("streami=",i)
                        sequenceStream = idxsStream1; correctAnswerIdx = whichStim0
                    else: sequenceStream = idxsStream2; correctAnswerIdx = whichStim1
                    print ("sequenceStream = ",sequenceStream)
                    print ("correctAnswerIdx = ", correctAnswerIdx)
                    print ("stimList = ", stimList, " correctAnswer = stimList[correctAnswerIdx] = ",stimList[correctAnswerIdx])
                    #Find which response is the one to this stream using where
                    respThisStreamI = responseOrder.index(streami)
                    respThisStream = responses[respThisStreamI] 
                    print ("responses = ", responses, 'respThisStream = ', respThisStream)   #responseOrder
                    correct = ( handleAndScoreResponse(passThisTrial,respThisStream,responsesAutopilot,task,stimList[correctAnswerIdx]) )
                    eachCorrect[streami] = correct
        
                print(numCasesInterframeLong, file=dataFile) #timingBlips, last thing recorded on each line of dataFile
                print('correct=',correct,'eachCorrect=',eachCorrect)
                numTrialsCorrect += eachCorrect.all() #so count -1 as 0
                numTrialsEachCorrect += eachCorrect #list numRespsWanted long
                    
                if exportImages:  #catches one frame of response
                     myWin.getMovieFrame() #I cant explain why another getMovieFrame, and core.wait is needed
                     framesSaved +=1; core.wait(.1)
                     myWin.saveMovieFrames('images_sounds_movies/frames.png') #mov not currently supported 
                     expStop=True
                #core.wait(.1)
                if feedback and useSound: 
                    play_high_tone_correct_low_incorrect(correct, passThisTrial=False)
                nDoneMain+=1
                #dataFile.flush(); logging.flush()
                #print('nDoneMain=', nDoneMain,' trials.nTotal=',trials.nTotal) #' trials.thisN=',trials.thisN
                if (trials.nTotal > 6 and nDoneMain > 2 and nDoneMain %
                     ( trials.nTotal*pctCompletedBreak/100. ) ==1):  #dont modulus 0 because then will do it for last trial
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
                core.wait(.1);  time.sleep(.1)
            #end main trials loop
    timeAndDateStr = time.strftime("%H:%M on %d %b %Y", time.localtime())
    msg = 'Finishing at '+timeAndDateStr
    print(msg); logging.info(msg)
    if expStop:
        msg = 'user aborted experiment on keypress with trials done=' + str(nDoneMain) + ' of ' + str(trials.nTotal+1)
        print(msg); logging.error(msg)

    if not doStaircase and (nDoneMain >0):
        print('Of ',nDoneMain,' trials, on ',numTrialsCorrect*1.0/nDoneMain*100., '% of all trials all targets reported exactly correct',sep='')
        for i in range(numRespsWanted):
            print('stream',i,': ',round(numTrialsEachCorrect[i]*1.0/nDoneMain*100.,2), '% correct',sep='')
    dataFile.flush(); logging.flush(); dataFile.close()

    #Do authors task
    myWin.allowGUI =True
    #myWin.close() #Seems to work better if close and open new window (even though units the same), both in terms of dimensions (even though same here!) and double-clicking
    #take a couple extra seconds to close and reopen window unfortunately
    #myWin = visual.Window(fullscr=True,monitor=mon,colorSpace='rgb',color=bgColor,units='deg')

    expStop,selected = doAuthorRecognitionTest(autopilot)
    #save authors file, in json format
    infix = 'authors'
    authorsFileName = os.path.join(dataDir, subject + '_' + timeDateStart + infix + '.json')
    authorsData['selected'] = selected
    authorsData['expStop'] = expStop

    with open(authorsFileName, 'w') as outfile:  
        json.dump(authorsData, outfile)
    
    logging.info("Terminated normally."); print("Terminated normally.")
    core.quit()
