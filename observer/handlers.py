import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')

ENDPOINTS = {
    'doc.': os.getenv('DOC_UPLOAD_URL'),
    'Ack1.': os.getenv('ACK_UPLOAD_URL'),
    'Ack2.': os.getenv('ACK_UPLOAD_URL'),
    'UponDocInfo': os.getenv('UPON_UPLOAD_URL'),
    'Registration': os.getenv('REGISTRATION_UPLOAD_URL'),
}

def get_upload_url(file_name):
    for prefix, url in ENDPOINTS.items():
        if file_name.startswith(prefix):
            return url
    return None

def wait_until_file_is_ready(file_path, timeout=5, interval=0.25):
    try:
        last_size = -1
        for _ in range(int(timeout / interval)):
            current_size = os.stat(file_path).st_size
            if current_size == last_size:
                return True
            last_size = current_size
            time.sleep(interval)
    except Exception as e:
        print(f"Error while checking file size: {e}")
    return False

def upload_file(file_path):
    file_name = os.path.basename(file_path)
    upload_url = get_upload_url(file_name)

    if not upload_url:
        print(f"Ignoring unsupported file: {file_name}")
        return

    if not wait_until_file_is_ready(file_path):
        print(f"File not ready in time: {file_name}")
        return

    print(f"Uploading {file_name} to {upload_url}")
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()  # read the whole file into memory

        files = {'file': (file_name, file_content, 'application/xml')}
        headers = {'X-API-Key': f'{API_KEY}'}
        response = requests.post(upload_url, files=files, headers=headers)

        print(f"Uploaded {file_name} → {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error uploading {file_name}: {e}")
