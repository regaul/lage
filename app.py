from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import env


app = Flask(__name__)

#loads env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)
print("Environment loaded.")

SPOTIFY_TOKEN = os.getenv("SPOTIFY_TOKEN")
print("SPOTIFY_TOKEN:", os.getenv("SPOTIFY_TOKEN"))
print("SPOTIFY_ID:", os.getenv("SPOTIFY_ID"))
print("SPOTIFY_SECRET:", os.getenv("SPOTIFY_SECRET"))




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
