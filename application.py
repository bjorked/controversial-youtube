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


if __name__ == '__main__':
    if (len(sys.argv) > 1):
        username = sys.argv[1]
    else:
        print("Username not provided. Usage:\npython application.py username")

    client = get_authenticated_service()
    channels = channels_list_by_username(
            client, part='contentDetails', forUsername=username)