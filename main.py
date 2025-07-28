from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
import io
import re
import os

def exportsvg(svg_list, output_filename="output.pdf"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://musescore.com/',
        'Accept': 'image/svg+xml,image/*,*/*'
    }
    if not svg_list:
        print("No SVG data provided")
        return
    
    outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    
    pdf_path = os.path.join(outputs_dir, output_filename)
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    for i, svg_url in enumerate(svg_list):
        try:
            if svg_url.startswith('http'):
                response = requests.get(svg_url, headers=headers)
                response.raise_for_status()
                
                # Parse SVG content
                svg_content = response.content
                drawing = svg2rlg(io.BytesIO(svg_content))
                
                if drawing:
                    scale_x = width / drawing.width if drawing.width > 0 else 1
                    scale_y = height / drawing.height if drawing.height > 0 else 1
                    scale = min(scale_x, scale_y)
                    
                    drawing.scale(scale, scale)
                

                renderPDF.draw(drawing, c, 0, 0)
                
            if i < len(svg_list) - 1:
                c.showPage()
                
        except Exception as e:
            print(f"Error processing SVG {i}: {e}")
            continue
    
    c.save()
    print(f"PDF saved as: {pdf_path}")

browser_choice = input("Select browser (chrome/firefox): ").strip().lower()
driver = None

if browser_choice == "chrome":
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  #Comment/disable to see browser actions
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

elif browser_choice == "firefox":
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")  # Comment/disable to see browser actions
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

else:
    print("Invalid browser selection. Please choose 'chrome' or 'firefox'.")
    exit(1)

url = input("Input URL: ").strip()
driver.get(url)
time.sleep(5)

seen_pages = set()
scroll_pause = 1.0
max_scrolls = 20
scroll_step = 400
scroller = driver.find_element(By.ID, "jmuse-scroller-component")

for _ in range(max_scrolls):
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    for img in soup.find_all("img", class_="KfFlO"):
        src = img.get("src")
        if src and src not in seen_pages:
            seen_pages.add(src)
            alt = img.get("alt")
            print(f"Found page: {alt}")

    driver.execute_script("arguments[0].scrollTop += arguments[1];", scroller, scroll_step)
    time.sleep(scroll_pause)

driver.quit()

# Filter and sort SVGs by score number
def extract_score_number(url):
    match = re.search(r'score_(\d+)', url)
    return int(match.group(1)) if match else None

# Filter URLs that follow score_X naming convention and sort by score number
score_pages = []
for url in seen_pages:
    score_num = extract_score_number(url)
    if score_num is not None:
        score_pages.append((score_num, url))

# Sort by score number
score_pages.sort(key=lambda x: x[0])
sorted_svg_list = [url for _, url in score_pages]

print(f"Found {len(sorted_svg_list)} score pages")

filename = input("Enter file name: ")
exportsvg(sorted_svg_list, output_filename=f"{filename}.pdf")

# print([url for _, url in score_pages]) #If you want to see the individual urls of svg files in terminal





