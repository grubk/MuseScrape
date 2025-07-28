from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import cairosvg
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import io
import os

def exportsvg(svg_list, output_filename="output.pdf"):
    if not svg_list:
        print("No SVG data provided")
        return
    

    pdf_path = os.path.join(os.path.dirname(__file__), output_filename)
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    for i, svg_content in enumerate(svg_list):
        try:
            
            png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
            img = Image.open(io.BytesIO(png_data))
            
            
            temp_path = f"temp_page_{i}.png"
            img.save(temp_path)
            
            
            img_width, img_height = img.size
            scale_x = width / img_width
            scale_y = height / img_height
            scale = min(scale_x, scale_y)
            
            
            scaled_width = img_width * scale
            scaled_height = img_height * scale
            x = (width - scaled_width) / 2
            y = (height - scaled_height) / 2
            
            c.drawImage(temp_path, x, y, width=scaled_width, height=scaled_height)
            
            os.remove(temp_path)
            
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
    # options.add_argument("--headless")  # Comment/disable to see browser actions
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

elif browser_choice == "firefox":
    options = webdriver.FirefoxOptions()
    # options.add_argument("--headless")  # Comment/disable to see browser actions
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

else:
    print("Invalid browser selection. Please choose 'chrome' or 'firefox'.")
    exit(1)

url = input("Input URL: ").strip()
driver.get(url)
time.sleep(5)  # Wait for page load

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



