import string

ltrList =  list(string.ascii_lowercase)
toRemove = []#['d','b','l','i','o','q','p','v','w','x'] #because symmetrical, see rotatedLettersAndSymbols.jpg 
for ltr in toRemove:
    ltrList.remove(ltr)

stimList = list()
for i in ltrList:
    for j in ltrList:
        for k in ltrList:
            if i != j and i != k and j != k:
                # convert i, j, and k to their corresponding ASCII codes and add 97
                # to get the lowercase letters a-z
                trigram = [i, j, k]
                stimList.append(trigram)
print(stimList)

#import string, copy
#ltrList =  list(string.ascii_lowercase)
#toRemove = []#['d','b','l','i','o','q','p','v','w','x'] #because symmetrical, see rotatedLettersAndSymbols.jpg 
#for ltr in toRemove:
#    ltrList.remove(ltr)
#Create full list of trigrams by going through all letters for the first position, then adding any letter but that one for second position,
#  and any letter but the previous two for the third position
#for ltrOne in ltrList:
#    #remove ltrOne to create the pool of letters for second position
#    secondLtrList = copy.deepcopy(ltrList)
#    secondLtrList.remove(ltrOne)
#    for ltrTwo in secondLtrList:
#        thirdLtrList = copy.deepcopy(secondLtrList)
#        thirdLtrList.remove(ltrTwo)
#        for ltrThree in thirdLtrList:
#            trigram = [ltrOne,ltrTwo,ltrThree]
#            print(trigram)