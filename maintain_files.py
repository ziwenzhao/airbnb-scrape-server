import glob
import os
import time
import threading

EXPIRE_TIME = 10 * 60 ## Expire Time For JSON Files
CLEAN_FILES_INTERVAL = 6 * 60 * 60  ## The interval of home json files cleaning task

def clean_files_periodically(application):
    application.logger.info('search all home json files')
    json_file_paths = glob.glob('./airbnb homes scrape/home_*.json')
    for path in json_file_paths:
        if time.time() - os.path.getmtime(path) > EXPIRE_TIME:
            os.remove(path)
    application.logger.info('cleared expired home json files')
    threading.Timer(CLEAN_FILES_INTERVAL, clean_files_periodically, [application]).start()
            
    
