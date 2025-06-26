# SpotifyPlayer.py
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
     client_id=os.getenv("client_id"),
     client_secret=os.getenv("client_secret"),
     redirect_uri=os.getenv("redirect_uri"),
     scope="user-read-playback-state user-modify-playback-state"
))

def play_song(query):
     try:
          # Try searching by track name
          results = sp.search(q=f"track:{query}", type='track', limit=1)
          tracks = results.get('tracks', {}).get('items', [])

          # Fallback to general search if specific search fails
          if not tracks:
               results = sp.search(q=query, type='track', limit=1)
               tracks = results.get('tracks', {}).get('items', [])
          
          if not tracks:
               return f"No results found for '{query}'. Please try a different song name."

          track = tracks[0]
          track_uri = track['uri']
          track_name = track['name']
          artist_name = track['artists'][0]['name']

          # Check active devices
          devices = sp.devices()
          device_list = devices.get('devices', [])

          if not device_list:
               return "No active Spotify devices found. Please open Spotify on one of your devices."

          device_id = device_list[0]['id']
          sp.start_playback(device_id=device_id, uris=[track_uri])

          return f"Now playing: {track_name} by {artist_name}"
     
     except Exception as e:
          return f"Error: {str(e)}"