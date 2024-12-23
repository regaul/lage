from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

app = Flask(__name__)

# add absolute path resolution
basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')

print(f"Looking for .env file at: {env_path}")
print(f"File exists: {os.path.exists(env_path)}")

# load with explicit path
load_dotenv(env_path)

# debug
print("Environment variables loaded. Checking values:")
print(f"SPOTIFY_TOKEN exists: {'SPOTIFY_TOKEN' in os.environ}")
print(f"SPOTIFY_ID exists: {'SPOTIFY_ID' in os.environ}")
print(f"SPOTIFY_SECRET exists: {'SPOTIFY_SECRET' in os.environ}")




@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    genre = data.get('genre')
    time_period = data.get('time_period', '2000s')

    response = {
        "input": {"genre": genre, "time_period": time_period},
        "recommendations": [
            {"title": "Song 1", "artist": "Artist 1"},
            {"title": "Song 2", "artist": "Artist 2"},
        ]
    }
    return jsonify(response)

@app.route('/')
def home():
    return "running :D"

if __name__ == '__main__':
    app.run(debug=True)
