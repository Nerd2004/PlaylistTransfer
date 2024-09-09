import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import time
import random
from urllib.parse import quote, urlparse, parse_qs

# user_agents = [
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
# ]
user_agents=[
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36"
]

def get_chrome_options():
    
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280x1696")
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--no-zygote")
    chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"
    return chrome_options

def get_chrome_service():
    return Service("/opt/chrome-driver/chromedriver-linux64/chromedriver")


def get_songs(playlist_link, retries=5):
    for attempt in range(retries):
        chrome_options = get_chrome_options()
        service = get_chrome_service()
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(playlist_link)

        try:
            h1_element = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.encore-text.encore-text-headline-large.encore-internal-color-text-base"))
            )
            playlist_name = h1_element.text
            
            grid_div = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='grid']"))
            )

            collected_labels = []
            collected_labels.append(playlist_name)


            last_button_count = 0
            print(f"Extracting Songs from Playlist {playlist_name}")

            while True:
                buttons = grid_div.find_elements(By.TAG_NAME, "button")
                
                for button in buttons:
                    try:
                        label = button.get_attribute('aria-label')
                        if label and label.startswith("Play"):
                            label = label.removeprefix("Play ")
                            if label not in collected_labels:
                                collected_labels.append(label)
                    except StaleElementReferenceException:
                        continue
                
                if len(buttons) == last_button_count:
                    break
                
                last_button_count = len(buttons)
                
                driver.execute_script("arguments[0].scrollIntoView();", buttons[-1])
                
                time.sleep(3)

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {2**(attempt+1)} seconds...")
                time.sleep(2**(attempt+1))
            else:
                print("All retries failed.")
                raise
            return []
        

        finally:
            driver.quit()

        return collected_labels

def search_results(query,retries=3,delay=5):
    for attempt in range(retries):
        chrome_options = get_chrome_options()
        service = get_chrome_service()
        driver = webdriver.Chrome(service=service, options=chrome_options)

        encoded_query = quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        driver.get(url)

        try:
            thumbnail_anchor = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#container a#thumbnail"))
            )

            href = thumbnail_anchor.get_attribute("href")
            parsed_url = urlparse(href)
            query_params = parse_qs(parsed_url.query)
            video_id = query_params.get('v', [None])[0]

            return video_id

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("All retries failed.")
                raise
            return None

        finally:
            driver.quit()

def lambda_handler(event, context):
    try:

        body_json = json.loads(event['body'])
        event_json = json.loads(body_json['event'])

        action = event_json['action']
        
        if not action:
            return {
                "statusCode": 400,
                "body": json.dumps("No 'action' found in event")
            }
        
        # Check for a special action to list files
        if action == 'list_files':
            print("reached list files")
            # List files in /opt
            files = os.listdir('/opt')
            file_list = "\n".join(files)
            print(file_list)
            return {
                "statusCode": 200,
                "body": json.dumps({"files": file_list})
            }
        
        if action == "get_songs":
            url = event_json.get("playlistLink")
            if url:
                songs = get_songs(url)
                return {"statusCode": 200, "body": json.dumps(songs)}
            else:
                return {"statusCode": 400, "body": json.dumps("playlistLink is missing")}
        
        elif action == "searchResults":
            query = event_json.get("query")
            if query:
                video_id = search_results(query)
                return {"statusCode": 200, "body": json.dumps(video_id)}
            else:
                return {"statusCode": 400, "body": json.dumps("query is missing")}
        
        else:
            return {"statusCode": 400, "body": json.dumps("Invalid action")}
    
    except Exception as e:
        print("Error occurred:", str(e))  # Log the error
        return {"statusCode": 500, "body": json.dumps(str(e))}
