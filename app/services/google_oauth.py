from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()


GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')


def get_google_flow(scopes: list):
    return Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uris": [GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=scopes,
        redirect_uri=GOOGLE_REDIRECT_URI
    )

def get_credentials_from_code(code, state):
    if state == 'email_auth':
        flow = get_google_flow([
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://mail.google.com/',
        ])
        flow.fetch_token(code=code)
        return flow.credentials
    elif state == 'spreadsheet_auth':
        flow = get_google_flow([
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/spreadsheets',
        ])
        flow.fetch_token(code=code)
        return flow.credentials


def get_google_email_service(credentials):
    return build('gmail', 'v1', credentials=credentials, static_discovery=False)

def get_user_country(credentials):
 
    service = build('people', 'v1', credentials=credentials)
    profile = service.people().get(resourceName='people/me', personFields='addresses').execute()
    addresses = profile.get('addresses', [])
    if addresses:
        return addresses[0].get('country')
    return None
