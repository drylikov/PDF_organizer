
# ==========================================================================
# Title: PDF Organizer
# Function: Data Processing
# Developed by: Denis Rylikov
# Date Created: 2026 Feb 25
# Version 2.4.0-RC
# Description: Organize PDF files into folders based on the number of pages and merge them into one PDF file.
# Status: RELEASE CANDIDATE
# Release Date: 2026  Mar 15
# Filename: PDF_organizer_App_Product_v2.4.0-RC.py
# ==========================================================================

# libraries
import arrow # for time and date
import csv
import enum
import fitz  # PyMuPDF
import fnmatch
import glob
import itertools
import logging
import os
import re
import sys  
import shutil
import threading
import time

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

from asyncio import coroutines
from datetime import datetime
from itertools import count
from multiprocessing.sharedctypes import Value
from operator import index
from pathlib import Path
#from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from PyPDF2 import PdfFileMerger
from re import search
from reportlab.pdfgen import canvas # create a blank pdf file use reportlab library
from reportlab.lib.pagesizes import letter
from tkinter.messagebox import YES
from typing import Counter
from pdfminer.high_level import extract_text

# declarations
start_time = time.time()

pd.set_option('display.max_columns', None) # display all columns

# open current working directory
thisDir = os.getcwd()  

# get the current date
current_date = datetime.now()

# format the current date as a string in the 'MMM-DD' format
date_today = datetime.now().strftime('%b-%d') 

today_log = datetime.now() # get the current date and time

# format the current date as a string in the 'yy-mm-dd' format
date_filename = current_date.strftime('%y-%m-%d') 

pdf_date_today = datetime.now().strftime('%y%m%d') 

standard_date = datetime.now().strftime('%Y %b %d') 

# Time and Date
utc = arrow.utcnow()
localTimeStamp = arrow.now()
localDate = localTimeStamp.format('DD-MMM')
stringDateToday = str(localDate)
eventStamp = localTimeStamp.format('ddd DD MMMM YYYY, hh:mm:ss A')

def printInfo():
    print("------------------------------------------------------")
    print("Version: 1.11")
    print("Author: Denis Rylikov (denis.rylikov@protonmail.com)")
    print("Developed by: Denis Rylikov")
    print("Date Created: 2026 Feb 25")
    print("Release Date: 2026 March 15")
    print("------------------------------------------------------")

# ==========================================================================
print("\n======================================================")
print("\t\tPDF ORGANIZER")
printInfo()
print('Start of Event: ', eventStamp, '\n')
print('==================== S T A R T =======================')

# Getting the current work directory (cwd)
print("\nCurrent Directory:\n")
thisdir = os.getcwd()
print("\t",thisdir,"\n")

# get and count total files
onlyfiles = next(os.walk('.'))[2]
totalFiles = len(onlyfiles)
print("List of files in current directory: ", totalFiles, "\n")
for countFiles, theFiles in enumerate(onlyfiles,1):
    print("\t",countFiles,".",theFiles)
# print("\nTotal files in current directory: ", totalFiles)

# ==========================================================================
# GET INFORMATION

#print("Current Python File:\n\n", Path(__file__).absolute, "\n")

# declare variables
dateToday = []
mailDate = []
fileSizeList = []

print()
# total PDF Files
pdf_count = len(fnmatch.filter(os.listdir(Path().absolute()), '*.pdf'))
print("Total PDF Files: ", pdf_count)
print()

# print("*** PDF Information: ***\n")

# START FUNCTION

import os
from PyPDF2 import PdfFileWriter, PdfFileReader
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

def writePageTempFile(page):
    temp_filename = "temp.pdf"
    writer = PdfFileWriter()
    writer.addPage(page)
    with open(temp_filename, 'wb') as temp_file:
        writer.write(temp_file)
    return os.path.abspath(temp_filename)

def extractTextPage(pdf_path):
    with open(pdf_path, 'rb') as file:
        parser = PDFParser(file)
        document = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = PDFPageAggregator(rsrcmgr, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            layout = device.get_result()
            text = ""
            for element in layout:
                if isinstance(element, LTTextBoxHorizontal):
                    #print(f"ID TEXT(page): {element.get_text()}")
                    #id_text += element.get_text().strip() + ' '
                    text += element.get_text()
            #print("return ID TEXT(page): ",text)
            return text


# this function will extract and group the pages from the PDF files into one dataframe per page and then group them into folders based on the 'group pages' column
# and then create blank pdf files for each group of pages and move them to the respective folders based on the 'group pages' column value
# and then organize the pdf files into folders based on their Page Tags (if any).
def pageData(pdf_source_files, output_csv_path):
    data = []
    page_count = 1 # Initialize the page count
    index_page = 1

    # Check if the file exists and get the last value of indexPage if it does exist and is not empty
    # This will be used to continue where you left off if there was an error or interruption in the script
    # and you need to run it again without starting from the beginning of the PDF files list.
    if os.path.isfile(output_csv_path): # If the file exists
        try:
            # Try to open the file
            with open(output_csv_path, 'r+') as csvfile: # Open the file in read mode
                df = pd.read_csv(csvfile) # Read the CSV file into a DataFrame
                # print("Dataframe head: ",df.head())
                # Get the last value of indexPage
                if not df.empty: # if the DataFrame is not empty
                    index_page = df['Index Page'].iloc[-1] # Get the last value of indexPage
                    # print("last value of indexPage: ",indexPage)
                    page_count = index_page + 1
                    # print("last value of pageCount", pageCount)
                pass # Continue to the next line of code
        except PermissionError: # If the file is already open in another program
            # The file is already open, handle this situation as needed
            # print(f"File '{output_csv_path}' is already open. Please close it before running the script.")
            # return  # Stop the script
            print(f"WARNING: CSV file '{output_csv_path}' is already open. Please CLOSE it and then Restart the script. Thank you!\n")
            sys.exit()  # Stop the script

    # Iterate over the PDF files in the list
    for pdf_file_path in pdf_source_files:
        if not os.path.isfile(pdf_file_path): # If the file does not exist
            print(f"File not found: {pdf_file_path}") # Print a message
            continue # Skip to the next iteration of the loop
        # Get the input PDF filename without the extension
        input_filename = os.path.splitext(os.path.basename(pdf_file_path))[0]
        
        

        # Create a PDF resource manager object that stores shared resources such as fonts or images
        resource_manager = PDFResourceManager()
        la_params = LAParams() # Set the parameters for analysis
        device = PDFPageAggregator(resource_manager, laparams=la_params) # Create a PDF page aggregator object
        interpreter = PDFPageInterpreter(resource_manager, device) # Create a PDF page interpreter object
        
        # NEW PROCESS - Create a CSV file to store the extracted text 
        #with open(pdf_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        with open(pdf_file_path, 'rb') as csvfile:
            # csv_writer = csv.writer(csvfile) # Create a CSV writer object
            # csv_writer.writerow(['Page', 'Key Text']) # Write the header row
            
            # Get the total number of pages in the PDF
            doc = fitz.open(pdf_file_path) # Open the PDF file
            total_pages = len(doc) # Total number of pages in the PDF

            for pdf_page_number in range(1, total_pages + 1): # Iterate through each page
                page_text = extract_text(pdf_file_path, page_numbers=[pdf_page_number - 1]) # Extract text from the page           
            
                cleaned_text = cleanText(page_text)
        
                match = re.search(r'Page\s\([^)]+\)', cleaned_text) # Search for the key text
                
                if match:
                    key_text = match.group() # Extract the key text
                    page_number = int(key_text.split('(')[1].split(')')[0]) # Extract the page number from the key text
                else:
                    key_text = 'none' # If key text is not found, set it to 'none'
                    page_number = '1'
                # csv_writer.writerow([pdf_page_number, key_text]) # Write the page number and key text to the CSV file
                
                data.append([input_filename, pdf_page_number, key_text if key_text else 'None', page_number if page_number else '1', f'pg_{page_count}', f'pg_{page_count}.pdf'])
                page_count += 1
                index_page += 1

            doc.close()
        

    # Check if the file exists
    
    if os.path.isfile(output_csv_path):
        df = pd.read_csv(output_csv_path) 
        # print("Dataframe End: ",df.tail())
        # Get the last value of indexPage
        if not df.empty: # if the DataFrame is not empty
            index_page = df['Index Page'].iloc[-1] + 1 # Get the last value of indexPage and increment it by 1
            # print("df not empty")

        # Append to the existing CSV file
        with open(output_csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            #for indexPage, row in enumerate(data, start=1):
            for index, row in enumerate(data, start=index_page): # start from the last indexPage
                writer.writerow([index] + row)  # Write the data
                # print("Writing to CSV: ",index, row)
    else:
        # Create a new CSV file
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile: # Create a new CSV file and write the header
            writer = csv.writer(csvfile) # Create a CSV writer object
            writer.writerow(["Index Page","Filename","PDF Page", "Page Number Text", "FP", "Page Tag", "TagFiles"])  # Write the header
            #for indexPage, row in enumerate(data, start=1):
            for index, row in enumerate(data, start=1):    
                #writer.writerow([indexPage] + row)  # Write the data
                writer.writerow([index] + row)  # Write the data

    
    # print(f"\nThe CSV file '{output_csv_path}' has been updated.\n")

    
# END FUNCTION - page_data
    
# START FUNCTION - extract_and_group_pages
# this function will extract and group the pages from the PDF files into one dataframe per page and then group them into folders based on the 'group pages' column
def extractPages(input_pdf_path, csv_path, output_folder_path):
    try:
        # Try to open the CSV file
        with open(csv_path, 'a') as file:
            pass
    except PermissionError:
        # The CSV file is already open, handle this situation as needed
        #print(f"WARNING: CSV file '{csv_path}' is already open. Please CLOSE it and then Restart the script. Thank you!\n")
        print("ERROR: CSV file is already open.")
        sys.exit()  # Stop the script

    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_path) # Load the CSV file into a DataFrame
    record_count = len(df) # Get the total number of records in the DataFrame

    # print(f'Total Pages(Raw Images): {record_count}')

    # print("\n\t⚙️  Processing in progress...\n")

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder_path, exist_ok=True)

    # Define the input PDF file path and page count variable
    with open(input_pdf_path, 'rb') as file:
        pdf = PdfFileReader(file)
        total_pages = pdf.getNumPages() # Get the total number of pages in the PDF file
        df['FP'] = df['FP'].astype(int) # ensure 'FP' is of integer type

        # write value in new column 'group pages' and identify as group of n-pages
        group_pages = 0
        group_counter = 0
        start_index = 0
        for i, row in df.iterrows():
            group_counter += 1  # Increment the counter for each row
            if i < len(df) - 1 and df.loc[i + 1, 'FP'] == 1:  # If 'FP' is 1 in the next row
                df.loc[start_index:i, 'Group Pages'] = group_counter  # Assign the count to 'group pages' for all rows in the current group
                start_index = i + 1  # Update the start index for the next group
                group_counter = 0  # Reset the counter for the next group
        df.loc[start_index:, 'Group Pages'] = group_counter  # Assign the count to 'group pages' for the last group
        df.to_csv(csv_path, index=False)  # save the DataFrame to the CSV file
        # print("Group Pages: ",df['Group Pages'])     

        # Add 'blank pages' column to the df DataFrame
        df['Blank Pages'] = ''

        # Initialize the previous group pages value
        prev_group_pages = df.loc[0, 'Group Pages']

        for i, row in df.iterrows():
            # If the 'Group Pages' value is an odd number other than 1 and equal to the 'FP' value of the same row
            if row['Group Pages'] % 2 != 0 and row['Group Pages'] != 1 and row['Group Pages'] == row['FP']:
                # Write 'b' in 'blank pages' for the current row
                df.loc[i, 'Blank Pages'] = 'b'

        # Save the DataFrame to the CSV file
        df.to_csv(csv_path, index=False)

        # Define the function to apply to each row
        def create_filename(row):
            if 'b' in str(row['Blank Pages']):
                return f"{row['Page Tag']}{row['Blank Pages']}.pdf"
            else:
                return None

        # Create the new column
        df['BlankTagFiles'] = df.apply(create_filename, axis=1)

        # Save the DataFrame back to the CSV file
        df.to_csv(csv_path, index=False)
       
# END FUNCTION - extract_and_group_pages

# this function will organize the pdf files into folders based on their Page Tags
def organizePdfFiles(csv_path, input_folder_path, output_folder_path):
    # Read the CSV file
    df = pd.read_csv(csv_path)
   
    # Group the DataFrame by the 'group pages' column
    groups = df.groupby('Group Pages')

    # For each group
    for name, group in groups:
        n_PageGroup = int(name)
        print(f">>> {n_PageGroup}-page Group Files: \n")
        # Create a folder with the group name
        folder_path = os.path.join(output_folder_path, str(int(name)))
        print("Folder Path: **\\",folder_path, "\n")
        os.makedirs(folder_path, exist_ok=True)

        # For each file in the group
        for index, row in group.iterrows():
            # Move the file to the newly created folder
            file_path = os.path.join(input_folder_path, row['TagFiles']) # get the file path from the dataframe
            if os.path.isfile(file_path): # If the file exists
                # print("File Path: ",file_path, "\n")
                print(f"\t**\\{n_PageGroup}\\",row['TagFiles'], "\n") # **\n\pg_n.pdf
                shutil.move(file_path, folder_path) # error page 1 already existing in folder 1, the second pdf has same filename page1
                # print("Moving to Folder: ",folder_path, "\n")

# this function will create a blank pdf file and add text from another pdf file to it
def createBlankPdf(blankFilename):
    # check if the blank pdf file exists
    if not os.path.isfile(blankFilename):
        # if not create a blank pdf file
        c = canvas.Canvas(blankFilename, pagesize=letter)
        c.showPage()
        c.save()

# this function will process the PDF files and create a new PDF file for each page in the input PDF files
# and then organize the PDF files into folders based on their Page Tags (if any).
def processFilesPdf(pdf_files, csv_path, output_folder_path):
    df = pd.read_csv(csv_path) # Load the CSV file into a DataFrame
    page_number = 1 # Initialize the page number
    folder_number = 1 # Initialize the folder number

    # Iterate over the rows in the DataFrame and the PDF files in the list at the same time using zip function
    for pdf_file, (index, row) in zip(pdf_files, df.iterrows()):
        print("➡️  Processing current PDF file:\n\n", pdf_file, "\n")
        pdf = PdfFileReader(pdf_file)  # Open the PDF file
        total_pages = pdf.getNumPages()  # Get the total number of pages in the PDF file
        print("Total Pages: ",total_pages, "\n")

        # Iterate over the pages in the current PDF file
        for page_index in range(total_pages):
            writer = PdfFileWriter() # Create a new PDF writer object
            writer.addPage(pdf.getPage(page_index)) # Add the page to the new PDF

            page_tag = row['Page Tag'] # Get the 'Page Tag' column value
                
            page_file_path = os.path.join(output_folder_path, f'pg_{page_number}.pdf') # Define the path for the new PDF file
            print(f"pg_{page_number}.pdf\n")

            with open(page_file_path, 'wb') as output_pdf: # Write the new PDF to the output folder
                writer.write(output_pdf) # Write the new PDF to the output folder
                # print("Writing PDF to the output folder: ",page_file_path, "\n") 

            page_number += 1 # Increment the page number

        if row['FP'] == 1 and index == df.index[-1]: # If the 'FP' column value is '1' and it's the last page of the current PDF
            print("Last Page of the PDF: ",pdf_file, "\n")
            folder_number += 1 # Increment the folder number
    
    organizePdfFiles(csv_path, output_folder_path, output_folder_path)   

# END FUNCTION - process_pdf_files

# HELPER FUNCTION (TBA) this function will move a file from the source folder to the destination folder
def moveFile(src, dest):
    os.makedirs(dest, exist_ok=True)
    shutil.move(src, dest)

""" def dataFrameLink(outReportCsv):
    output_csv_path = f'Data_Log_{date_filename}.csv'  # replace with the path to your output CSV file
    df = pd.read_csv(output_csv_path) # Load the CSV file into a DataFrame
    print(df.head()) """

def createReport(df_data, report_filename):
    # Group the DataFrame by 'Filename' and calculate the last 'pdf page' and the sum of 'FP' for each group
    df_report = df_data.groupby('Filename').agg(Images=('PDF Page', 'last'), Records=('FP', lambda x: (x == 1).sum())).reset_index()

    # Insert a new column 'Records' at the beginning of the DataFrame, containing the sequence number of the records
    df_report.insert(0, 'Item', range(1, len(df_report) + 1))

    # Get the current date
    df_report['Date Today'] = date_today

    # Write the DataFrame to a new CSV file
    df_report.to_csv(report_filename, index=False)

def groupPageCounts(df_data, group_pagecounts_filename):

    # Group the DataFrame by 'Group Pages' and calculate the sum of 'Total Images' and the count of 'Group Pages' for each group
    df_group = df_data.groupby('Group Pages').size().reset_index(name='Total Images')

    # Insert a new column 'Total Records' at the beginning of the DataFrame, containing the sequence number of the records
    df_group['Total Records'] = df_group['Total Images'] / df_group['Group Pages']
    
    # Write the DataFrame to a new CSV file
    df_group.to_csv(group_pagecounts_filename, index=False)

     # Plot the 'Total Images' column
    ax = df_group['Total Images'].plot(kind='bar', color='b', label='Total Images')

    # Plot the 'Total Records' column
    df_group['Total Records'].plot(kind='bar', color='r', alpha=0.5, label='Total Records', ax=ax)

    # Add the 'Total Images' values as text on the bars
    ax.set_xticks(range(len(df_group)))
    ax.set_xticklabels(range(1, len(df_group) + 1))

    # Add a legend
    ax.legend()

    # Add the values on each bar
    for i, v in df_group.iterrows():
        ax.text(i, v['Total Images'], str(int(v['Total Images'])), ha='center', va='bottom')
        ax.text(i, v['Total Records'], str(int(v['Total Records'])), ha='center', va='bottom', color='white')

    # Add labels
    ax.set_xlabel('Group N-Pages')
    ax.set_ylabel('Images/Records')

    # format y-axis values to display interger values
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x)))

    # Add a title
    plt.title(f'Work Order: {work_order}\nDate: {standard_date}', fontsize=12, color='black', fontweight='bold')

    plt.savefig(f'Bar_chart_pdf_counts_{date_filename}.png', bbox_inches='tight') # Save the plot as a PNG file


# this function will move the blank PDF files to the destination folders
def moveBlankFiles(df_data):
    # Create a list to store the source and destination paths
    move_operations = []

    # Iterate over DataFrame rows
    for i, row in df_data.iterrows():
        # Check if 'BlankTagFiles' column is not None
        if pd.notna(row['BlankTagFiles']):
            # Create a blank PDF
            writer = PdfFileWriter()

            # Define the path for the new PDF file
            new_pdf_path = os.path.join('output', row['BlankTagFiles'])

            # Create a blank PDF file
            createBlankPdf(new_pdf_path)

            # Define the destination folder path
            dest_folder_path = os.path.join('output', str(int(row['Group Pages']))) 

            # Create the destination folder if it doesn't exist
            os.makedirs(dest_folder_path, exist_ok=True)

            # Add the source and destination paths to the list
            move_operations.append((new_pdf_path, os.path.join(dest_folder_path, row['BlankTagFiles'])))

    for source, destination in move_operations:
        # Move the blank PDF to the destination folder
        shutil.move(source, destination) 

def mergePdf_pypdf2(output_folder):
    # Merge the PDF files into one PDF file
    subfolder = [f for f in os.listdir(output_folder) if os.path.isdir(os.path.join(output_folder, f))]

    for subfolder in subfolder:
        pdf_group_folder = [f for f in os.listdir(os.path.join(output_folder, subfolder)) if f.endswith('.pdf')]

        merger = PdfFileMerger()

        for pdf in pdf_group_folder:
            merger.append(os.path.join(output_folder, subfolder, pdf))

        merger.write(f'PR_{work_order}_{pdf_date_today}_{subfolder}.pdf')
        merger.close()

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [atoi(c) for c in re.split(r'(\d+)', text)]

def mergePdf(output_folder):
    subfolders = [f for f in os.listdir(output_folder) if os.path.isdir(os.path.join(output_folder, f))]

    for subfolder in subfolders:
        pdf_group_folder = [f for f in os.listdir(os.path.join(output_folder, subfolder)) if f.endswith('.pdf')]
        
        # Sort the files by name before merging
        pdf_group_folder.sort(key=natural_keys)

        merged_pdf = fitz.open()
        for pdf in pdf_group_folder:
            pdf_path = os.path.join(output_folder, subfolder, pdf)
            pdf_doc = fitz.open(pdf_path)
            merged_pdf.insert_pdf(pdf_doc)
            pdf_doc.close()

        merged_pdf.save(f'PR_{work_order}_{pdf_date_today}_{subfolder}.pdf')
        merged_pdf.close()

# Usage example

# █ add text in pdf
def add_text_to_pdf(input_pdf, output_pdf, text_to_add, page_number=0, margin=20, font_size=12):
    # Open the PDF
    pdf_document = fitz.open(input_pdf)

    # Select the page to add text to
    page = pdf_document[page_number]

    # Get page dimensions
    page_width = page.rect.width
    page_height = page.rect.height

    # Calculate the position for the lower left corner
    position = (margin, page_height - margin - font_size)

    # Add text to the page
    page.insert_text(position, text_to_add, fontsize=font_size)

    # Save the changes
    pdf_document.save(output_pdf)
    pdf_document.close()

# Example usage
# add_text_to_pdf("input.pdf", "output.pdf", "Sample Text Lower Left Corner", page_number=0, margin=20, font_size=12)


def userInput():
    global operator_name, work_order

    while True:
        operator_name = input("Enter Operator Name: ")
        print("Operator Name: ", operator_name)
        work_order = input("Enter Work Order #: ")
        print("Work Order #: ", work_order)
        confirm_user_input = input("Confirm User Input (y=Yes/n=No/x=Exit): ")

        if confirm_user_input.lower() == 'y':
            print("\nThank you! The program will now continue. ☻\n")
            break
        elif confirm_user_input.lower() == 'x':
            print("\nExiting the program. Thank you!\n")
            exit()
        else:
            print("\nPlease enter the correct information. Thank you!\n")


def cleanText(text):
    # Replace special characters with space
    cleaned_text = re.sub(r'[^A-Za-z0-9() ]', ' ', text)
    # Replace multiple spaces with single space
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    return cleaned_text.strip()

#  Function to read text from PDF file and return it as a string
def findPageText(pdf_path):
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile) # Create a CSV writer object
        csv_writer.writerow(['Page', 'Key Text']) # Write the header row
        
        # Get the total number of pages in the PDF
        doc = fitz.open(pdf_path) # Open the PDF file
        total_pages = len(doc) # Total number of pages in the PDF

        for page_num in range(1, total_pages + 1): # Iterate through each page
            page_text = extract_text(pdf_path, page_numbers=[page_num - 1]) # Extract text from the page           
          
            cleaned_text = cleanText(page_text)
    
            match = re.search(r'Page\s\([^)]+\)', cleaned_text) # Search for the key text
            
            if match:
                key_text = match.group() # Extract the key text
            else:
                key_text = 'none' # If key text is not found, set it to 'none'
            csv_writer.writerow([page_num, key_text]) # Write the page number and key text to the CSV file

        doc.close()

# Function to print a spinner
def spinner():
    for char in itertools.cycle('█|/-\\'):
        if done:
            break
        print("Processing...",char, end='\r')
        time.sleep(0.1)

script_version = '2.4.0-RC'
# START PROGRAM

# Set up logging
logging.basicConfig(filename=f'pdfo_program_log_{date_filename}.txt', level=logging.INFO, 
                    format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

userInput() # Get the user input for Operator Name and Work Order #

logging.info(f'Operator Name: {operator_name}, Work Order #: {work_order}')

print("███ PDF Organizer ███\n")

# Flag to indicate when the processing is done
done = False

# Start the spinner in a separate thread
spinner_thread = threading.Thread(target=spinner)
spinner_thread.start()

# Indicate that the processing is done
done = True

# Wait for the spinner thread to finish
spinner_thread.join()

# print("\n\t Processing Completed! ☻\n")

print("\n\t⚙️  Processing in progress... ⚙️\n")

output_folder = 'output'

# get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# get a list of all the PDF files in the current directory
pdf_files = glob.glob(os.path.join(script_dir, '*.pdf'))

# define the path for the output CSV file
output_csv_path = f'Data_log_{date_filename}.csv'  # replace with the path to your output CSV file

# Check if the file already exists
if os.path.isfile(output_csv_path):
    response = input(f"ALERT: CSV file '{output_csv_path}' already exists. Do you want to delete it? (y=Yes/n=No): ")
    if response.lower() == 'y':
        os.remove(output_csv_path)
        print(f"CSV file '{output_csv_path}' has been deleted!\n")
        print("Thank you! The program will now continue. ☻\n")
    else:
        print("Please delete the CSV file and then restart the program. Thank you!")
        exit()

# Start of the program
logging.info(f'Program started on {today_log.strftime("%d-%b-%Y %H:%M:%S")}')

# if there are PDF files in the current directory, process them one by one
df = None  # Define the variable "df" before calling the function "process_pdf_files"

if pdf_files: # If there are PDF files in the current directory
    for input_pdf_src in pdf_files: # process multiple pdf files
        pageData([input_pdf_src], output_csv_path) # process only single pdf file
        # print("Completed Executing Function: page_data()")

        text = extractTextPage(input_pdf_src) # process only single pdf file
        # print("Completed Executing Function: extract_text_from_page()")

        extractPages(input_pdf_src, output_csv_path, 'output') # process only single pdf file
        # print("Completed Executing Function: extract_and_group_pages()")

        logging.info(f'Processed PDF file: {input_pdf_src}')
    
    processFilesPdf(pdf_files, output_csv_path, 'output')
    
else:
    print("No PDF files found in the current directory")
    sys.exit()

# count the total number of '1's in the 'FP' column
df_data = pd.read_csv(output_csv_path) # Load the CSV file into a DataFrame
print("█ Dataframe Output:\n",df_data)
total_fp_ones = (df_data['FP'] == 1).sum()
total_records = total_fp_ones
total_images_count = len(df_data) # Get the total number of records in the DataFrame

print("\n>>> Summary Counts:\n")
print("Total Pages(Raw Images):", total_images_count, "\n")
print("Total Records:", total_records, "\n")

createReport(df_data, f'Report_{date_filename}.csv') # Create a report for each processed pdf, including record counts and total images

groupPageCounts(df_data, f'Group_page_counts_{date_filename}.csv') # Create a report for group page counts with total images and records

moveBlankFiles(df_data) # Move the blank PDF files to the destination folders

mergePdf(output_folder) # Merge the PDF files into one PDF file


print("\n\t⚙️  Processing Completed! ⚙️\n")


#if __name__ == '__main__':



print('==================== E N D ====================\n')
print("End of Program: ",eventStamp)
print(f"\nThank you for using the program, {operator_name}. Have a great day! ad aspera ad astra.\n")
printInfo()
#print("\n\t-->>",exportFname)
#input("< Press Any Key to Close App >")

end_time = time.time()
total_time = end_time - start_time
print(f"Total Program Runtime: {format(total_time, '.5f')} seconds\n")

# End of the program
logging.info(f'Program ended on {datetime.now().strftime("%d-%b-%Y %H:%M:%S")}')


# END OF CODE