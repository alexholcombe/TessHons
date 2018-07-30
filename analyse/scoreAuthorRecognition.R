library('readr')#install.packages('readr')
library(dplyr)
authorScore<- function(js) {
  sel<- js$selected
  #Import the key.
  answersFileWithPath<- file.path("..","inputFiles","authorsAndNonauthors.txt")
  key <-read_tsv(answersFileWithPath)  #read_tsv from tidyverse readr has advantage of not having padding spaces
  
  #Calculate how many authors selected.
  numTested <- length(sel)
  #get scoring key only for those tested, which is the first numTested of the whole key
  keyThis<- key$author[1:numTested]
  selWithAns <- data.frame(sel,keyThis)
  #Use dplyr to select rows where keyThis ==1, then add up number selected
  authors<- selWithAns %>% filter(keyThis==1)
  maxScorePossible <- nrow(authors)
  
  authorsChosen<- sum(authors$sel)
  
  #Calculate how many non-authors selected
  nonAuthors<- selWithAns %>% filter(keyThis==0)
  nonAuthorsChosen <- sum(nonAuthors)
  scoreRaw <- authorsChosen - nonAuthorsChosen
  scorePct <- scoreRaw / maxScorePossible
  return(
    list("authorsRaw" = scoreRaw, "authorsPct" = scorePct, "authorsTotalChosen"=sum(sel))
         )
}