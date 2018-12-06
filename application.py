import os
import argparse
import sys
from apiclient.discovery import build


DEVELOPER_KEY = os.environ['YOUTUBE_API_KEY']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


def get_authenticated_service():
    return build(API_SERVICE_NAME, API_VERSION, developerKey=DEVELOPER_KEY)


def channels_list(client, **kwargs):
    """Returns a list of channels for given username
    """
    return client.channels().list(**kwargs).execute()


def search_list_by_keyword(client, **kwargs):
    """Returns a collection of search results that match
    the query parameters specified in the API request
    """
    return client.search().list(**kwargs).execute()


def get_channels(client, username):
    """Makes a request for list of channels based on channel name or id,
    also checks if channel exists
    """
    # Channels with spaces in their names can only be found through channel_id
    if ' ' in username:
        response = search_list_by_keyword(client, part='snippet',
                                          maxResults=1, q=username,
                                          type='channel')
        channel_id = response['items'][0]['id']['channelId']
        channels = channels_list(client, part='contentDetails', id=channel_id)
    else:
        channels = channels_list(client, part='contentDetails',
                                 forUsername=username)

    if not channels['items']:
        print('Channel not found')
        sys.exit(1)

    return channels


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


def get_videos(client, video_ids):
    """Makes a request for each video_id, extract title, like/dislike counts
    and bundle it all up in a list
    """
    videos = []

    # Can place at most 50 video_id's in a request
    beg = 0
    end = 49 if 49 <= len(video_ids) else len(video_ids)
    # Loop through every 50 indices of video_ids list
    while beg <= len(video_ids):
        ids_str = ','.join(video_ids[beg:end])
        response = videos_list_by_id(client, id=ids_str,
                                     part='snippet, statistics', maxResults=50)

        videos_part = []
        for item in response['items']:
            # Some videos have likes/dislikes disabled - skip them
            if 'likeCount' not in item['statistics']:
                continue

            title = item['snippet']['title']
            video_id = item['id']
            like_count = int(item['statistics']['likeCount'])
            dislike_count = int(item['statistics']['dislikeCount'])
            dtl_ratio = dislike_to_like_ratio(like_count, dislike_count)

            video_dict = {
                    'title': title,
                    'id': video_id,
                    'dtl_ratio': dtl_ratio,
                    'likes': like_count,
                    'dislikes': dislike_count}
            videos_part.append(video_dict)

        videos += videos_part

        beg = end + 1
        end = end + 50 if (end + 50) <= len(video_ids) else len(video_ids)

    return videos


def dislike_to_like_ratio(like_count, dislike_count):
    """Calculates controversiality rating based on like/dislike counts
    """
    total = like_count + dislike_count
    if total == 0:
        return 50.0
    else:
        return (dislike_count / total) * 100 if dislike_count != 0 else 0


def sort_by_dtl_ratio(videos):
    """Sorts a list of video objects by like/dislike ration in ascending order
    """
    return sorted(videos, key=lambda x: x['dtl_ratio'], reverse=True)


def print_controversial(videos, count):
    """Prints specified amount of most controversial videos
    """
    if (len(videos) < count):
        print("Channel doesn't have that many videos")
    else:
        for i in range(1, count+1):
            video = videos[i]
            print(f"{i}. {video['title']}\n"
                  f"Link: https://www.youtube.com/watch?v={video['id']}\n"
                  f"Likes: {video['likes']} Dislikes: {video['dislikes']}\n"
                  f"Ratio: {round(video['dtl_ratio'], 2)}")


def parse_args():
    """Get channel's name and optional count from the commandline
    """
    parser = argparse.ArgumentParser(
            description="Print youtube channel's controversial videos")
    parser.add_argument('channel', metavar='channel',
                        type=str, help="channel's name")
    parser.add_argument('--count', metavar='count',
                        type=int, help='amount of videos to print', default=5)
    args = vars(parser.parse_args())

    if args['count'] <= 0:
        print('Invalid result count')
        sys.exit(1)

    return args


if __name__ == '__main__':
    args = parse_args()
    username = args['channel']
    count = args['count']

    client = get_authenticated_service()
    channels = get_channels(client, username)

    uploads_playlist_id = (
            channels['items'][0]['contentDetails']
            ['relatedPlaylists']['uploads'])

    video_ids = extract_video_ids(client, uploads_playlist_id)
    videos = get_videos(client, video_ids)
    print_controversial(sort_by_dtl_ratio(videos), count)
