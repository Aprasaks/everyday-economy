"""Run on the owner's computer. Writes credentials privately; never prints tokens."""
import json
import os
from pathlib import Path


def main():
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json',
        scopes=['https://www.googleapis.com/auth/blogger'])
    credentials = flow.run_local_server(port=0, access_type='offline', prompt='consent')
    if not credentials.refresh_token:
        raise RuntimeError('No refresh token returned')
    config = json.loads(Path('client_secret.json').read_text())['installed']
    values = {'GOOGLE_CLIENT_ID': config['client_id'],
              'GOOGLE_CLIENT_SECRET': config['client_secret'],
              'GOOGLE_REFRESH_TOKEN': credentials.refresh_token}
    fd = os.open('google_credentials.env', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as file:
        file.write('\n'.join(f'{key}={value}' for key, value in values.items()) + '\n')
    print('Saved google_credentials.env privately. Copy values into the host secret settings.')


if __name__ == '__main__':
    main()
