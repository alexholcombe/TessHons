
eyelinkReportSummarise<- function(inputEDFname,widthPix,heightPix,centralZoneWidthPix,centralZoneHeightPix) {
  #inputEDFname is the path and name of an EDF file
  #widthPix is width of screen. Used to calculate center of screen 
  #Eyelink reports eye position in pixels
  if (!file.exists(inputEDFname)) {
    stop( paste0("ERROR no file ",fname," exists") )
  }
  leftLimitPixel = widthPix/2 - centralZoneWidthPix/2
  rightLimitPixel = widthPix/2 + centralZoneWidthPix/2
  bottomLimitPixel = heightPix/2 + centralZoneHeightPix/2
  topLimitPixel = heightPix/2 - centralZoneHeightPix/2
  
  gaze <- eyelinkReader::read_edf(inputEDFname,
                                  import_samples = TRUE,
                                  sample_attributes = c('time', 'gx', 'gy'))
  
  if (length(gaze)==0) {
    cat('Failure to read EDF file with eyelinkReader!')
  }
  # gaze$samples contains the x,y locations
  
  #Go through every sample for all trials and indicate whether each event falls within the designated limits
  gazeLocatn <- gaze$samples %>% 
    mutate(outOfCentralArea = (gxL < leftLimitPixel) | (gxL > rightLimitPixel)  ) %>%
    mutate(outOfCentralArea = as.numeric(outOfCentralArea)) #Change boolean to 0/1
  
  proportnOutside = gazeLocatn %>% summarise(outOfCentralArea = mean(outOfCentralArea, na.rm=T)) #HAve to ignore NAs, which might be blinks
  proportnOutside = proportnOutside$outOfCentralArea
  #cat("Proportion of samples for this participant that are outside the central zone =", proportnOutside)
  
  eachTrial <- gazeLocatn %>% group_by(trial) %>% summarise(outOfCentralArea = mean(outOfCentralArea, na.rm=T))
  proportnTrialsOutside = as.numeric( (eachTrial$outOfCentralArea > 0) )
  msg = paste("Proportion of trials for this participant that are outside the central zone =", mean(proportnTrialsOutside))
  print(msg)
  
  #Save as a CSV file the variable of whether in each trial the person's eyes were ever outside the central zone
  library(readr)
  outputFilename = paste0( inputEDFname, ".csv" )
  readr::write_excel_csv( eachTrial, outputFilename )
  
  return( eachTrial )
}


TESTME = TRUE #Unfortunately no equivalent in R of python __main__. Would have to use testthat I guess

if (TESTME) {

  inputEDFname <- "../dataEyetracking/results for p14 10.15am aug10.EDF"
  widthPix = 1470
  heightPix = 956
  centralZoneHeightPix = 77.8
  centralZoneWidthPix = 77.8

  eachT <- eyelinkReportSummarise(inputEDFname, widthPix,heightPix,centralZoneWidthPix,centralZoneHeightPix)

}