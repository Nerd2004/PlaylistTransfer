import queue
import logging
from flask import Blueprint, Response
from flask_sse import sse
from flask_cors import CORS

logging_bp = Blueprint('logging', __name__)
CORS(logging_bp, supports_credentials=True)
log_queue = queue.Queue()

def get_log_message():
    if not log_queue.empty():
        return log_queue.get()
    else:
        return ''

def log_message(message):
    log_queue.put(message)
    logging.info(message)  # Also log to the default logging output

@logging_bp.route('/logs')
def logs():
    def generate_logs():
        while True:
            log_message = get_log_message()
            if log_message:
                yield f'data: {log_message}\n\n'
    return Response(generate_logs(), mimetype='text/event-stream')