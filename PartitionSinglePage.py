import spacy
import json
import nltk
from spacy import displacy
import re



'''
Currently this cannot account for the situation where there's a title that starts on the line above a name, but also leaks into the line with the name
SpaCy doesn't detect every name, so this ends up with blocks of multiple names somtimes
'''

filePath = "C:\\Users\\tykun\\OneDrive\\Documents\\SchoolDocs\\VSCodeProjects\\yellowBookStuff\\fileReads\\standardizedSegmentResultsInit.json"
titleIndices = []


def pathToString(filePath):
    with open(filePath, 'r') as file:
        fullText = json.load(file)
    return fullText


def removeEmptyElements(page):
    page = list(filter(None, page))
    page = list(filter(lambda x: x.strip(), page))
    return page


#Uses spacy to detect the named entities on the page and labels them
def tagNames(rawData):
    lineNumber = 0
    for text in rawData:
        doc = nlp(text)
        for ent in doc.ents:
            isPerson = str(ent.label_) == "PERSON"
            isGPE = any(ent.label_ == "GPE" for ent in doc.ents)
            #Will have to add a different way to handle the word dean, just a temporary solution
            isDean = str(ent.text) == "Dean"
            noKeywords = all(keyword not in text for keyword in ["Education", "Affiliation", "Career:"])
            #Assign the next line, ensure that it's not out of bound. Also check two lines ahead
            #-------------------------------------------------------------------------------
            if lineNumber < len(rawData) - 1:
                nextLine = rawData[lineNumber+1]
            else:
                nextLine = rawData[0]

            if lineNumber < len(rawData) - 2:
                twoLines = rawData[lineNumber+2]
            else:
                twoLines = rawData[0]
            #-------------------------------------------------------------------------------
            
            noTel = "tel:" not in nextLine.lower() and "tel" not in twoLines.lower()

            if isPerson and noKeywords and not isDean and noTel:
                checkStructure(text, rawData[lineNumber-1], str(ent.text), lineNumber, rawData)

        lineNumber+=1 


#Given a line of text, check to see what the name/title layout is
def checkStructure(currentLine, previousLine, name, lineNumber, rawData):
    nameStartIndex = currentLine.index(name)
    nameEndIndex = nameStartIndex + len(name)
    if(currentLine[nameEndIndex:] != "" and currentLine[:nameStartIndex] != ""):
        #Check for case where the title is above the name and on the same line. This is not a perfect check, but it should overcount instead of undercount
        if(":" not in previousLine):
            title = previousLine, currentLine[:nameStartIndex].replace("Dr.", "")
            titleIndices.append(lineNumber-1)
        else:
            title = currentLine[:nameStartIndex].replace("Dr.", "")
            titleIndices.append(lineNumber)
        # print("This is the current line: ", currentLine)
        # print("First case title: ", title)
        # print("\n\n")
    elif(currentLine[:nameStartIndex] == "" and currentLine[-2].isdigit()):
        title = previousLine
        titleIndices.append(lineNumber-1)
        # print("This is the current line: ", currentLine)
        # print("Second case title: ", title)
        # print("\n\n")
    elif(currentLine[:nameStartIndex] == "" and currentLine[nameEndIndex:] != ""):
        title = currentLine[nameEndIndex:]
        titleIndices.append(lineNumber)
        # print("This is the current line: ", currentLine)
        # print("Third case title: ", title)
        # print("\n\n")
    return titleIndices


def formatText(page, titleIndices):
    fileName = "structuredDataPage1.txt"
    lineCounter = 0
    with open(fileName, 'w') as file:
        for line in page:
            if(lineCounter in titleIndices):
                file.write('\n\n')
            # print(line)
            file.write(str(line))
            file.write('\n')
            lineCounter+=1



def printFormattedText(page, titleIndices):
    lineCounter = 0
    for line in page:
        if(lineCounter in titleIndices):
            print("\n\n")
        print(line)
        lineCounter+=1


#For getting the distance between two title indices
def distance(current, previous):
    distance = abs(int(current) - int(previous))
    # print("this is the distance: ", distance)
    return distance


#Check a name block and return true if a substring appears more than once in that block
def doubleOccurrence(list, substring):
    occurrences = 0
    for line in list:
        if substring in line:
            occurrences += 1
    # print(occurrences)
    return occurrences > 1


#Finds the first occurrence of a substring in a name block
def findFirstOccurrence(list, substring):
    lineNumber = 0
    # print("this is list: ", list)
    for line in list:
        # print("Thi is line: ", line, "    and this is substring: ", substring)
        if(substring in line):
            return lineNumber
        lineNumber += 1
    return lineNumber


#Takes two substrings, eg: Education: and Email:, and returns which one appears first
def appearsFirst(list, substring1, substring2):
    for line in list:
        if(substring1 in line):
            return substring1
        elif(substring2 in line):
            return substring2
    return ""


def breakChunks(page, titleIndices):
    numTitles = len(titleIndices)
    startIndex = 0
    endIndex = 1
    while(endIndex < len(titleIndices)):

        if(startIndex < numTitles and distance(titleIndices[startIndex], titleIndices[endIndex]) > 3):
            nameBlock = page[titleIndices[startIndex]:titleIndices[endIndex]]
            firstAppeared = appearsFirst(nameBlock, "Education:", "E-mail:")

            if(doubleOccurrence(nameBlock, "Education:") and firstAppeared == "E-mail:"):
                #play around with this plus 1
                indexSplit = findFirstOccurrence(nameBlock, "Education:") + titleIndices[startIndex] + 1
                titleIndices.insert(startIndex+1, indexSplit)
                startIndex += 1
                endIndex += 1
            elif(doubleOccurrence(nameBlock, "E-mail:") and firstAppeared == "Education:"):
                indexSplit = findFirstOccurrence(nameBlock, "E-mail:") + titleIndices[startIndex] + 1
                titleIndices.insert(startIndex+1, indexSplit)
                startIndex += 1
                endIndex += 1
            elif(doubleOccurrence(nameBlock, "E-mail:") and firstAppeared == "E-mail:"):
                indexSplit = findFirstOccurrence(nameBlock, "E-mail:") + titleIndices[startIndex] + 1
                titleIndices.insert(startIndex+1, indexSplit)
                startIndex += 1
                endIndex += 1
            elif(doubleOccurrence(nameBlock, "Education:") and firstAppeared == "Education:"):
                indexSplit = findFirstOccurrence(nameBlock, "E-mail:") + titleIndices[startIndex] + 1
                titleIndices.insert(startIndex+1, indexSplit)
                startIndex += 1
                endIndex += 1

        startIndex+=1
        endIndex+=1
    return titleIndices






# -----------------  Testing Methods  ----------------- #

nlp = spacy.load("en_core_web_sm")
rawData = pathToString(filePath)
singlePage = rawData[1]
singlePage = removeEmptyElements(singlePage)
tagNames(singlePage)
print("This is title indices before: ", titleIndices)
titleIndices = breakChunks(singlePage, titleIndices)
titleIndices = breakChunks(singlePage, titleIndices)
print("This is title indices after: ", titleIndices)
formatText(singlePage, titleIndices)
print("\n\n\n\n")
printFormattedText(singlePage, titleIndices)

print("\n\n\n")
print("Finished!")