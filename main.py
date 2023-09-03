import requests
import secrets
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup

client_id = secrets.CLIENT_ID
client_secret = secrets.CLIENT_SECRET
redirect_uri = secrets.REDIRECT_URI
username = secrets.USERNAME

ENDPOINT = "https://api.spotify.com"

date = input("Which year do you want to travel to? Type the date in YYYY-MM-DD format: ")
year, month, day = date.split("-")

URL = "https://www.billboard.com/charts/hot-100/"

response = requests.get(f'{URL}{date}')
website = response.text

soup = BeautifulSoup(website, "html.parser")
song_tags = soup.select("li ul li h3")
songs: list[str] = [song_tag.get_text().strip() for song_tag in song_tags][:100]

authentication = SpotifyOAuth(client_id, client_secret, redirect_uri,
                              scope="playlist-modify-private", cache_path="token.txt")
access_token: str = authentication.get_access_token(as_dict=False)

sp = spotipy.Spotify(auth=access_token)
user = sp.current_user()
user_id = user["id"]

song_uris = []
for song in songs:
    result = sp.search(q=f"track: {song} year: {year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

playlist_id = sp.user_playlist_create(user=user_id, name=f"{int(month)}/{int(day)}/{year} Billboard 100", public=False)
sp.playlist_add_items(playlist_id=playlist_id["id"], items=song_uris)
