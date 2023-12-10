import pickle
import streamlit as st
import pandas as pd
import time  
import csv
import random

# Load CSS styles
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Open and read the first CSV file
with open('split_csv/output_file1.csv', 'r', newline='') as file1:
    reader1 = csv.reader(file1)
    data1 = list(reader1)

# Open and read the second CSV file
with open('split_csv/output_file2.csv', 'r', newline='') as file2:
    reader2 = csv.reader(file2)
    data2 = list(reader2)

# Combine the data from both files
combined_data = data1 + data2

# Write the combined data to a new CSV file
with open('merged_data.csv', 'w', newline='') as output_file:
    writer = csv.writer(output_file)
    writer.writerows(combined_data)

# Load the combined data into a DataFrame
music = pd.read_csv('merged_data.csv')

# Load the similarity matrix
similarity = pickle.load(open('similarity.pkl', 'rb'))

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

    # Return top N similar artists
    return similar_artists[:10]


# Function to recommend songs
def recommend(song):
    try:
        index = music[music['song'] == song].index[0]
        if index >= len(similarity):
            st.error("Error: Song index is out of bounds. Please try another song!")
            return []

        distances = sorted(enumerate(similarity[index]), key=lambda x: x[1], reverse=True)
        recommended_music_names = [(music.iloc[i[0]]['song'], music.iloc[i[0]]['artist'], music.iloc[i[0]]['text'][:100]) for i in distances[1:6]]

        return recommended_music_names
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
            st.subheader(f'Artists similar to {selected_artist}')
            for artist, similarity_score in similar_artists:
                st.write(f"{artist} (Similarity: {similarity_score:.2f})")
        else:
            st.error("No similar artists found.")

# Footer
st.markdown('<div class="team">© 2023 TechnoMelody</div>', unsafe_allow_html=True)
