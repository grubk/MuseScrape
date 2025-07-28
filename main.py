from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Rectangle
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import io
import os

def exportsvg(svg_list, output_filename="output.pdf"):
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
            # Download SVG content if it's a URL
            if svg_url.startswith('http'):
                response = requests.get(svg_url)
                svg_content = response.content
            else:
                svg_content = svg_url.encode('utf-8')
            
            # Create a temporary SVG file
            temp_svg_path = f"temp_page_{i}.svg"
            with open(temp_svg_path, 'wb') as f:
                f.write(svg_content)
            
            # Use matplotlib to render SVG and save as PNG
            fig, ax = plt.subplots(figsize=(8.5, 11), dpi=150)
            ax.axis('off')
            
            # Read and display the SVG
            try:
                # For SVG files, we need to use a different approach
                # Convert to PNG using matplotlib's SVG support
                temp_png_path = f"temp_page_{i}.png"
                
                # Use matplotlib to save the figure as PNG
                plt.savefig(temp_png_path, bbox_inches='tight', dpi=150, 
                           facecolor='white', edgecolor='none')
                plt.close()
                
                # Read the PNG and add to PDF
                img = Image.open(temp_png_path)
                img_width, img_height = img.size
                
                # Scale to fit page if necessary
                scale = min(width/img_width, height/img_height, 1.0)
                scaled_width = img_width * scale
                scaled_height = img_height * scale
                
                x = (width - scaled_width) / 2
                y = (height - scaled_height) / 2
                
                c.drawImage(temp_png_path, x, y, width=scaled_width, height=scaled_height)
                
                # Clean up temporary files
                os.remove(temp_svg_path)
                os.remove(temp_png_path)
                
            except Exception as svg_error:
                print(f"Error rendering SVG {i} with matplotlib: {svg_error}")
                # Fallback: if it's an image URL, try to download directly
                if svg_url.startswith('http'):
                    response = requests.get(svg_url)
                    img = Image.open(io.BytesIO(response.content))
                    temp_png_path = f"temp_page_{i}.png"
                    img.save(temp_png_path)
                    
                    img_width, img_height = img.size
                    scale = min(width/img_width, height/img_height, 1.0)
                    scaled_width = img_width * scale
                    scaled_height = img_height * scale
                    
                    x = (width - scaled_width) / 2
                    y = (height - scaled_height) / 2
                    
                    c.drawImage(temp_png_path, x, y, width=scaled_width, height=scaled_height)
                    os.remove(temp_png_path)
            
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

filename = input("Enter file name: ")
exportsvg(list(seen_pages), output_filename=f"{filename}.pdf")
driver.execute_script("arguments[0].scrollTop += arguments[1];", scroller, scroll_step)
time.sleep(scroll_pause)

driver.quit()

filename = input("Enter file name: ")
exportsvg(list(seen_pages), output_filename=f"{filename}.pdf")





