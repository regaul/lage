from flask import Flask, request, jsonify, render_template 
import requests
import os
import base64
import time
from dotenv import load_dotenv

app = Flask(__name__, template_folder='ui')

token_info = {'token': None, 'expiry': None}

basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')
load_dotenv(env_path)

def get_tidal_token():
    if token_info['token'] and token_info['expiry'] and token_info['expiry'] > time.time():
        return token_info['token']
        
    auth_url = 'https://auth.tidal.com/v1/oauth2/token'
    client_id = os.getenv('TIDAL_ID')
    client_secret = os.getenv('TIDAL_SECRET')
    
    if not client_id or not client_secret:
        print("Missing TIDAL credentials")
        return None
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    try:
        response = requests.post(auth_url, headers=headers, data=data)
        print(f"Token response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            token_info['token'] = response_data['access_token']
            token_info['expiry'] = time.time() + response_data['expires_in']
            return token_info['token']
        else:
            print(f"Token request failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Token request failed: {str(e)}")
    return None

def parse_track_payload(payload):
    """Parse the track payload from the batch response"""
    tracks_data = []
    
    for track in payload.get('data', []):
        # Find corresponding artist and album in included data
        artist_id = track['relationships']['artists']['data'][0]['id']
        album_id = track['relationships']['albums']['data'][0]['id']
        
        artist_name = None
        album_picture = None
        
        for item in payload.get('included', []):
            if item['type'] == 'artists' and item['id'] == artist_id:
                artist_name = item['attributes']['name']
            elif item['type'] == 'albums' and item['id'] == album_id:
                image_links = item['attributes'].get('imageLinks', [])
                if image_links:
                    album_picture = image_links[0]['href']
        
        # Get similar track IDs
        similar_track_ids = [t['id'] for t in track['relationships'].get('similarTracks', {}).get('data', [])]
        
        tracks_data.append({
            'id': track['id'],
            'title': track['attributes']['title'],
            'artist': artist_name or 'Unknown Artist',
            'albumUrl': album_picture,
            'similarTracks': similar_track_ids[:5]
        })
    
    return tracks_data

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    token = get_tidal_token()
    if not token:
        return jsonify({'error': 'Failed to get TIDAL token'}), 401

    data = request.json
    query = data.get('query', '')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
        
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/vnd.tidal.v1+json'
    }

    search_url = 'https://openapi.tidal.com/v2/searchresults/' + query + "/relationships/tracks"
    params = {
        'include': 'tracks',
        'countryCode': 'US'
    }
    
    try:
        response = requests.get(search_url, headers=headers, params=params)
       
        if response.status_code != 200:
            return jsonify({'error': 'Search failed'}), response.status_code
            
        response_data = response.json()
        # Get the track IDs from the data array
        track_ids = [track['id'] for track in response_data.get('data', [])[:5]]
        

        # Get detailed track info in one request using ISRCs
        tracks_url = 'https://openapi.tidal.com/v2/tracks'
        tracks_params = {
            'filter[id]': ','.join(track_ids),
            'countryCode': 'US',
            'include': ['artists', 'albums', 'similarTracks']
        }
        
        tracks_response = requests.get(tracks_url, headers=headers, params=tracks_params)
        if tracks_response.status_code != 200:
            return jsonify({'error': 'Failed to get track details'}), tracks_response.status_code
            
        tracks_data = tracks_response.json()
        tracks = parse_track_payload(tracks_data)
        return jsonify({'tracks': tracks})
        
        # Get the full track data for each ID
       
    except Exception as e:
        print(f"Search failed: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    token = get_tidal_token()
    if not token:
        return jsonify({'error': 'Failed to get TIDAL token'}), 401

    data = request.json
    track_id = data.get('trackId')
    similarTracks = data.get('similarTracks')
    if not track_id:
        return jsonify({'error': 'No track ID provided'}), 400
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    try:
        recs = []
         # Get detailed track info in one request using ISRCs
        tracks_url = 'https://openapi.tidal.com/v2/tracks'
        tracks_params = {
            'filter[id]': ','.join(similarTracks),
            'countryCode': 'US',
            'include': ['artists', 'albums', 'similarTracks']
        }
        
        tracks_response = requests.get(tracks_url, headers=headers, params=tracks_params)
        if tracks_response.status_code != 200:
            return jsonify({'error': 'Failed to get track details'}), tracks_response.status_code
            
        tracks_data = tracks_response.json()
        recs = parse_track_payload(tracks_data)
        return jsonify({'recommendations': recs})

    except Exception as e:
        print(f"Recommendations failed: {str(e)}")
        return jsonify({'error': 'Failed to get recommendations'}), 500

if __name__ == '__main__':
    app.run(debug=True)