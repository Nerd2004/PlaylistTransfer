import os
import random
import time
from flask import Blueprint, json, jsonify, redirect, session, request, abort
import requests
from logging_manager import log_message
from flask_cors import CORS


youtube_bp = Blueprint('youtube', __name__)
CORS(youtube_bp, supports_credentials=True)

def process_playlist(playlist_name,user_id, songs):
    TOKEN_REFRESH_THRESHOLD = 300

    # Check if the token has expired or will expire soon
    if int(time.time()) >= session['token_expiry'] - TOKEN_REFRESH_THRESHOLD:
        # Token has expired or will expire soon, generate a new one using the refresh token
        refresh_token = session['refresh_token']
        token_endpoint = "https://oauth2.googleapis.com/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {
            "grant_type": "refresh_token",
            "client_id": os.getenv('CLIENT_ID'),
            "client_secret": os.getenv("CLIENT_SECRET"),
            "refresh_token": refresh_token
        }
        response = requests.post(token_endpoint, headers=headers, data=payload)
        if response.status_code == 200:
            # Get the new token and expiry from the response
            token_response = response.json()
            session['token'] = token_response['access_token']
            session['token_expiry'] = int(time.time()) + token_response['expires_in']
            print("New token generated successfully!")
        else:
            print("Error generating new token:", response.text)
            refresh_token = session['refresh_token']

    base_url = "https://www.googleapis.com/youtube/v3"

    # Set up headers with the access token obtained from OAuth 2.0
    headers = {
        "Authorization": f"Bearer {session['token']}"
    }
    
    # Create a Playlist
    log_message(user_id,"Creating the Playlist on YouTube")
    print(user_id,"Creating the Playlist on YouTube")
    playlist_request_body={
        "snippet": {
            "title": str(playlist_name),
            "description": "Transferred from Spotify with the help of website created by NERD"
        },
    }
    response = requests.post(f"{base_url}/playlists?part=snippet", headers=headers, json=playlist_request_body)
    # response = requests.get(endpoint, headers=headers)
    # Check for successful response
    playlist_id=""
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        playlist_id=data['id']
        log_message(user_id,"Playlist created successfully!")
        print(user_id,"Playlist created successfully!")
    elif response.status_code == 403:
         log_message(user_id,"Daily Free API quota finished")
         print(user_id,"Daily Free API quota finished")
         return{}
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return
    

    # Adding Videos on YT
    index=0
    for name,video_id in songs.items():
       # Adding video into the playlist
        videoadd_request_body={
            'snippet': {
            'playlistId': playlist_id, 
            'resourceId': {
                'kind': 'youtube#video',
                'videoId': video_id
                },
            'position': index
            }
        }

        # Attempt to add video with retries
        playlistaddresponse = add_video_with_retries(user_id,videoadd_request_body,base_url,headers)
        
        if playlistaddresponse:
            log_message(user_id,f"Added {name}")
            print(user_id,f"Added {name}")
            index += 1
        else:
            print(user_id,f"Unable to add {name}")
        

    return jsonify({'url': f"https://www.youtube.com/playlist?list={playlist_id}"})


# Function for exponential backoff with retries
def add_video_with_retries(user_id,videoadd_request_body,base_url,headers, max_retries=5):
    retries = 0
    while retries < max_retries:
        playlistaddresponse = requests.post(f"{base_url}/playlistItems?part=snippet", headers=headers, json=videoadd_request_body)
        if playlistaddresponse.status_code == 200:
            return playlistaddresponse
        elif playlistaddresponse.status_code == 403:
            log_message(user_id,"Daily Free API quota finished")
            print("Daily Free API quota finished")
            return None
        else:
            retries += 1
            wait_time = (2 ** retries) + random.uniform(0, 1)  # Exponential backoff with jitter
            print(f"Retrying in {wait_time:.2f} seconds due to error: {playlistaddresponse.json()}")
            time.sleep(wait_time)
    
    # If max retries reached
    print(f"Failed after {max_retries} attempts")
    return None




















