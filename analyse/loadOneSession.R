source('scoreAuthorRecognition.R')
library(jsonlite)
library(readr)
loadOneSession<- function(dataDir,fname) {

  js<- fromJSON(file.path(dataDir,paste0(fname,"authors.json")))
  
  txtfileWithPath<- file.path(dataDir,paste0(fname,".txt"))
  df <-read_tsv(txtfileWithPath)  #read_tsv from tidyverse readr has advantage of not having padding spaces
  df$noisePercent<-NULL
  
  #score the author test, add to main data tibble. 
  #Have to drop selected because won't work with dplyr because array.
  scores<- authorScore(js) #("authorsRaw" = scoreRaw, "authorsPct" = authorsPct, "authorsTotalChosen"=sum(sel))
  #add author scores to main tibble. authorsRaw, authorsPct, authorsTotalChosen
  for (i in length(names(scores))) {
    df[names(scores)[i]] <- js[names(scores)[i]]
  }
  #add other metadata to main tibble
  for (i in length(names(js)) {
    df[names(js)[i]] <- js[names(js)[i]]
  }  #df$language <- js$`What is the first language you learned to read?`

  library(lubridate)
  #x <- c("Apr-13", "May-14")
  ##add DD as 01
  #x <- paste("01",x,sep="-")
  ##result
  #dmy(x)
  
}