from openai import OpenAI
import json
import csv
import re
from lcpartition import *



client = OpenAI()
#Currently using json instead of text files for the input
OCRPath = "C:\\Users\\tykun\\OneDrive\\Documents\\SchoolDocs\\VSCodeProjects\\yellowBookStuff\\fileReads\\standardizedSegmentResultsInit.json"
# OCRPath = "C:\\Users\\tykun\\OneDrive\\Documents\\SchoolDocs\\VSCodeProjects\\yellowBookStuff\\fileReads\\newFormatTestJ.json"



filePath = "C:\\Users\\tykun\\OneDrive\\Documents\\SchoolDocs\\VSCodeProjects\\yellowBookStuff\\fileReads\\standardizedSegmentResultsInit.json"
titleIndices = []
blockedList = []
nlp = spacy.load("en_core_web_sm")
rawData = pathToString(filePath)
singlePage = rawData[8]
singlePage = removeEmptyElements(singlePage)
singlePage = removeEmptyElements(singlePage)
titleIndices = tagNames(singlePage, titleIndices)
titleIndices = breakChunks(singlePage, titleIndices)
titleIndices = breakChunks(singlePage, titleIndices)
titleIndices = breakDoubleNames(singlePage, titleIndices)
titleIndices = breakTwoLineDoubleName(singlePage, titleIndices)
titleIndices = connectSingleLines(singlePage, titleIndices)
# response = ""
fullresponse = ""



#Converts to json to string
def convertToString(path): 
    with open(path, 'r') as file:
        fullText = json.load(file)
    return fullText


def listToString(list):
    str = ""
    for x in list:
        str += '\n' + x
    return str


#This file does not run in a loop and clean every page in the text, it only takes one. Used for testing.
processedPath =  convertToString(OCRPath)
processedPathStr = str(processedPath[1])
processedPathStr = re.sub(r"['\"]", "", processedPathStr)
print("this is the string we are using right now: ", processedPathStr)

startIndex = 0
endIndex = 1

#Right now, not putting email or phone number as a column because they aren't super useful, but it can be quickly added to prompt
for i in range(len(titleIndices)-1):
    # if singlePage[titleIndices[endIndex+2]] is not None:
    #     textBlockList = singlePage[titleIndices[startIndex]:titleIndices[endIndex+1]]
    # else:
    textBlockList = singlePage[titleIndices[startIndex]:titleIndices[endIndex]]

    #convert to string
    textBlock = listToString(textBlockList)

    # print(textBlock)
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are part of a data processing pipeline. Your task is to parse the data into a tabular format, with no additional annotations or explanations, or it will break the process. Remember, you are only returning tabular information."},
        {"role": "user", "content": "Extract all names of people (sometimes this is \"Vacant\"), then their current job title (generally Trustee, President, Dean, Chair, Provost, Director, Chairman, Executive Committee Member, Manager, etc.) including prefixes (vice, assistant, associate, senior, executive, etc.), suffixes (MD, PhD, Jr, etc.), "},
        {"role": "user", "content": "Organize the above information into a tab separated table (tsv table) with the following columns:"},
        {"role": "user", "content": "| Name | Current Title | Education | Other Affiliation | Current University |"},
        {"role": "user", "content": "Create a new line for each name that is extracted. If there are multiple elements to put into one column, separate them by commas. If there is no elements to put into a column, put: N/A."},
        {"role": "user", "content": "If there is a line of text that contains the phrase, \"Education: \", you can NEVER leave that information out of the table. It's critical to ensure that the education column is rarely empty, as missing education information will disrupt the pipeline."},
        {"role": "user", "content": "If there is a line of text that contains the phrase, \"Affiliation: \" or \"Career:\", then ALWAYS put whatever is listed for that person's affiliation in the table under the column Other Affiliation. Double check for lines containing affiliation, as one person's career/affiliation can span multiple elements. Ensure that no information for current affiliations is missed, even if it spans multiple lines."},
        {"role": "user", "content": "Make sure to look through the entire text and don't leave any information out. Any incorrect or missing information WILL break the pipeline. Please double check that all of the above instructions have been fulfilled."},
        {"role": "user", "content": "You will be continuously given 3 blocks of text, each block containing the information associated with one board member. With each new prompt, the first block will be identical to the last block from the previous prompt. This is to check for information being incorrectly distributed about the blocks. Do not list the same name twice."},
        # {"role": "user", "content": "After the first prompt of the loop, stop printing the header."},
        {"role": "assistant", "content": "Here is the organized data in the format you specified:\"\"\" "},
        {"role": "assistant", "content": textBlock},
        {"role": "assistant", "content": "\"\"\" "}
        # {"role": "assistant", "content": "reset"} #we may not want to keep this
    ],
    temperature = 0.0
    )
    # print("case 2")

    startIndex+=1
    endIndex+=1

    # print(completion.choices[0].message.content)
    response = completion.choices[0].message.content
    fullresponse += response
    print("\n", response)
    # print("this is full response: \n", fullresponse)





# print(type(completion))
# print(completion.choices[0].message)
# print("Finished!\n\n\n\n")
print(completion.choices[0].message.content)
response = completion.choices[0].message.content
print("\n\n\n\n\n", response)

#Write the result into a csv. It doesn't open correctly in excel right now, but works correctly opened with notepad. The result goes into the project folder
csvPath = "GPTFormattedBlocked.csv"
with open(csvPath, 'w', newline = '') as csvfile:
    write = csv.writer(csvfile, quoting = csv.QUOTE_NONE, escapechar=' ')
    write.writerow(['SEP=|'])
    # print("This is the value of response: \n\n\n")
    # print(response,"\n\n\n")
    write.writerow([fullresponse])



# print(f"Generated response saved to {csv_file_path}")
print("Finished!")