from flask import redirect, url_for, render_template, render_template_string
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from bs4 import BeautifulSoup

def playlist(request, session, client_id, client_secret, redirect_uri, scope):
    """
    Creates a new playlist with Billboard Top 100 songs based on the provided date.
    Handles both GET and POST requests.
    """
    if request.method == 'POST':
        date = request.form['date']
        token_info = session.get('token_info', None)
        if not token_info:
            return redirect('/')

        sp = spotipy.Spotify(auth=token_info['access_token'])

        user_id = sp.me()['id']
        playlist = sp.user_playlist_create(user=user_id, name=f'Billboard 100 ({date})', public=True, description=f'Top 100 songs from Billboard on {date}')

        billboard_url = f'https://www.billboard.com/charts/hot-100/{date}'
        response = requests.get(billboard_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        songs = soup.select('li.o-chart-results-list__item h3')
        artists = soup.select('li.o-chart-results-list__item span.c-label')

        track_ids = []
        for song, artist in zip(songs, artists):
            song_name = song.get_text(strip=True)
            artist_name = artist.get_text(strip=True)
            results = sp.search(q=f'track:{song_name} artist:{artist_name}', type='track')
            items = results['tracks']['items']
            if items:
                track_ids.append(items[0]['id'])

        if track_ids:
            sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist['id'], tracks=track_ids)

        return render_template_string('''
            <html>
                <head>
                    <link rel="stylesheet" type="text/css" href="/static/styles.css">
                </head>
                <body>
                    <div class="center">
                        <p>Playlist created successfully!</p>
                        <button onclick="window.location.href='/analytics'">View Analytics</button>
                        <button onclick="window.location.href='/playlist'">Create Another Playlist</button>
                    </div>
                </body>
            </html>
        ''')
    
    return render_template('index.html')
