import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pymongo

# Set up the API client
youtube = build('youtube', 'v3', developerKey='AIzaSyA2t7_3fcDsDA00drph9nRERsI-QPnXgrQ')  # Replace with your YouTube API key

# Function to get channel ID from channel name or URL
def get_channel_id(input_text):
    if 'youtube.com' in input_text:
        match = re.search(r'/user/([^/]+)|/c/([^/]+)|/channel/([^/]+)', input_text)
        if match:
            return match.group(1) or match.group(2) or match.group(3)
    else:
        return input_text

# Function to save data to MongoDB
def save_to_mongodb(data):
    # Connect to MongoDB (replace with your MongoDB connection details)
    client = pymongo.MongoClient("mongodb+srv://anuprasad4444:1234567890@cluster0.nw9dkpu.mongodb.net/")
    db = client["YoutubeAnuprasad"]
    collection = db["streamlt1"]

    # Insert data into MongoDB
    collection.insert_many(data)

# Page Title
st.title("YouTube Channel Data Visualization")

# Input for YouTube Channel URL
channel_url = st.text_input("Enter the YouTube channel URL:")
channel_id = get_channel_id(channel_url)

if channel_id:
    try:
        # Make a request to retrieve all videos from the channel
        next_page_token = None
        videos = []

        while True:
            response = youtube.search().list(
                part='snippet',
                channelId=channel_id,
                type='video',
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            # Loop through the items in the API response and extract relevant information
            for item in response['items']:
                video_info = {
                    'channel': channel_id,
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt']
                }

                video_stats_response = youtube.videos().list(
                    part='statistics',
                    id=item['id']['videoId']
                ).execute()

                video_stats = video_stats_response['items'][0]['statistics']

                try:
                    video_info['likes'] = int(video_stats.get('likeCount', 0))
                except ValueError:
                    video_info['likes'] = 0

                try:
                    video_info['comments'] = int(video_stats.get('commentCount', 0))
                except ValueError:
                    video_info['comments'] = 0

                try:
                    video_info['views'] = int(video_stats.get('viewCount', 0))
                except ValueError:
                    video_info['views'] = 0

                videos.append(video_info)

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        # Save the video data to MongoDB
        save_to_mongodb(videos)

        # Data Visualization
        st.subheader("Data Visualization")
        plot_type = st.selectbox("Select a plot type", ["Histogram", "Bar Plot", "Scatter Plot"])
        data = pd.DataFrame(videos)

        if plot_type == "Histogram":
            column = st.selectbox("Select a column for the histogram", data.columns)
            plt.figure(figsize=(8, 6))
            plt.hist(data[column], bins=20)
            plt.xlabel(column)
            plt.ylabel("Frequency")
            st.pyplot()

        elif plot_type == "Bar Plot":
            x_axis = st.selectbox("Select the x-axis", data.columns)
            y_axis = st.selectbox("Select the y-axis", data.columns)
            plt.figure(figsize=(10, 6))
            sns.barplot(x=x_axis, y=y_axis, data=data)
            plt.xlabel(x_axis)
            plt.ylabel(y_axis)
            st.pyplot()

        elif plot_type == "Scatter Plot":
            x_axis = st.selectbox("Select the x-axis", data.columns)
            y_axis = st.selectbox("Select the y-axis", data.columns)
            plt.figure(figsize=(10, 6))
            sns.scatterplot(x=x_axis, y=y_axis, data=data)
            plt.xlabel(x_axis)
            plt.ylabel(y_axis)
            st.pyplot()

    except HttpError as e:
        st.error(f"An HTTP error occurred: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
