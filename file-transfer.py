import io
import os.path
from datetime import datetime
import os
import shutil
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

source_dir = '/Users/dangg/Desktop'
archive_dir = '/Users/dangg/Desktop/old'
prefix = 'All Isl Monthly Stats model.xlsx_'

os.makedirs(archive_dir, exist_ok=True)

for filename in os.listdir(source_dir):
    if filename.startswith(prefix):
        shutil.move(os.path.join(source_dir, filename),
                    os.path.join(archive_dir, filename))
        print(f"Moved {filename} to {archive_dir}")

# List all files that match the pattern
files = [f for f in os.listdir(archive_dir) if f.startswith(prefix)]

# Extract date from filename and sort (most recent first)
def extract_date(file):
    try:
        date_str = file.split('_')[-1]
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return datetime.min  # Push invalid or undated files to the end

# Sort by date defined on file name
files.sort(key=extract_date, reverse=True)

# Keep only the 5 most recent
for file in files[5:]:
    full_path = os.path.join(archive_dir, file)
    os.remove(full_path)
    print(f"Deleted: {file}")



def download_file(file_id, file_name):
    creds = None
    # Load existing token or go through OAuth flow
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save token for later
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(file_name, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
  download_file("14tAFXhstMir7ccOVMetQe6-20WERy_vZ", f"/Users/dangg/Desktop/All Isl Monthly Stats model.xlsx_{datetime.now().date()}")

