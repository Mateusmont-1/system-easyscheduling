import os
import datetime

class Logger:
    def __init__(self, log_dir='logs'):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _get_log_file(self):
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        return os.path.join(self.log_dir, f'log_{date_str}.txt')
    
    def log(self, operation, collection, document_id, data):
        log_entry = f"{datetime.datetime.now()} | Operation: {operation} | Collection: {collection} | Document ID: {document_id} | Data: {data}\n"
        log_file_path = self._get_log_file()
        with open(log_file_path, 'a') as log_file:
            log_file.write(log_entry)

logger = Logger()