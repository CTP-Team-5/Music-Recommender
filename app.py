import pickle
import streamlit as st
import pandas as pd
import csv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"
CLIENT_SECRET = "YOUR_SPOTIFY_SECRET_KEY"

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load CSS styles
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load the combined data into a DataFrame
music = pd.read_csv('spotify_mil_song_dataset.csv')

# Load the similarity matrix
similarity = pickle.load(open('pickle files/similarity.pkl', 'rb'))

def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        return album_cover_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png"

def get_artist_image_url(artist_name):
    results = sp.search(q=f"artist:{artist_name}", type="artist")

    if results and results["artists"]["items"]:
        artist = results["artists"]["items"][0]
        if artist["images"]:
            return artist["images"][0]["url"]
    return "https://i.postimg.cc/0QNxYz4V/social.png"

def find_similar_artists(artist_name):
    # Find all songs by the given artist within the first 5000 indices
    artist_songs_indices = music[music['artist'] == artist_name].index.tolist()
    artist_songs_indices = [index for index in artist_songs_indices if index < 5000]

    # Dictionary to keep sum of similarities for each artist
    artist_similarity = {}

    # Calculate similarity with other songs
    for index in artist_songs_indices:
        for i, similarity_score in enumerate(similarity[index]):
            if i >= 5000:  # Skip artists beyond the 5000 index
                continue
            other_artist = music.iloc[i]['artist']
            if other_artist != artist_name:
                if other_artist in artist_similarity:
                    artist_similarity[other_artist] += similarity_score
                else:
                    artist_similarity[other_artist] = similarity_score

    # Sort artists by total similarity
    similar_artists = sorted(artist_similarity.items(), key=lambda x: x[1], reverse=True)

    # Return top N similar artists with their images
    similar_artists_with_images = [
        (artist, similarity_score, get_artist_image_url(artist))
        for artist, similarity_score in similar_artists[:10]
    ]

    return similar_artists_with_images

# Function to recommend songs
def recommend(song):
    try:
        index = music[music['song'] == song].index[0]
        if index >= len(similarity):
            st.error("Error: Song index is out of bounds. Please try another song!")
            return []

        distances = sorted(enumerate(similarity[index]), key=lambda x: x[1], reverse=True)
        recommended_music = [(music.iloc[i[0]]['song'], music.iloc[i[0]]['artist'], music.iloc[i[0]]['text'][:100]) for i in distances[1:6]]

        recommended_music_with_covers = [
            (song_name, artist_name, lyrics_snippet, get_song_album_cover_url(song_name, artist_name))
            for song_name, artist_name, lyrics_snippet in recommended_music
        ]

        return recommended_music_with_covers
    except IndexError:
        st.error("Error: Song not found. Please try a song from the dropdown menu!")
        return []

# Streamlit app interface
st.header('TextTune Music Recommender')
st.write('This is a music recommendation system based on the lyrics.')

# Sidebar for choosing recommendation type
recommendation_type = st.sidebar.radio(
    'Choose your recommendation type',
    ('Song Recommendation', 'Artist Recommendation')
)

if recommendation_type == 'Song Recommendation':
    # Dropdown for song selection
    selected_song = st.selectbox("Select a song", music['song'].unique(), 0)
    if st.button('Show Recommendations by Song'):
        recommended_music = recommend(selected_song)
        if recommended_music:
            st.subheader('Recommended Music')
            cols = st.columns(5)
            for idx, (song_name, artist_name, lyrics_snippet, cover_url) in enumerate(recommended_music):
                with cols[idx % 5]:
                    st.image(cover_url, use_column_width=True)
                    st.text(f"{song_name} by {artist_name}")
                    st.markdown(f"*{lyrics_snippet}*")
        else:
            st.error("No recommendations available.")

elif recommendation_type == 'Artist Recommendation':
    selected_artist = st.selectbox("Select an artist", music['artist'].unique(), 0)
    if st.button('Show Similar Artists'):
        similar_artists = find_similar_artists(selected_artist)
        if similar_artists:
            st.subheader(f'Artists similar to {selected_artist}')
            cols = st.columns(5)
            for idx, (artist, similarity_score, image_url) in enumerate(similar_artists):
                with cols[idx % 5]:
                    st.image(image_url, use_column_width=True)
                    st.write(f"{artist} (Similarity: {similarity_score:.2f})")
        else:
            st.error("No similar artists found.")

# Footer
st.markdown('<div class="team">© 2023 TechnoMelody</div>', unsafe_allow_html=True)
