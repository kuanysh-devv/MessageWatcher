import os
import json
import datetime
import requests

LOG_FILE = 'mw_errors.json'


def log_error(file_name, error_detail):
    log_entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + 'Z',
        "file_name": file_name,
        "error": error_detail
    }

    # Append to JSON log file
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r+', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
            data.append(log_entry)
            f.seek(0)
            json.dump(data, f, indent=2)
    else:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump([log_entry], f, indent=2)
