from flask import Blueprint, request, jsonify
from flask_cors import CORS
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import StaleElementReferenceException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import random
from youtube import process_playlist
from urllib.parse import quote
from urllib.parse import urlparse, parse_qs
from logging_manager import log_message





scraping_bp = Blueprint('scraping', __name__)
CORS(scraping_bp, supports_credentials=True, origins=["https://playlist-transfer-lovat.vercel.app"])


user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
]

headers = {
    'User-Agent': random.choice(user_agents),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.google.com/',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


#Routes for scraping spotify playlist details 
@scraping_bp.route("/scrapeplaylist", methods=["POST"])
def get_songs():

    #  Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument(f'user_agent={random.choice(user_agents)}')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the ChromeDriver with webdriver_manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Extract the playlist link from the request JSON body
    data = request.get_json()  # Get the JSON data from the request
    playlist_link = data.get("playlistLink")  # Extract the playlist_link field
    
    url = playlist_link
    driver.get(url)

    try:
        # Wait for the grid div to be present
        h1_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.encore-text.encore-text-headline-large.encore-internal-color-text-base"))
        )
        playlist_name = h1_element.text
        
        grid_div = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='grid']"))
        )

        collected_labels = []
        
        last_button_count = 0
        # Use log_message to send logs
        log_message(f"Extracting Songs from Playlist {playlist_name}")
        print(f"Extracting Songs from Playlist {playlist_name}")
        while True:
            # Find all buttons inside the grid div
            buttons = grid_div.find_elements(By.TAG_NAME, "button")
            
            # Extract and write the aria-label attribute of each button
            for button in buttons:
                try:
                    label = button.get_attribute('aria-label')
                    if label and label.startswith("Play"):
                        label = label.removeprefix("Play ")
                        if label not in collected_labels:
                            collected_labels.append(label)
                except StaleElementReferenceException:
                    # Handle cases where elements might have been removed from the DOM
                    continue
            
            # If no new buttons were loaded, break the loop
            if len(buttons) == last_button_count:
                break
            
            # Update the button count
            last_button_count = len(buttons)
            
            # Scroll to the last button
            driver.execute_script("arguments[0].scrollIntoView();", buttons[-1])
            
            # Wait for potential new content to load
            time.sleep(3)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()

    # Initialize an empty map (dictionary) to store name and video ID pairs
    video_map = {}
    # Process each label in the collected_labels list
    for label in collected_labels:
        log_message(f"Searching for {label}")
        print(f"Searching for {label}")
        video_id = searchResults(label)  # Generate the search result URL for the label
        video_map[label] = video_id  # Add the label and video ID to the map
    
    return process_playlist(playlist_name,video_map)



def searchResults(query):
     #  Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument(f'user_agent={random.choice(user_agents)}')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the ChromeDriver with webdriver_manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    encoded_query = quote(query)
    
    url = f"https://www.youtube.com/results?search_query={encoded_query}"
    driver.get(url)

    try:
        # Locate the <a> tag with id="thumbnail" inside nested divs
        thumbnail_anchor = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#container a#thumbnail"))
        )

        # Get the href attribute or perform other actions
        href = thumbnail_anchor.get_attribute("href")
        
        # Parse the URL
        parsed_url = urlparse(href)

        # Extract the query parameters
        query_params = parse_qs(parsed_url.query)

        # Get the 'v' parameter value (the video ID)
        video_id = query_params.get('v', [None])[0]

        return video_id

    except Exception as e:
        print(f"An error occurred: {e}")


    finally:
        driver.quit()
