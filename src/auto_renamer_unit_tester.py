from auto_renamer_thread import auto_renamer_thread as art

c = art("op")
b=art('op')
c.start()
b.start()
c.stop()
b.stop()
