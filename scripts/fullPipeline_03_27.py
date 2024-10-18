# --------- Imports --------- #
import os
import json
import csv
import pandas as pd
import numpy as np
import pdf2image
from io import StringIO
import cv2
import pytesseract
from openai import OpenAI
from PIL import Image
from IPython.display import display
from matplotlib import pyplot as plt
from lcocr import *
from lcpartition import *
import spacy
from spacy import displacy
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain.chains import create_extraction_chain
# --------------------------- #

textList = []
path2scans = 'C:\\Users\\tykun\\OneDrive\\Documents\\SchoolDocs\\SecondYearStuff\\ConnectedData\\BoardScans'
path2connectedleaders = 'C:\\Users\\tykun\\OneDrive\\Documents\\SchoolDocs\\SecondYearStuff\\ConnectedData\\BoardScans'

scanConverted = pdf2image.convert_from_path(os.path.join(path2connectedleaders, 'uniWinterRandom.pdf'), poppler_path = r'C:\\Program Files (x86)\\poppler-24.02.0\\Library\\bin')
llm = OllamaFunctions(model="mistral", temperature=0, cache=False)

for x in scanConverted:
    img = np.array(x)
    point_list, rotated_orig_Image = rotate_image(img)
    unrotatedImage, firstWhiteUnRotated, lastWhiteUnRotated = straighten_image(point_list, rotated_orig_Image)
    split_image, rect1, rect2 = column_split(unrotatedImage, firstWhiteUnRotated, lastWhiteUnRotated)

    rescale_factor = 2.3
    binimage = binarize_image(split_image, rescale_factor=rescale_factor)
    rect1.rescale(rescale_factor=rescale_factor)
    rect2.rescale(rescale_factor=rescale_factor)

    col_image1 = get_cropped_region(binimage, rect=rect1)
    col_image2 = get_cropped_region(binimage, rect=rect2)
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    col_text1 = extract_text(col_image1)
    col_text2 = extract_text(col_image2)
    print(col_text1) 
    print("\n")
    print(col_text2)

    fullPage = ""
    fullPage += col_text1
    fullPage += "\n"
    fullPage += col_text2
    textList.append(fullPage)
    print("\n\n Finished Page! \n\n")
    # print("this is texlist: ", textList)

filePath = "C:\\tykun\\OneDrive\\Documents\\SchoolDocs\\VSCodeProjects\\randomPagesOCR.txt"
os.makedirs(os.path.dirname(filePath), exist_ok=True)

try:
    with open(filePath, 'w') as file:
        for item in textList:  # Assuming textList is iterable
            file.write(str(item) + '\n')  # Convert each item to string and add newline
except Exception as e:
    print(f"Error writing file: {e}")