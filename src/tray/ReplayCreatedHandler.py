from watchdog.events import FileSystemEventHandler
import hashlib
import time
from datetime import datetime
import sc2reader
import os
from src.structures import defaults

class ReplayCreatedHandler(FileSystemEventHandler):
    """Used to handle the renaming once the replay file is generated
    
    Replay-saving sequence:
    Create Ephemeron LE (4).SC2Replay
    Create Ephemeron LE (4).SC2Replay.writeCacheBackup
    Modify Ephemeron LE (4).SC2Replay
    Delete Ephemeron LE (4).SC2Replay.writeCacheBackup
    Modify Ephemeron LE (4).SC2Replay
    """

    def __init__(self, settings):
        self.settings = settings
        self.hashes = set()
        FileSystemEventHandler.__init__(self)


    def on_created(self, event):
        """Called when a file or directory is created"""
        
        file = event.src_path
        
        if os.path.isfile(file) and os.path.splitext(file)[1] == '.SC2Replay':

            # sleeps for 1 second to make sure all the cache data is written to the replay file before we operate on it
            time.sleep(1)
            
            file_hash = self.get_hash(file)
            
            if file_hash in self.hashes:
                print(f'{os.path.split(file)[1]} has already been hashed')
                return None
            
            else:
                self.hashes.add(file_hash)
                print(f'event type: {event.event_type} at {datetime.now().strftime("%H:%M:%S")}')
                print(f'path: {event.src_path}')
                print(f'{self.hashes}', end='\n\n')


    def get_hash(self, file):
        """ Gets the md5 hash of the file """

        md5 = hashlib.md5()
        with open(file, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                md5.update(data)

        return md5.hexdigest()
