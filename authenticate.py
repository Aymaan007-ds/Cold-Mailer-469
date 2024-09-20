from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os

# Define the OAuth 2.0 scopes your application will access
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    """Handles OAuth 2.0 authentication and stores the credentials in token.json."""
    creds = None

    # Check if token.json already exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If credentials are invalid or don't exist, initiate the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired credentials
            creds.refresh(Request())
        else:
            try:
                # Create the flow using the client secrets file from the Google API Console
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', SCOPES)
                # Run the local server to complete the authentication
                creds = flow.run_local_server(port=5001)
            except Exception as e:
                print("Error during authentication:", e)
                return None

        # Save the credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    print("Authentication successful! Credentials saved to token.json.")
    print("You can now send emails using the Gmail.")
    return creds

if __name__ == '__main__':
    authenticate_gmail()
