#raw data path containing .py,.log,.json file for each subject

library(jsonlite)

source(file.path("loadOneSession.R"))

readInAllFiles <- function(rawDataPath) {
  files <- dir(path=rawDataPath,pattern='.txt')  #find all data files in this directory
  #Create list for warning messages etc.
  msgs <- vector("list", length(files)) #initialize list because appending is very very slow
  len<-length(msgs)
  firstFileRead <- FALSE
  tbAll<-tibble()
  for (i in 1:length(files)) { #read in each file
    fileThis<- files[i] #file.path(rawDataPath,files[i])
    tibbleAndMsg<- tryCatch(
      loadOneSession(rawDataPath,fileThis),
      error=function(e) {
        stop( paste0("ERROR loading the file ",fileThis," :",e) )
      } )
    msgs[[i]] <- tibbleAndMsg$msg
    if (!is.null(tibbleAndMsg$tb)) { #loaded something
      tibbleThis <- tibbleAndMsg$tb
      tibbleThis$file <- files[i]
      if (!firstFileRead) {
        tbAll<-tibbleThis
        firstFileRead<-TRUE
      } else { #check for new columns, then merge
        newCols <- setdiff( colnames(tibbleThis),prevColNames )
        oldColsNotInNew <- setdiff( prevColNames,colnames(tibbleThis) )
        if (length(newCols) >0) {
          writeLines( paste("newCols are",newCols))
          for (n in 1:length(newCols)) { #add newCol to old data.frame with dummy value
            tbAll[newCols[n]] <- -999
            #writeLines(paste("Added new column",newCols[n],"to tbAll"))
          }
        }
        if (length(oldColsNotInNew)>0) {
          writeLines( "oldColsNotInNew are'"); cat(oldColsNotInNew);
          #writeLines(paste("'rawDataPath=",rawDataPath))
          for (n in 1:length(oldColsNotInNew)) #add old col to new data.frame that doesn't have it
            tibbleThis[oldColsNotInNew[n]] <- -999	
        }
        tryCatch( tbAll<-rbind(tbAll,tibbleThis), #if fail to bind new with old,
                  error=function(e)
                  { print ("ERROR merging"); print(e)
                    colnamesNew <- paste(colnames(tibbleThis),collapse=",")
                    colnamesOld <- paste(colnames(tbAll),collapse=",")
                    diff= setdiff(colnames(tibbleThis),colnames(tbAll))
                    if (length(diff) >0) {
                      writeLines( paste('colnamesNew=',colnamesNew,'\n colnamesOld=', colnamesOld))
                      writeLines('difference is'); writelines( diff )
                    } else {
                      writeLines( paste('colnames=',colnamesNew,' no difference between the two files'))    
                    }    
                    quitQUIT
                  } ) #end tryCatch
        # if (!("knownMachinesForPilot.index(networkMachineName)" %in% names(tibbleThis))) {
        #   #only included if it was a known machine on a pilot day
        #   tibbleThis["knownMachine"] <- "NA"
        # } else {  #give it a name that is not impossible"
        #   tibbleThis["knownMachine"] <- 
        #     tibbleThis["knownMachinesForPilot.index(networkMachineName)"]
        #   tibbleThis["knownMachinesForPilot.index(networkMachineName)"] <- NULL #delete
        # }
      }
      prevColNames<- colnames(tibbleThis)
    } 
  } #looping through files
  #Print out messages, because can get lost in sea of stupid read.tsv output about column parsing
  #msgs<<-msgs
  for (i in 1:length(files)) {
    #writeLines(as.character(i)) #debug
    #writeLines(paste(len,as.character(length(msgs))))
    if (!is.null(msgs[[i]]) & (msgs[[i]]!='')) {
      writeLines(msgs[[i]])
    }
  }
  return(tbAll)
}
