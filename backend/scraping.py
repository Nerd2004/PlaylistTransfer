import os
import time
from flask import Blueprint, json, request, jsonify
from flask_cors import CORS
from youtube import process_playlist
from logging_manager import log_message
import boto3
import concurrent.futures
from botocore.config import Config
scraping_bp = Blueprint('scraping', __name__)
CORS(scraping_bp, supports_credentials=True)

# Initialize the Boto3 client for Lambda
config = Config(
    read_timeout=900,  # Set this to the max time your Lambda function may take (up to 15 minutes)
    connect_timeout=900
)
# lambda_client = boto3.client('lambda', region_name='us-east-1',config=config)

def create_lambda_client():
    session = boto3.Session(
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1'
    )
    return session.client('lambda', config=config)

def searchResults(query, max_retries=3):
    log_message(f"Searching for {query}")
    print(f"Searching for {query}")
    
    retries = 0
    
    while retries < max_retries:
        try:
            lambda_client = create_lambda_client()  # Create a new client for each call
            # Invoke the Lambda function
            response = lambda_client.invoke(
                FunctionName='Scraper-SeleniumFunction-QOvvqKdVKlHh',
                InvocationType='RequestResponse',
                Payload=json.dumps({"action": "searchResults", "query": f"{query}"})
            )
        
            # Parse the response
            response_payload = json.loads(response['Payload'].read())
            video_id = json.loads(response_payload.get('body'))
            
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
        # Invoke the Lambda function
        lambda_client = create_lambda_client()  # Create a new client for each call
        response = lambda_client.invoke(
            FunctionName='Scraper-SeleniumFunction-QOvvqKdVKlHh',
            InvocationType='RequestResponse', 
            # Payload=json.dumps({"action":"list_files"})
            Payload=json.dumps({"action":"get_songs","playlistLink": f"{playlist_link}"})  # Replace with your actual payload
        )
    
        # Parse the response
        response_payload = json.loads(response['Payload'].read())
        song_list = json.loads(response_payload.get('body'))
        playlist_name = song_list[0]
        del song_list[0]
        
        log_message(f"PlaylistTransfer Found Total {len(song_list)} songs from playlist {playlist_name}")
        print(f"PlaylistTransfer Found Total {len(song_list)} songs from playlist {playlist_name}")
    
        # Use ThreadPoolExecutor for I/O-bound tasks
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(searchResults, song_list))
        
        # Create a dictionary mapping songs to their results
        result_map = dict(zip(song_list, results))

        print(result_map)
        return process_playlist(playlist_name,result_map)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    



    
    

    
