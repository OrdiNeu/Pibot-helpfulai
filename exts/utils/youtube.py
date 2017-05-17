# YouTube hook for pibot
import sys

import httplib2

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

ERROR_COULD_NOT_FIND_USER = -1
ERROR_COULD_NOT_FIND_UPLOADS = -2

API = None  # Initialized to the Youtube object in init()
YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def init(secret_filename):
    """Initialize the YouTube API"""
    global API

    # Are you ready for some cargo cult programming?
    flow = flow_from_clientsecrets(secret_filename,
                                   #message=MISSING_CLIENT_SECRETS_MESSAGE,
                                   scope=YOUTUBE_READONLY_SCOPE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])   # This makes me feel weird
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        flags = argparser.parse_args()
        credentials = run_flow(flow, storage, flags)

    API = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                http=credentials.authorize(httplib2.Http()))

def grabUploadsByPlaylistId(playlist_id):
    """Helper function to get the upload IDs in the given playlist"""
    uploads = []
    try:
        uploads = API.playlistItems().list(
            playlistId=playlist_id,
            part="snippet",
            maxResults=50
        ).execute()
        test = uploads["items"][0]["snippet"]["resourceId"]["videoId"]
    except Exception:
        return ERROR_COULD_NOT_FIND_UPLOADS

    # Construct the response of youtube videoIds
    response = []
    for video in uploads["items"]:
        response.append(video["snippet"]["resourceId"]["videoId"])
    return response

def grabUploads(username):
    """Helper function to get the upload IDs from a particular user"""
    # Grab the list of uploads from the username provided
    playlist_id = ""
    try:
        uploads_list_id = API.channels().list(
            part="contentDetails",
            forUsername=username
        ).execute()
        playlist_id = uploads_list_id['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    except Exception:
        return ERROR_COULD_NOT_FIND_USER

    return grabUploadsByPlaylistId(playlist_id)
