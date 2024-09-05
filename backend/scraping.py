import os
import time
from flask import Blueprint, json, request, jsonify
from flask_cors import CORS
import requests
from youtube import process_playlist
from logging_manager import log_message
import concurrent.futures
scraping_bp = Blueprint('scraping', __name__)
CORS(scraping_bp, supports_credentials=True)


def searchResults(query, max_retries=5):
    log_message(f"Searching for {query}")
    print(f"Searching for {query}")
    
    retries = 0
    
    while retries < max_retries:
        try:
            function_url = os.environ.get('AWS_FUNCTION_URI')
            
            payload = {'action':'searchResults','query': f"{query}"}
            payload_json = json.dumps(payload)
            
            response = requests.post(function_url, json={'event': payload_json})
            
            # Parse the response
            video_id = response.json()
           
            # Check if video_id is None or empty and retry if needed
            if video_id and video_id != None:
                return video_id
            else:
                retries += 1
                print(f"Retrying for {query} ({retries}/{max_retries})...")
                time.sleep(2 ** retries)  # Exponential backoff
        
        except Exception as e:
            print(f'Error while searching for {query}: {e}')
            retries += 1
            time.sleep(2 ** retries)  # Exponential backoff
    
    # If max retries exceeded, return a default value or an error
    print(f"Max retries exceeded for {query}. Returning default value.")
    return "Nhi Mila Kuch"


    

#Routes for scraping spotify playlist details 
@scraping_bp.route("/scrapeplaylist", methods=["POST"])
def get_songs():
    # Extract the playlist link from the request JSON body
    data = request.get_json()  # Get the JSON data from the request
    playlist_link = data.get("playlistLink")  # Extract the playlist_link field

    try:
        # Invoke the Lambda function using Function URL
        function_url = os.environ.get('AWS_FUNCTION_URI')

        payload = {'action':'get_songs','playlistLink': f"{playlist_link}"}
        payload_json = json.dumps(payload)
        
        response = requests.post(function_url, json={'event': payload_json})
        print(response)

        # Parse the response
        song_list = response.json()
        

        playlist_name = song_list[0]
        del song_list[0]
        
        log_message(f"PlaylistTransfer Found Total {len(song_list)} songs in playlist {playlist_name}")
        print(f"PlaylistTransfer Found Total {len(song_list)} songs in playlist {playlist_name}")
    
        # Use ThreadPoolExecutor for I/O-bound tasks
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(searchResults, song_list))
        
        # Create a dictionary mapping songs to their results
        result_map = dict(zip(song_list, results))

        # for song, result in result_map.items():
        #     print(f"{song}: {result}")
        
        return process_playlist(playlist_name,result_map)

    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500
    



    
    

    
