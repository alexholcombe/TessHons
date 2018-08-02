#raw data path containing .py,.log,.json file for each subject

library(jsonlite)

source(file.path("loadOneSession.R"))

readInAllFiles <- function(rawDataPath) {
  
  files <- dir(path=rawDataPath,pattern='.txt')  #find all data files in this directory
  for (i in 1:length(files)) { #read in each file
    fileThis<- files[i] #file.path(rawDataPath,files[i])
    tibbleThis=tryCatch(
      loadOneSession(rawDataPath,fileThis),
      error=function(e) {
        stop( paste0("ERROR loading the file ",fileThis," :",e) )
      } )

    tibbleThis$file <- files[i]
    if (i==1) {
      tbAll<-tibbleThis
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
  return(tbAll)
}
