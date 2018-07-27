#read in authors, and also non-authors, then combine the list and put in alphabetical order
import os

def readNamesFromFile(file):
    authors = list()
    f = open(file)
    eachLine = f.readlines()
    numStimsWanted = 70
    if len(eachLine) < numStimsWanted:
        print("ERROR file doesn't have as many lines as expected, there are ", len(eachLine), "wanted more.")
    for l in range(1,numStimsWanted):#skip first, header line, therefore start with line 1
        line = eachLine[l]
        values = line.split() #splits on tabs or whitespaces and trims leading,following including newlines
        #print('values=',values)
        author = ' '.join(values)  #values[0]
        authors.append( author )
    return authors
    
stimDir = os.path.join(os.pardir,'inputFiles') #parent directory
#stimDir='../inputFiles'
print('is directory=',os.path.isdir(stimDir))
stimFile = os.path.join(stimDir,"authors.txt")
print('stimFile=',stimFile)
authors= readNamesFromFile(stimFile)
print(authors)

stimFile = os.path.join(stimDir,"nonauthors.txt")
nonauthors= readNamesFromFile(stimFile)
print(nonauthors)
print('Got',len(authors),'authors and',len(nonauthors),'nonauthors')

#Combine the lists
both = authors + nonauthors
print('both =',both)

#Alphabetise indices
#Simple python way not sufficient because need to save indices
#alphabetized = sorted(both, key=str.lower)  #put in lower case, otherwise will sort by uppercase first
idxs = sorted(range(len(both)), key=lambda k: both[k])
print('hopefully idxs used for alphabetical sorting=',idxs)

alphabetized = [both[w] for w in idxs]
print('alphabetized=',alphabetized)

#print('alphabetized=',alphabetized)

#Determine which are authors and which are not, for scoring. But this can be done much later
numAuthors = len(authors)
numNonauthors = len(nonauthors)
#For each index in idxs, classify as author or not
isAuthor = list()
for idx in idxs:
    if idx < numAuthors:
        isAuthor.append(1)
    else:
        isAuthor.append(0)

out = os.path.join(stimDir,'authorsAndNonauthors.txt')
thefile = open(out, 'w')
print>>thefile, 'name\tauthor'
for i in xrange( len(alphabetized) ):
  print>>thefile, alphabetized[i], '\t', isAuthor[i]