* PDF Organizer

**Version:** 2.4.0-RC  
**Release Date:** March 15, 2026
**Author:** Denis Rylikov (denis.rylikov@protonmail.com)

* Description  
**PDF Organizer** is a Python-based tool designed to process, organize, and manage PDF files. It automates tasks such as adding sequence numbers to pages, grouping pages, merging PDFs, and generating detailed reports. This tool is ideal for efficiently handling large batches of PDF files.

---

* Features  
1. Adds sequence numbers to the lower-left corner of PDF pages.  
2. Counts records per PDF file.  
3. Processes multiple PDF files and organizes them into folders.  
4. Merges PDF files into a single document.  
5. Generates detailed reports for processed PDFs.  
6. Counts and organizes files into folders based on specific criteria.

---

* Requirements  
- Python 3.9 or higher  
- Libraries:
  - `arrow`
  - `csv`
  - `fitz` (PyMuPDF)
  - `matplotlib`
  - `numpy`
  - `pandas`
  - `PyPDF2`
  - `reportlab`
  - `pdfminer.six`

---

* Installation  
1. Clone the repository:  
   (( git clone https://github.com/drylikov/pdf-organizer.git ))  
   (( cd pdf-organizer ))  # Navigate to the project directory

2. Install the required Python libraries:  
   (( pip install -r requirements.txt ))  # Install dependencies from requirements.txt

---

* Usage  
1. Place the PDF files you want to process in the same directory as the script.  
2. Run the script:  
   (( python PDF_Organizer_App_Product_v2.4.0-RC.py ))  # Run the main Python script

3. Follow the prompts to enter the operator name and work order number.

---

* Outputs  
- **Processed PDFs:** Organized into folders based on page groups.  
- **Reports:**
  - `Data_log_<date>.csv`: Logs details of processed pages.  
  - `Report_<date>.csv`: Summary of processed PDFs, including record counts and total images.  
  - `Group_page_counts_<date>.csv`: Grouped page counts with total images and records.  
- **Merged PDFs:** Combined PDFs for each group.

---

* Key Functions  
1. **pageData**  
   Extracts and groups pages from PDF files into a DataFrame and organizes them into folders.

2. **extractPages**  
   Processes PDF files, groups pages, and creates blank PDFs for odd-numbered groups.

3. **processFilesPdf**  
   Processes PDF files and organizes them into folders based on page tags.

4. **createReport**  
   Generates a CSV report summarizing the processed PDFs.

5. **mergePdf**  
   Merges grouped PDF files into a single PDF for each group.

---

* Example Workflow  
1. Place your PDF files in the directory.  
2. Run the script and provide the required inputs.  
3. The script will:  
   - Extract and group pages.  
   - Create blank pages for odd-numbered groups.  
   - Organize PDFs into folders.  
   - Generate reports.  
   - Merge grouped PDFs into single files.

---

* Known Issues  
- **Blank PDF Creation:** A race condition may occur when creating the first blank PDF file during long processes.  
- **File Locking:** Ensure CSV files are not open in another program while running the script.

---

* Revision History  
**2.4.0-RC** (April 15, 2024)  
- Fixed bugs related to merging 5-page PDFs with blanks.  
- Created blank pages for odd-numbered groups.

**2.2**  
- Fixed merge sort order.

**2.0**  
- Switched from PyPDF2 to PyMuPDF and pdfminer.six for text extraction.

**1.11**  
- Added user input for operator name and work order.  
- Updated logging and bar chart generation.

---

* Author  
Developed by **Denis Rylikov**  
Contact: denis.rylikov@protonmail.com

---

* Acknowledgments  
Special thanks to the Python community for providing the libraries used in this project.

