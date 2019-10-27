import time
from watchdog.observers import Observer
from src.tray.ReplayCreatedHandler import ReplayCreatedHandler

class AutoRenamerThread:
    
    has_running_thread = False
    name = 0

    def __init__(self, settings):
        self.continue_running = False
        AutoRenamerThread.name += 1

        self.event_handler = ReplayCreatedHandler()
        self.observer = Observer()
        self.observer.schedule(self.event_handler, path=settings['source_dir'], recursive=False)
        
        self.name = AutoRenamerThread.name


    def start(self):
        if not AutoRenamerThread.has_running_thread:
            self.continue_running = True
            self.observer.start()
            print(self, "has been started")
            AutoRenamerThread.has_running_thread = True
        
        else:
            print("Only one instance of AutoRenamerThread can be run at a time")

    
    def stop(self):
        if self.continue_running:
            self.continue_running = False
            self.observer.stop()
            self.observer.join()
            print(self, "has been stopped")
            AutoRenamerThread.has_running_thread = False
        
        else:
            print(self, "has not been started")
    
    
    def __str__(self):
        return 'auto_renamer instance ' + str(self.name)