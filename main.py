from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pycoingecko import CoinGeckoAPI
import requests
import os
import json

# Twitter Bearer Token for @intern_davisc
bearer_token = "AAAAAAAAAAAAAAAAAAAAANAhhAEAAAAA0azzTujSXV1w58A0x26V1cfvzh8%3DPhdd95xnQvrn6d8vPixNGno0fEwN9Y7vKVpjW37sThipY2reqt"

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1rGBynD_Z8ML2bcxQOgRWVpSfKSBT7LrPs5uOVygmXcw'
SAMPLE_RANGE_NAME = 'A1:E10'

cg = CoinGeckoAPI()


def create_url(users):
    # Specify the usernames that you want to lookup below
    # You can enter up to 100 comma-separated values.
    # EXAMPLE: usernames = "usernames=TwitterDev,TwitterAPI"
    usernames = "usernames=" + users
    user_fields = "user.fields=public_metrics"
    # User fields are adjustable, options include:
    # created_at, description, entities, id, location, name,
    # pinned_tweet_id, profile_image_url, protected,
    # public_metrics, url, username, verified, and withheld
    url = "https://api.twitter.com/2/users/by?{}&{}".format(usernames, user_fields)
    return url


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserLookupPython"
    return r


def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth,)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def update_values(creds, range_name, value_input_option,
                  _values):
    """
    Creates the batch_update the user has access to.
    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
        """
    # pylint: disable=maybe-no-member
    try:
        service = build('sheets', 'v4', credentials=creds)
        values = [
            [
                # Cell values ...
            ],
            # Additional rows ...
        ]
        body = {
            'values': _values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


# TODO: Change param + output to array
def get_twitter_followers(users):
    users_str = ""
    users_ar = []
    try:
        for u in users:
            users_str = users_str + u + ","
        url = create_url(users_str)
        json_response = connect_to_endpoint(url)
        print(json.dumps(json_response, indent=4, sort_keys=True))
    except:
        return 'n/a'


def get_token_ticker(tids):
    tids_ar = []
    for t in tids:
        try:
            tids_ar.append(cg.get_coin_by_id(t)['tickers'][0]['base'])
        except:
            tids_ar.append('n/a')
    return tids_ar


def get_token_address(tad):
    tad_ar = []
    for t in tad:
        try:
            tad_ar.apppend(cg.get_coin_by_id(t)['contract_address'])
        except:
            tad_ar.append('n/a')
    return tad_ar


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/Users/davischeng/Desktop/client_secret_491554625934-rr7gfbt99rp0utp3n2vlcdv3iu84h0mk.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return

        print(values)

    except HttpError as err:
        print(err)

    # TODO: make it write the relevant data
    update_values(creds, "A1:C2", "USER_ENTERED",
                  [
                      ['A', 'B'],
                      ['C', 'D']
                  ])


if __name__ == '__main__':
    main()

