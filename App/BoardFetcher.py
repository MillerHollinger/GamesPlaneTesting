# Gets board state pictures.
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import base64
import asyncio
import io
import numpy as np
import cv2
import datetime

class BoardFetcher:
    # The base URL for where Uni is running. 
    # TODO Change this to be Uni's web link once the board-overlay branch is merged.
    UNI_URL = "http://localhost:3000/uni"
    LOAD_DELAY = 3 # How long it's expected to take to load a board overlay.
    LOADING_IMAGE = "ExtraFiles/GamesPlane Logo/Loading Logo.png"

    def __init__(self, name, variant):
        self.name = name
        self.variant = variant

        self.base_url = f"{self.UNI_URL}/games/{self.name}/variants/{self.variant}"

        # Create a Selenium driver for this game.
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)

        self.board_cache = {}
        self.loaded = {}

    def url_for(self, board_state):
        return f"{self.base_url}/{board_state}/board-overlay"

    async def fetch_svg(self, board_state):
        # Generate and save to cache.
        url = self.url_for(board_state)
        print(f"Fetching a board overlay from {url}")
        self.driver.get(url)

        # Let the page load and JS run.
        # TODO We should try to lower this as much as possible.
        await asyncio.sleep(0.5)

        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Extract element by ID
        try:
            data_url = soup.find("img", id="board-overlay")["src"]

            # Remove prefix info
            _, encoded = data_url.split(',', 1)
            image_data = base64.b64decode(encoded)

            # Decode the image
            image_np = np.frombuffer(image_data, dtype=np.uint8)
            
            image_cv = cv2.imdecode(image_np, cv2.IMREAD_UNCHANGED)
            
            # Check we successfully decoded the image
            if image_cv is None:
                raise ValueError("Failed to decode image.")
            
            # Resize to 512x512
            image_cv = cv2.resize(image_cv, (512, 512), interpolation=cv2.INTER_AREA)

            self.board_cache[board_state] = image_cv
            self.loaded[board_state] = True
        except:
            print(f"Invalid board state {board_state} was queried.")
            self.loaded[board_state] = True

    async def get_svg_for(self, board_state):
        # Check the cache.
        if board_state in self.board_cache:
            return self.board_cache[board_state]

        self.board_cache[board_state] = cv2.imread(self.LOADING_IMAGE, cv2.IMREAD_UNCHANGED)   # Default to loading logo.
        self.loaded[board_state] = False

        # Begin trying to load the web picture.
        await self.fetch_svg(board_state)

    # Ends the selenium session.
    def close(self):
        self.driver.quit()
        print("Closing")

    # Debug function to check what a board state's image looks like.
    def show(self, board_state):
        if board_state in self.board_cache:
            cv2.imshow(f"{self.name} : {board_state}", self.board_cache[board_state])
            # Get the current date and time
        else:
            print(f"{datetime.datetime.now()} : Tried to show {board_state} which wasn't in cache. {self.board_cache}")

async def main():
    bf = BoardFetcher("othello", "regular")

    try:
        asyncio.create_task(bf.get_svg_for("1_-----BW--WB-----"))
        while True:
            bf.show("1_-----BW--WB-----")

            await asyncio.sleep(0.001)

            # Wait for the user to press 'Q' to quit
            key = cv2.waitKey(1)  # 1 millisecond wait
            
            if key == ord('q'):  # Check if the key pressed is 'q'
                print("You pressed 'Q'. Exiting...")
                break  # Exit the loop

    finally:
        bf.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    asyncio.run(main())