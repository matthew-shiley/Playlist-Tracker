import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import os
from datetime import datetime

with open("config.json") as f:
    config = json.load(f)

SPOTIPY_CLIENT_ID = config['client_id']
SPOTIPY_REDIRECT_URI = config['redirect_uri']
PLAYLIST_ID = config['playlist_id']

SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

if SPOTIPY_CLIENT_SECRET is None:
    print("SPOTIPY_CLIENT_SECRET is not set")
else:
    print("SPOTIPY_CLIENT_SECRET loaded successfully")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="playlist-read-private"
))


def fetch_playlist_tracks():
    results = sp.playlist_items(PLAYLIST_ID)
    tracks = []
    for item in results['items']:
        track = item['track']
        tracks.append({
            'name': track['name'],
            'artist': ', '.join([artist['name'] for artist in track['artists']]),
            'album': track['album']['name'],
            'release_date': track['album']['release_date'],
            'url': track['external_urls']['spotify'],
            'added_at': item['added_at']
        })
    return tracks


def save_data(tracks):
    time = datetime.now()
    
    month = time.strftime("%Y-%m")
    day = time.strftime("%Y-%m/%Y-%m-%d")

    file = f"data/{day}.json"
    os.makedirs('data', exist_ok=True)
    folder = f"data/{month}"
    os.makedirs(folder, exist_ok=True)

    with open(file, 'w', encoding='utf-8') as f:
        json.dump(tracks, f, indent=4, ensure_ascii=False)
    print(f"Full snapshot saved to {file}")

def main():
    # Fetch the current playlist
    tracks = fetch_playlist_tracks()

    save_data(tracks)

if __name__ == "__main__":
    main()
