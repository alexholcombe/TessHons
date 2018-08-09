source('scoreAuthorRecognition.R')
library(jsonlite)
library(readr)

#dataDir<-"practiceData"
#datafilename<-"bleo3225_01Aug2018_12-40.txt"

loadOneSession<- function(dataDir,datafilename) {

  fnameroot = substr(datafilename,1,nchar(datafilename)-4)
  datafilename <- file.path(dataDir,datafilename)
  #txtfileWithPath<- file.path(dataDir,paste0(fnameroot,".txt"))
  df <-read_tsv(datafilename)  #read_tsv from tidyverse readr has advantage of not having padding spaces
  apparentSubjectName <- strsplit(fnameroot,split="_")[[1]][1]
  msg<-""
  if (nrow(df)<3) {
    msg <- paste("Not loading",fnameroot,"because nrows(df)=",nrow(df))
    writeLines( msg )
    df <- NULL
  } else { #load
    df$noisePercent<-NULL
    #writeLines(paste("apparentSubjectname=",apparentSubjectName,"fnameroot=",fnameroot))
    subjectName<- df$subject[[1]]
    if (apparentSubjectName != subjectName) {
      stop( paste0("WARNING apparentSubjectName",apparentSubjectName," from filename does not match subjectName in data structure",subjectName) )
    }
    jsonFname<- file.path(dataDir,paste0(fnameroot,"authors.json"))
    if (file.exists( jsonFname )) {
      js<- fromJSON(jsonFname)
    } else {
      print(paste0(jsonFname," not found"))
    }
    
    #Score the author test and add to main data tibble. 
    #Have to drop selected because won't work with dplyr because array.
    scores<- authorScore(js) #("authorsRaw" = scoreRaw, "authorsPct" = authorsPct, "authorsTotalChosen"=sum(sel))
    
    #add author scores to main tibble. authorsRaw, authorsPct, authorsTotalChosen
    for (i in 1:length(names(scores))) {
      df[names(scores)[i]] <- scores[ names(scores)[i] ]
    }
    #add other metadata to main tibble
    js$selected<- NULL #delete this one because list
    js$oneTargetConditions <- NULL #delete this one because list
    for (i in 1:length(names(js))) {
      df[names(js)[i]] <- js[ names(js)[i] ]
    }  #df$language <- js$`What is the first language you learned to read?`
    
    #library(lubridate)
    datetime <- js$datetime
    datetime<- strsplit(datetime,split="[-T]")[[1]]
    month<- datetime[2]
    day<-datetime[3]
    df$month<- month
    df$day <- day
  }
  return (list("tb"= df, "msg"=msg))
  
}