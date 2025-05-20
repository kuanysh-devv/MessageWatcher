import time
import os
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

from django.core.management.base import BaseCommand
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
from observer.handlers import upload_file

load_dotenv()
WATCH_DIRECTORY = os.getenv('WATCH_DIRECTORY')

UPLOAD_QUEUE = Queue()
MAX_WORKERS = 20

class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.xml'):
            return
        print(f"New file detected: {event.src_path}")
        UPLOAD_QUEUE.put(event.src_path)

class Command(BaseCommand):
    help = 'Watches for new XML files and uploads them in parallel.'

    def handle(self, *args, **kwargs):
        if not WATCH_DIRECTORY:
            self.stderr.write("WATCH_DIRECTORY not set in .env")
            return

        observer = Observer()
        observer.schedule(FileHandler(), WATCH_DIRECTORY, recursive=False)
        observer.start()

        self.stdout.write(f"Watching directory: {WATCH_DIRECTORY}")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            def worker():
                while True:
                    file_path = UPLOAD_QUEUE.get()
                    if file_path is None:
                        break
                    executor.submit(upload_file, file_path)
                    UPLOAD_QUEUE.task_done()

            # Start background worker
            threading.Thread(target=worker, daemon=True).start()

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
                self.stdout.write("Stopping observer...")
            observer.join()
