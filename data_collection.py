import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import os
from datetime import datetime, timedelta

# Load config
with open("config.json") as f:
    config = json.load(f)

SPOTIPY_CLIENT_ID = config['client_id']
SPOTIPY_CLIENT_SECRET = config['client_secret']
SPOTIPY_REDIRECT_URI = config['redirect_uri']
PLAYLIST_ID = config['playlist_id']

# Initialize Spotify API client
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


def save_snapshot(tracks):
    date_str = datetime.now().strftime("%Y-%m")
    snapshot_file = f"data/snapshot_{date_str}.json"
    os.makedirs('data', exist_ok=True)
    with open(snapshot_file, 'w', encoding='utf-8') as f:
        json.dump(tracks, f, indent=4, ensure_ascii=False)
    print(f"Full snapshot saved to {snapshot_file}")


def save_delta(new_tracks, old_tracks):
    date_str = datetime.now().strftime("%Y-%m-%d")
    delta_file = f"data/delta_{date_str}.json"

    changes = compare_changes(new_tracks, old_tracks)

    # Save the delta only if there are changes
    if changes['added'] or changes['removed']:
        os.makedirs('data', exist_ok=True)
        with open(delta_file, 'w', encoding='utf-8') as f:
            json.dump(changes, f, indent=4, ensure_ascii=False)
        print(f"Delta saved to {delta_file}")
    else:
        print("No changes detected. Delta file not created.")


def compare_changes(new_tracks, old_tracks):
    new_set = {(t['name'], t['artist'], t['url']) for t in new_tracks}
    old_set = {(t['name'], t['artist'], t['url']) for t in old_tracks}

    added = new_set - old_set
    removed = old_set - new_set

    return {
        'added': [{'name': name, 'artist': artist, 'url': url} for name, artist, url in added],
        'removed': [{'name': name, 'artist': artist, 'url': url} for name, artist, url in removed]
    }


def main():
    # Fetch the current playlist
    new_tracks = fetch_playlist_tracks()

    # Check if a full snapshot exists for this month
    current_month = datetime.now().strftime("%Y-%m")
    snapshot_file = f"data/snapshot_{current_month}.json"

    if not os.path.exists(snapshot_file):
        # Save a full snapshot for the month
        save_snapshot(new_tracks)
        old_tracks = []
    else:
        # Load the most recent snapshot
        with open(snapshot_file, 'r', encoding='utf-8') as f:
            old_tracks = json.load(f)

        # Save the delta for today
        save_delta(new_tracks, old_tracks)


if __name__ == "__main__":
    main()