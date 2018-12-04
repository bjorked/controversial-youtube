import os
import sys
from apiclient.discovery import build


DEVELOPER_KEY = os.environ['YOUTUBE_API_KEY']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


def get_authenticated_service():
    return build(API_SERVICE_NAME, API_VERSION, developerKey=DEVELOPER_KEY)


def channels_list_by_username(client, **kwargs):
    """Returns a list of channels for given username
    """
    return client.channels().list(**kwargs).execute()


def playlist_items_list_by_playlist_id(client, **kwargs):
    """Returns a list of playlist items for given playlist id
    """
    return client.playlistItems().list(**kwargs).execute()


def videos_list_by_id(client, **kwargs):
    """Returns a list of video objects for given video id
    """
    return client.videos().list(**kwargs).execute()


def extract_video_ids(client, playlist_id):
    """Given a playlist id, extracts video ID's and puts them in a list
    """
    response = playlist_items_list_by_playlist_id(
            client, part='contentDetails',
            maxResults=50, playlistId=playlist_id)

    video_ids = []
    while True:
        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        if 'nextPageToken' not in response:
            break
        else:
            token = response['nextPageToken']
            response = (
                    playlist_items_list_by_playlist_id(
                        client, part='contentDetails',
                        maxResults=50, pageToken=token,
                        playlistId=playlist_id))

    return video_ids


def get_video_stats(client, video_ids):
    """Get video stats for each video_id, extract what is needed
    and put in a list of dicts
    """
    videos = []
    for video_id in video_ids:
        response = videos_list_by_id(client,
                                     part='snippet, statistics', id=video_id)

        title = response['items'][0]['snippet']['title']
        likeCount = int(response['items'][0]['statistics']['likeCount'])
        dislikeCount = int(response['items'][0]['statistics']['dislikeCount'])
        ld_ratio = controversiality(likeCount, dislikeCount)

        video_dict = {
                'title': title,
                'id': video_id,
                'ld_ratio': ld_ratio}
        videos.append(video_dict)

    return videos


def controversiality(likeCount, dislikeCount):
    """Calculates controversiality rating based on like/dislike counts
    """
    total = likeCount + dislikeCount
    if total == 0:
        return 50.0
    else:
        return (dislikeCount / total) * 100 if dislikeCount != 0 else 100.0


def sort_by_controversiality(videos):
    """Sorts a list of video objects by like/dislike ration in ascending order
    """
    return sorted(videos, key=lambda x: x['ld_ratio'])


if __name__ == '__main__':
    if (len(sys.argv) > 1):
        username = sys.argv[1]
    else:
        print("Username not provided. Usage:\npython application.py username")
        sys.exit(1)

    client = get_authenticated_service()
    channels = channels_list_by_username(
            client, part='contentDetails', forUsername=username)

    uploads_playlist_id = (
            channels['items'][0]['contentDetails']
            ['relatedPlaylists']['uploads'])

    video_ids = extract_video_ids(client, uploads_playlist_id)
    videos = get_video_stats(client, video_ids)
