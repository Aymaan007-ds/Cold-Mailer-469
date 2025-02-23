import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the Gmail API scope (modify if needed)
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Choose the port for the OAuth callback (must be registered in your redirect URIs)
OAUTH_PORT = 62348  # or use 62348

def get_credentials():
    """
    Obtains user credentials:
      - If 'credentials.json' exists, loads and returns them.
      - Otherwise, runs the OAuth flow using 'client_secret.json' with forced re-consent,
        saves the credentials (including a refresh token) to 'credentials.json', and returns them.
    """
    creds = None
    if os.path.exists('credentials.json'):
        creds = Credentials.from_authorized_user_file('credentials.json', SCOPES)
        print("Loaded credentials from credentials.json")
    else:
        # Force the consent screen and request offline access to always get a refresh token.
        flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
        creds = flow.run_local_server(port=OAUTH_PORT, prompt='consent', access_type='offline')
        # Save the credentials for future use
        with open('credentials.json', 'w') as token:
            token.write(creds.to_json())
        print("Saved new credentials to credentials.json")
    return creds

def main():
    creds = get_credentials()
    print("User authenticated successfully!")

if __name__ == '__main__':
    main()
