loadOneSession<- function(dataDir,fname) {
  js<- fromJSON(file.path(dataDir,fname,".json"))
  
  fileWithPath<- file.path(dataDir,fname,".txt")
  df <-read_tsv(fileWithPath)  #read_tsv from tidyverse readr has advantage of not having padding spaces
  df$noisePercent<-NULL
  
  #score the author test, add to main data tibble. 
  #Have to drop selected because won't work with dplyr because array.
  scores<- authorScore(df) #("authorsRaw" = scoreRaw, "authorsPct" = authorsPct, "authorsTotalChosen"=sum(sel))
  df$authorsPct <- scores$authorsPct
  df$authorsTotalChosen <- scores$authorsTotalChosen
  
  #add other metadata to tibble
  df$language <- js$`What is the first language you learned to read?`
  df$networkMachineN
  
  library(lubridate)
  #x <- c("Apr-13", "May-14")
  ##add DD as 01
  #x <- paste("01",x,sep="-")
  ##result
  #dmy(x)
  
}