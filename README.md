# 🎶MuseScrape

A python web scraper that takes a MuseScore sheet from a url, and converts it to .pdf format directly.

---
### 🔧Installation

1. Clone the repository
2. Initialize a virtual environment in the project (have python installed of course)
     
   _in cmd:_
   ```
   python -m venv venv 
   venv\Scripts\activate
   ```
3. Install required dependencies  

     _in cmd:_
   ```
   pip install -r requirements.txt
   ```
---
### 📖How To Use

1. Run the file
2. Enter prompted information into the terminal (browser, url in format: https://musescore.com/user/{numbers}/scores/{numbers})
3. Name the file (Do not include .pdf at the end of your input, this is already appended in the program)
4. Once the script finishes, check **outputs** folder for your sheet music
---
### ‼️Important Information
- This does not work if the sheet is not fully displayable on MuseScore (For exapmle, this happens when the author is MuseScore themselves: "Made By Muse")
- Inside main.py, there are some lines of code that you can un-comment to enable certain functions:
  - View the browser the scraper opens behind the hood
  - Print a list of the svgs that were scraped
---
### ℹ️How Does It Work?

Using standard BeautifulSoup4 web scraping did not initially work for the MuseScore site, since sheet music was contained in a scrollable div that only displays the active page of sheet music in the page's html file.  
I had to use selenium to open an instance of a browser and then scroll within this div, extracting the pages as the script scrolls down the page.
The pages of sheet music were stored in .svg format, so I had to scale them to letter size, so they would fit in a printable pdf, and then convert the .svgs to one pdf file, sorting them and putting each new .svg on its own page.
