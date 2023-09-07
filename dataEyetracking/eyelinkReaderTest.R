#To get the eyetracking file that this file processes,

#To get eyelinkReader to work, did following:
#library("devtools")
#install_github("alexander-pastukhov/eyelinkReader", dependencies=TRUE)
#Executed usethis::edit_r_environ() to edit the .Renviron file and add the two lines on the eyelinkReader github page:
#EDFAPI_LIB="/Library/Frameworks"
#EDFAPI_INC="/Library/Frameworks/edfapi.framework/Headers"

library(eyelinkReader)
#browseVignettes('eyelinkReader') #Seems to be no vignettes even though github page claims there is

EDF_example <- "../dataEyetracking/results for p14 10.15am aug10.EDF"
EDF_example <- "../dataEyetracking/results for p15 11.30am aug10.EDF"

gaze <- eyelinkReader::read_edf(EDF_example)

if (length(gaze)>0) {
  cat('Success!')
} #Worked 31 Aug 2023

#View(gaze$saccades)

plot(gaze, trial = 1, show_fixations = TRUE, show_saccades = TRUE)

#Need to go through all trials and check largest fixation deviation from center,
# and merge with PsychoPy data file.

#To do this, I could either set up an area of interest maybe, or manually
# import samples with selected attributes
gazeXY <- eyelinkReader::read_edf(EDF_example,
                 import_samples = TRUE,
                 sample_attributes = c('time', 'gx', 'gy'))
#samples table contains the x,y locations
head(gazeXY$samples)

numTrials <- length( unique( gazeXY$samples$trial ) )
cat('number of trials =', numTrials)

#Left eye was recorded, so the samples are in gxL and gyL
head(gazeXY$samples$gxL)

#Work out how to go through all values and detect deviations
meanX <- mean(gazeXY$samples$gxL, na.rm=T)
meanY <- mean(gazeXY$samples$gyL, na.rm=T)

cat('mean gaze location is: (', meanX, meanY, ')')






#Start using tidyverse to calculate things
library(dplyr)

##DO SOME BASIC DESCRIPTIVES ABOUT THE EYETRACKING DATA FOR THIS FILE
numNAs <- gazeXY$samples %>% summarise(na_count = sum(is.na(gxL)))

proportionMissing <- numNAs / nrow(gazeXY$samples)
#maybe the NAs are blinks.  1% of samples for this example EDF file

#Tess' Psychopy logfile says screen is 1470 x 956
scrnWidthHeight = c(1470, 956)
scrnCenter = scrnWidthHeight / 2
cat('scrnCenter = ', scrnCenter)

#In past work, we tended to use exclusion zone of 1 degree
exclusionDeg = 1.0 #if participant's eye is ever more than exclusionDeg away from fixation, Exclusion=1

widthPix = scrnWidthHeight[1]
heightPix = scrnWidthHeight[2]
monitorWidth = 39 #cm
viewdist = 57 #cm
widthScreenDeg =  2*(atan((monitorWidth/2)/viewdist) /pi*180)
pixelsPerDegree = widthPix / widthScreenDeg
exclusionPixels = exclusionDeg * pixelsPerDegree
centralZoneWidthPix = exclusionPixels*2
centralZoneHeightPix = exclusionPixels*2

leftLimitPixel = widthPix/2 - centralZoneWidthPix/2
rightLimitPixel = widthPix/2 + centralZoneWidthPix/2
bottomLimitPixel = heightPix/2 + centralZoneHeightPix/2
topLimitPixel = heightPix/2 - centralZoneHeightPix/2

#Go through every sample for all trials and indicate whether each event falls within the designated limits
cat(paste0("leftLimitPixel=",leftLimitPixel,"\n"))
gazeLocatn <- gazeXY$samples %>% 
      mutate(outOfCentralArea = (gxL < leftLimitPixel) | (gxL > rightLimitPixel)  ) %>%
      mutate(outOfCentralArea = as.numeric(outOfCentralArea)) #Change boolean to 0/1

proportnOutside = gazeLocatn %>% summarise(outOfCentralArea = mean(outOfCentralArea, na.rm=T)) #HAve to ignore NAs, which might be blinks
proportnOutside = proportnOutside$outOfCentralArea
cat("Proportion of samples for this participant that are outside the central zone =", proportnOutside)

perTrial <- gazeLocatn %>% group_by(trial) %>% summarise(outOfCentralArea = mean(outOfCentralArea, na.rm=T))
proportnTrialsOutside = as.numeric( (perTrial$outOfCentralArea > 0) )
cat("Proportion of trials for this participant that are outside the central zone =", mean(proportnTrialsOutside))

#Save as a CSV file the variable of whether in each trial the person's eyes were ever outside the central zone
library(readr)
outputFilename = paste0( EDF_example, ".csv" )
readr::write_excel_csv( perTrial, outputFilename )

#See summariseEyelinkData.R for most of this in a function