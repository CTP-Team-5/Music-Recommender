import pickle
import streamlit as st
import pandas as pd
import time  
import csv
import random

# Load CSS styles from a file and apply them to the Streamlit app
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load the data into a pandas DataFrame
music = pd.read_csv('spotify_mil_song_dataset.csv')

# Load a precomputed similarity matrix from a file
similarity = pickle.load(open('pickle files/similarity.pkl', 'rb'))

# This function finds artists similar to the given artist based on a similarity matrix
def find_similar_artists(artist_name):
    # Find indices of songs by the given artist within the first 5000 entries of the music DataFrame
    artist_songs_indices = music[music['artist'] == artist_name].index.tolist()
    artist_songs_indices = [index for index in artist_songs_indices if index < 5000]

    # Initialize a dictionary to keep track of similarity scores for each artist
    artist_similarity = {}

    # Loop over each song index of the given artist
    for index in artist_songs_indices:

        # Iterate over the similarity scores of the song with other songs
        for i, similarity_score in enumerate(similarity[index]):

            # Skip processing for indices beyond 5000
            if i >= 5000: 
                continue
            other_artist = music.iloc[i]['artist']

            # Accumulate similarity scores for artists other than the given artist
            if other_artist != artist_name:
                if other_artist in artist_similarity:
                    artist_similarity[other_artist] += similarity_score
                else:
                    artist_similarity[other_artist] = similarity_score

    # Sort artists based on the total accumulated similarity score in descending order
    similar_artists = sorted(artist_similarity.items(), key=lambda x: x[1], reverse=True)

    # Return top 10 similar artists
    return similar_artists[:10]


# This function recommends songs based on a given song using the similarity matrix
def recommend(song):
    try:
        # Find the index of the given song in the music DataFrame
        index = music[music['song'] == song].index[0]

        # Check if the index is within the bounds of the similarity matrix
        if index >= len(similarity):
            st.error("Error: Song index is out of bounds. Please try another song!")
            return []

        # Calculate distances (similarities) of the given song to all other songs
        distances = sorted(enumerate(similarity[index]), key=lambda x: x[1], reverse=True)

        # Select the top 5 similar songs (excluding the given song itself)
        recommended_music_names = [(music.iloc[i[0]]['song'], music.iloc[i[0]]['artist'], music.iloc[i[0]]['text'][:100]) for i in distances[1:6]]

        # Return the recommended song details
        return recommended_music_names
    
    # Handle the case where the song is not found in the DataFrame
    except IndexError:
        st.error("Error: Song not found. Please try a song from the dropdown menu!")
        return []

# Streamlit app interface setup
st.header('TextTune Music Recommender')
st.write('This is a music recommendation system based on the lyrics.')

# Sidebar for selecting recommendation type (song or artist)
recommendation_type = st.sidebar.radio(
    'Choose your recommendation type',
    ('Song Recommendation', 'Artist Recommendation')
)

# Handling the user's choice for recommendation type
if recommendation_type == 'Song Recommendation':
    # Dropdown for song selection
    selected_song = st.selectbox("Select a song", music['song'].unique(), 0)
    if st.button('Show Recommendations by Song'):
        recommended_music = recommend(selected_song)
        if recommended_music:
            st.subheader('Recommended Music')
            for song_name, artist_name, lyrics_snippet in recommended_music:
                formatted_output = f"**{song_name} by {artist_name}**\n\n**Lyrics:**\n*{lyrics_snippet}*"
                st.markdown(formatted_output, unsafe_allow_html=True)
        else:
            st.error("No recommendations available.")


elif recommendation_type == 'Artist Recommendation':
    selected_artist = st.selectbox("Select an artist", music['artist'].unique(), 0)
    if st.button('Show Similar Artists'):
        similar_artists = find_similar_artists(selected_artist)
        if similar_artists:
            # Normalize the similarity scores
            max_score = max(similar_artists, key=lambda x: x[1])[1]
            normalized_artists = [(artist, score / max_score) for artist, score in similar_artists]

            st.subheader(f'Artists similar to {selected_artist}')
            for artist, normalized_score in normalized_artists:
                st.write(f"{artist} (Similarity: {normalized_score:.2f})")
        else:
            st.error("No similar artists found.")


# Footer with a copyright notice
st.markdown('<div class="team">© 2023 TechnoMelody</div>', unsafe_allow_html=True)
