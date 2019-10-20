import threading


class auto_renamer_thread:
    
    has_running_thread = False
    name = 0


    def __init__(self, operation):
        self.continue_running = False
        auto_renamer_thread.name += 1
        self.thread = threading.Thread(target=self.auto_rename, name=auto_renamer_thread.name, args=(operation,))


    def auto_rename(self, operation):
        while self.continue_running:
            print("running")


    def start(self):
        if not auto_renamer_thread.has_running_thread:
            self.continue_running = True
            self.thread.start()
            auto_renamer_thread.has_running_thread = True
        
        else:
            print("Only one instance of auto_renamer_thread can be run at a time")

    
    def stop(self):
        if self.thread.is_alive():
            self.continue_running = False
            self.thread.join()
            print(self, "has been stopped")
            auto_renamer_thread.has_running_thread = False
        
        else:
            print(self, "has not been started")
    
    
    def __str__(self):
        return 'auto_renamer_thread instance ' + self.thread.name