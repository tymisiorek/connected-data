from openai import OpenAI
import json
import csv
import re



client = OpenAI()
#Currently using json instead of text files for the input
OCRPath = "C:\\Users\\tykun\\OneDrive\\Documents\\SchoolDocs\\VSCodeProjects\\yellowBookStuff\\fileReads\\standardizedSegmentResultsJ.json"

#Converts to json to string
def convertToString(path): 
    with open(path, 'r') as file:
        fullText = json.load(file)
    return fullText

#This file does not run in a loop and clean every page in the text, it only takes one. Used for testing.
processedPath =  convertToString(OCRPath)
processedPathStr = str(processedPath[9])
print("this is the string we are using right now: ", processedPathStr)

#Right now, not putting email or phone number as a column because they aren't super useful, but it can be quickly added to prompt
completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    # {"role": "system", "content": "You are cleaning and organizing data from a Python list."},
    # {"role": "system", "content": "You will be provided with unstructured data, and your task is to parse it into CSV format."},
    {"role": "system", "content": "You are part of a data processing pipeline. Your task is to parse the data into a tabular format, with no additional annotations or explanations, or it will break the process. Remember, you are only returning tabular information."},
    {"role": "user", "content": "Extract the important entities mentioned in the text below. First, extract all names of people, then their current job title (generally Trustee), any education/degree they've recieved, (Anything following the phrase, \"Education:\") finally, current affiliation/positions they hold at other companies "},
    {"role": "user", "content": "Organize the above information into a table with the following format: "},
    {"role": "user", "content": "| Name | Current Title | Education | Other Affiliation |"},
    # {"role": "user", "content": ": Name : Current Job Title : Education : Past Jobs :"},
    {"role": "user", "content": "Create a new line for each name that is extracted. If there are multiple elements to put into one column, separate them by commas. If there is no elements to put into a column, put: N/A."},
    {"role": "user", "content": "If there is a line of text that contains the line, \"Education:\", then always put whatever is listed for that person's education in the table. Double check for lines containing education. Most of the time, this column should not be empty."},
    {"role": "user", "content": "If there is a line of text that contains the line, \"Affiliation:\", then always put whatever is listed for that person's affiliation in the table under the column Other Affiliation. Double check for lines containing affiliation. This column is not often empty."},
    {"role": "assistant", "content": "Here is the organized data in the format you specified:\"\"\" "},
    {"role": "assistant", "content": processedPathStr},
    {"role": "assistant", "content": "\"\"\" "}
    # {"role": "assistant", "content": "reset"} #we may not want to keep this
  ],
  temperature = 0.0
)



# print(type(completion))
# print(completion.choices[0].message)
# print("Finished!\n\n\n\n")
print(completion.choices[0].message.content)
response = completion.choices[0].message.content
print("\n\n\n\n\n", response)

#Write the result into a csv. It doesn't open correctly in excel right now, but works correctly opened with notepad. The result goes into the project folder
csvPath = "apiGeneratedResponseSingle.csv"
with open(csvPath, 'w', newline = '') as csvfile:
    write = csv.writer(csvfile, quoting = csv.QUOTE_NONE, escapechar=' ')
    write.writerow(['SEP=|'])
    # print("This is the value of response: \n\n\n")
    # print(response,"\n\n\n")
    write.writerow([response])



# print(f"Generated response saved to {csv_file_path}")
print("Finished!")