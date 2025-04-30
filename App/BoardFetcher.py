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
import pickle
import os

class BoardFetcher:
    # The base URL for where Uni is running. 
    # TODO Change this to be Uni's web link once the board-overlay branch is merged.
    UNI_URL = "http://localhost:3000/uni"
    LOAD_DELAY = 3 # How long it's expected to take to load a board overlay.
    LOADING_IMAGE = "ExtraFiles/GamesPlane Logo/Loading Logo.png"
    FAILED_IMAGE = "ExtraFiles/GamesPlane Logo/Invalid Logo.png"

    def __init__(self, name, variant):
        self.name = name
        self.variant = variant

        self.base_url = f"{self.UNI_URL}/games/{self.name}/variants/{self.variant}"

        # Create a Selenium driver for this game.
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)

        self.cache_route = f"{self.CACHE_BASE_ROUTE}/{self.name}_{self.variant}.pkl"
        self.loaded = {}
        self.board_cache = self.get_cache()

    def url_for(self, board_state):
        return f"{self.base_url}/{board_state}/board-overlay"
    
    CACHE_BASE_ROUTE = "./App/MovesCache/"
    # Write my current cache
    def write_cache(self):
        with open(self.cache_route, 'wb') as f:
            pickle.dump(self.board_cache, f)
            print(f"Dumped {len(self.board_cache)} cached board overlays for {self.name} to {self.cache_route}")

    # Attempt to get my cache object from the MovesCache.
    # If it doesn't exist, create it.
    def get_cache(self):
        if os.path.exists(self.cache_route):
            with open(self.cache_route, 'rb') as f:
                items = pickle.load(f)
                print(f"Successfully loaded {len(items)} cached board overlays for {self.name} from {self.cache_route}")
                return items
        else:
            self.board_cache = {}
            self.write_cache()
            return {}

    async def fetch_svg(self, board_state):
        # Generate and save to cache.
        url = self.url_for(board_state)
        print(f"Fetching a board overlay from {url}")
        self.driver.get(url)

        # Let the page load and JS run.
        # TODO We should try to lower this as much as possible.
        await asyncio.sleep(1.5)

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
            self.board_cache[board_state] = cv2.imread(self.FAILED_IMAGE, cv2.IMREAD_UNCHANGED) 
            self.loaded[board_state] = True

    async def get_svg_for(self, board_state):
        # Check the cache.
        if board_state in self.board_cache:
            return self.board_cache[board_state]

        self.board_cache[board_state] = cv2.imread(self.LOADING_IMAGE, cv2.IMREAD_UNCHANGED)   # Default to loading logo.
        self.loaded[board_state] = False

        # Begin trying to load the web picture.
        await self.fetch_svg(board_state)

    # To be called before a program ends. Closes the selenium session and writes to cache.
    def close(self):
        self.driver.quit()
        self.write_cache()
        print("Quit Selenium and wrote cache.")

    # Debug function to check what a board state's image looks like.
    def show(self, board_state):
        if board_state in self.board_cache:
            cv2.imshow(f"{self.name} : {board_state}", self.board_cache[board_state])
            # Get the current date and time
        else:
            print(f"{datetime.datetime.now()} : Tried to show {board_state} which wasn't in cache. {self.board_cache}")