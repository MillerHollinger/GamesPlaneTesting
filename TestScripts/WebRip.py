import time
import base64
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Setup headless Chrome
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# Load the page
driver.get("http://localhost:3000/uni/games/othello/variants/regular/board-overlay")

# Wait for JS load (tweak as needed)
time.sleep(3)

# Get page source after JS execution
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# Extract element by ID
data_url = soup.find("img", id="board-overlay")["src"]

# Step 1: Strip prefix
header, encoded = data_url.split(",", 1)

# Step 2: Decode base64
image_data = base64.b64decode(encoded)

# Step 3: Write to file
with open("demo-out.png", "wb") as f:
    f.write(image_data)

driver.quit()