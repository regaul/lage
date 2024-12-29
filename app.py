from flask import Flask, request, jsonify, render_template 
import requests
import os
import base64
from dotenv import load_dotenv

app = Flask(__name__, template_folder='ui')

# current env setup
basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')

print(f"Looking for .env file at: {env_path}")
print(f"File exists: {os.path.exists(env_path)}")
load_dotenv(env_path)

print("Environment variables loaded. Checking values:")
print(f"SPOTIFY_ID exists: {'SPOTIFY_ID' in os.environ}")
print(f"SPOTIFY_SECRET exists: {'SPOTIFY_SECRET' in os.environ}")

#generates token
def get_spotify_token():
    auth_url = 'https://accounts.spotify.com/api/token'
    
    # credentials
    client_id = os.getenv('SPOTIFY_ID')
    client_secret = os.getenv('SPOTIFY_SECRET')
    
    print(f"attempting token generation with:")
    print(f"Client ID present: {bool(client_id)}")
    print(f"Client Secret present: {bool(client_secret)}")
    
    if not client_id or not client_secret:
        print("Missing credentials")
        return None
        
    auth_string = f"{client_id}:{client_secret}"
    auth_header = base64.b64encode(auth_string.encode()).decode('utf-8')
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    
    try:
        response = requests.post(auth_url, headers=headers, data=data)
        print(f"token status: {response.status_code}")
        print(f"token response body: {response.text}")
        
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            print(f"failed to get token: {response.text}")
            return None
    except Exception as e:
        print(f"exception during token request: {str(e)}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    print("\n=== Starting new request ===")
    print("Received query:", request.json)
    
    query = request.json.get('query')
    print("\n=== Getting spotify token ===")
    token = get_spotify_token()
    print("Token received:", token[:30] + "..." if token else "No token received")
    
    headers = {'Authorization': f'Bearer {token}'}
    search_url = f'https://api.spotify.com/v1/search?q={query}&type=track&limit=5'
    print("\n=== Making spotify request ===")
    print("URL:", search_url)
    print("Headers:", {k: v[:30] + "..." if k == "Authorization" else v for k, v in headers.items()})
    
    response = requests.get(search_url, headers=headers)
    print("\n=== Spotify response ===")
    print("Status Code:", response.status_code)
    try:
        print("Response Body:", response.json())
    except Exception as e:
        print("Error parsing response:", str(e))
    
    tracks = response.json().get('tracks', {}).get('items', [])
    
    return jsonify({
        'recommendations': [
            {
                'title': track['name'],
                'artist': track['artists'][0]['name'],
                'url': track['external_urls']['spotify']
            }
            for track in tracks
        ]
    })

if __name__ == '__main__':
    app.run(debug=True)
