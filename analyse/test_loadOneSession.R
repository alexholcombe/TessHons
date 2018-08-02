#test_loadOneSession.R

rawDataPath<- file.path("practiceData")
files <- dir(path=rawDataPath,pattern='.txt')  #find all data files in this directory

loadOneSession(rawDataPath,files[1])
