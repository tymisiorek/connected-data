from openai import OpenAI
import json
import csv

client = OpenAI()
#Using json files instead of txt for input
OCRPath = "C:\\Users\\tykun\\OneDrive\\Documents\\SchoolDocs\\VSCodeProjects\\yellowBookStuff\\fileReads\\standardizedSegmentResults75.json"

def convertToString(path): 
    with open(path, 'r') as file:
        fullText = json.load(file)
    return fullText

processedPath =  convertToString(OCRPath)

# Assuming processedPath is a list. Iterate through the list (each element is a page of OCR)
for text in processedPath:
    processedPathStr = str(text)
    # print(processedPathStr)

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
        ],
        temperature = 0.0
    )

    # print("Finished!\n\n\n\n")
    # print(completion.choices[0].message.content)
    response = completion.choices[0].message.content
    # print("\n\n\n\n\n", type(response), "\n\n\n")

    #Write the result into a csv. It doesn't open correctly in excel right now, but works correctly opened with notepad. The result goes into the project folder
    csvPath = "apiGeneratedResponse75pages.csv"
    with open(csvPath, 'a', newline = '') as csvfile:
        write = csv.writer(csvfile, quoting = csv.QUOTE_NONE, escapechar=' ')
        write.writerow(['SEP=|'])
        # print("This is the value of response: \n\n\n")
        # print(response,"\n\n\n")
        write.writerow([response])

print("\n\n\n Finished! \n\n\n")
