import spotipy
from spotipy.oauth2 import SpotifyOAuth

from flask import Flask, redirect, request, session, url_for, render_template

from dotenv import load_dotenv
import os

import features.playlist as playlist_feature
import features.analytics as analytics_feature

app = Flask(__name__)
app.secret_key = 'djkfgg121'
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'

# Spotify API credentials
client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')
redirect_uri = os.getenv('redirect_uri')
scope = 'playlist-modify-public user-top-read user-read-recently-played'

@app.route('/')
def index():
    sp_oauth = SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope)
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """
    Handles the callback from Spotify's authentication process.
    Retrieves the access token and stores it in the session.
    Redirects to the features page.
    """
    sp_oauth = SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope)
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect(url_for('features'))

@app.route('/features')
def features():
    """
    Displays the features page if the user is authenticated.
    Redirects to the authentication page if not.
    """
    if 'token_info' not in session:
        return redirect('/')
    return render_template('features.html')

@app.route('/playlist', methods=['GET', 'POST'])
def playlist():
    """
    Handles the creation of a new playlist with Billboard Top 100 songs.
    Processes user's submission and creates a playlist with the specified date.
    """
    return playlist_feature.playlist(request, session, client_id, client_secret, redirect_uri, scope)

@app.route('/analytics')
def analytics_route():
    """
    Displays user analytics including top artists,
    tracks, albums, and recently played songs.
    """
    return analytics_feature.analytics(session, client_id, client_secret, redirect_uri, scope)

if __name__ == '__main__':
    app.run(debug=True)
