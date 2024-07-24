import base64
import io
import matplotlib.pyplot as plt
from flask import redirect, render_template
import spotipy

def analytics(session, client_id, client_secret, redirect_uri, scope):
    """
    Displays user analytics including top artists,
    tracks, albums, and recently played songs.
    """
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect('/')

    sp = spotipy.Spotify(auth=token_info['access_token'])

    top_artists = sp.current_user_top_artists(limit=5, time_range='medium_term')['items']
    top_tracks = sp.current_user_top_tracks(limit=5, time_range='medium_term')['items']
    top_albums = [track['album']['id'] for track in top_tracks]

    album_details = [sp.album(album_id) for album_id in top_albums]
    album_popularity = [album['popularity'] for album in album_details]
    album_names = [album['name'] for album in album_details]

    recently_played = sp.current_user_recently_played(limit=5)['items']

    def generate_bar_graph(labels, values, title):
        plt.figure(figsize=(10, 5))
        plt.bar(labels, values)
        plt.title(title)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        img = io.BytesIO()
        plt.savefig(img, format='png')
        plt.close()
        img.seek(0)
        return base64.b64encode(img.getvalue()).decode()

    artist_names = [artist['name'] for artist in top_artists]
    artist_popularity = [artist['popularity'] for artist in top_artists]
    artist_graph = generate_bar_graph(artist_names, artist_popularity, 'Top 5 Artists')

    track_names = [track['name'] for track in top_tracks]
    track_popularity = [track['popularity'] for track in top_tracks]
    track_graph = generate_bar_graph(track_names, track_popularity, 'Top 5 Songs')

    album_graph = generate_bar_graph(album_names, album_popularity, 'Top 5 Albums')

    recent_track_names = [item['track']['name'] for item in recently_played]
    recent_track_artists = [item['track']['artists'][0]['name'] for item in recently_played]

    return render_template('analytics.html', 
                           artist_graph=artist_graph, 
                           track_graph=track_graph, 
                           album_graph=album_graph, 
                           recent_track_names=recent_track_names, 
                           recent_track_artists=recent_track_artists, 
                           zip=zip)
