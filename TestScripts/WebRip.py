from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Set up headless Chrome
options = Options()
options.add_argument("--headless")  # run in the background
driver = webdriver.Chrome(options=options)

# Load the page
driver.get("http://localhost:3000/uni/games/othello/variants/regular/1_-----BW--WB-----/board-overlay")

# Wait for JavaScript to load (tweak as needed)
time.sleep(3)

# Get page source after JS execution
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# Extract element by ID
svg_element = driver.find_element("tag name", "svg")
print(svg_element)
svg_html = svg_element.get_attribute("outerHTML")

with open("output.svg", "w", encoding="utf-8") as f:
    f.write(svg_html)

print("SVG saved as output.svg")

driver.quit()