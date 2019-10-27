from watchdog.events import FileSystemEventHandler
import time
import sc2reader

class ReplayCreatedHandler(FileSystemEventHandler):
    """Used to handle the renaming once the replay file is generated"""
    
    def on_any_event(self, event):
        """Catch-all event handler."""

        print(f'event type: {event.event_type}')
        print(f'path: {event.src_path}')

    def on_created(self, event):
        """Called when a file or directory is created."""
        
        return None

    def on_modified(self, event):
        """Called when a file or directory is modified.
        Probably will have to use this one to prevent mess-ups"""
        
        return None

        