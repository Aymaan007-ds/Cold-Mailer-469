# authenticate.py

import os
import json
from flask import session, redirect, url_for, request
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    """Handles OAuth 2.0 authentication and stores the credentials in the session."""
    creds = None

    # Check if credentials are stored in session
    if 'credentials' in session:
        creds = Credentials.from_authorized_user_info(session['credentials'], SCOPES)

    # If credentials are invalid or don't exist, initiate the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired credentials
            creds.refresh(Request())
            # Update the credentials in the session
            session['credentials'] = json.loads(creds.to_json())
        else:
            # Load client configuration from environment variable
            client_config = json.loads(os.environ.get('client_secret.json'))
            flow = Flow.from_client_config(
                client_config,
                scopes=SCOPES,
                redirect_uri=url_for('oauth2callback_route', _external=True)
            )

            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'  # Ensures a refresh token is received
            )

            # Store the state in the session
            session['state'] = state

            return redirect(authorization_url)

    return creds

def oauth2callback():
    """Handles the OAuth2 callback and saves the credentials in the session."""
    state = session.get('state', '')

    client_config = json.loads(os.environ.get('client_secret.json'))
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('oauth2callback_route', _external=True)
    )

    flow.fetch_token(authorization_response=request.url)

    creds = flow.credentials
    session['credentials'] = json.loads(creds.to_json())

    # Redirect back to the index page
    return redirect(url_for('index'))
