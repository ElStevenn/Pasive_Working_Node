from fastapi import APIRouter, Request
from fastapi import HTTPException
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from oauthlib.oauth2 import OAuth2Error
import warnings
from starlette.responses import RedirectResponse
from typing import Optional
import jwt, os

from services.database import crud
from services.google_oauth import get_credentials_from_code, get_google_flow, get_user_country

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="mini_frontend")

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv('')
EMAIL_SCOPES = [
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://mail.google.com/',
    ]
SPREADSHEET_SCOPES = [
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/spreadsheets',
]


@router.get("/google/email/login", description="Redirect the user to Google's OAuth login page to authenticate the email", include_in_schema=True)
async def authenticate_google_account_with_email():
    flow = get_google_flow(scopes=EMAIL_SCOPES)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
        state='email_auth'  
    )
    return RedirectResponse(authorization_url)

@router.get("/google/spreadsheet/login", description="Redirect the user to Google's OAuth login page to authenticate the spreadsheet", include_in_schema=True)
async def authenticate_google_acount_spreadsheet():
    flow = get_google_flow(scopes=SPREADSHEET_SCOPES)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
        state='spreadsheet_auth' 
    )
    return RedirectResponse(authorization_url)


@router.get("/google/callback", include_in_schema=True)
async def google_callback(code: str, state: str, request: Request, error: Optional[str] = None):
    if error == 'access_denied':
        return "<h1>Access denied. Please try again or contact support if the issue persists.</h1>"

    try:
        # Fetch the token without validating scopes
        credentials = get_credentials_from_code(code=code, state=state)

        id_token = credentials.id_token

        # Decode id_token to get user info
        decoded_token = jwt.decode(
            id_token,
            options={"verify_signature": False},
            audience=GOOGLE_CLIENT_ID
        )
        user_id = decoded_token.get('sub')
        user_email = decoded_token.get('email')
        user_name = decoded_token.get('name')
        user_picture = decoded_token.get('picture')

        if not user_email:
            raise HTTPException(status_code=400, detail="Email not found in token")

    except OAuth2Error as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch token from Google: {str(e)}")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="ID token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid ID token")

    # Optionally get the user's country from the Google People API
    user_country = get_user_country(credentials)

    # Register this user in the database if they don't already exist
    db_account = await crud.get_user_by_email(user_email)
    if not db_account:
        await crud.create_user(
            id=user_id,
            email=user_email,
            username=user_name,
            picture=user_picture,
            oauth_provider="google",
            country=user_country
        )

    await crud.set_user_token(user_id, credentials.token, credentials.refresh_token, "gmail" if state == 'email_auth' else 'spreadsheet')

    return templates.TemplateResponse(
        request=request, name="success_verified.html", context={"email": user_email, "name": str(user_name).upper(), "user_picture": user_picture}
    )


    """
    # Uncoment this if needed -> 
    return {
        "response": "success verified",
        "user_id": user_id,  
        "user_email": user_email,
        "user_name": user_name,
        "user_picture": user_picture,
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "expires_in": credentials.expiry,
        "user_country": user_country  
    }
    """
