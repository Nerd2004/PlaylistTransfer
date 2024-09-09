import queue
import logging
from flask import Blueprint, Response, request, session
from flask_cors import CORS
import sys
import time

logging_bp = Blueprint('logging', __name__)
CORS(logging_bp, supports_credentials=True)
log_queue = queue.Queue()


# Dictionary to map user session IDs to log queues
user_log_queues = {}

def get_user_log_message(user_id):
    # Retrieve and return log messages for a specific user
    if user_id in user_log_queues and not user_log_queues[user_id].empty():
        return user_log_queues[user_id].get()
    return ''

def log_message(user_id, message):
    # Store the message in the log queue for the specific user
    if user_id not in user_log_queues:
        user_log_queues[user_id] = queue.Queue()
    user_log_queues[user_id].put(message)
    logging.info(message)  # Also log to the default logging output

@logging_bp.route('/logs')
def logs():
    user_id = session.get('email')  # Retrieve the user's session ID

    if not user_id:
        return Response("Unauthorized", status=401)
    def generate_logs():
        while True:
            log_message = get_user_log_message(user_id)
            if log_message:
                yield f'data: {log_message}\n\n'
            else:
                # Send a keep-alive message every 5 seconds
                yield ':keep-alive \n\n'
                # Flush the buffer to make sure the message is sent
                sys.stdout.flush()
                # Add a sleep interval to prevent the loop from running too frequently
                time.sleep(5)

    return Response(generate_logs(), mimetype='text/event-stream')



# import logging
# from flask import Blueprint, Response
# from flask_cors import CORS
# import redis
# import json
# from datetime import datetime
# import time
# import sys

# logging_bp = Blueprint('logging', __name__)
# CORS(logging_bp, supports_credentials=True)

# print("Initializing Redis client...", file=sys.stderr)
# try:
#     redis_client = redis.Redis(host='localhost', port=6379, db=0)
#     redis_client.ping()  # Test the connection
#     print("Redis connection successful", file=sys.stderr)
# except redis.exceptions.ConnectionError as e:
#     print(f"Failed to connect to Redis: {e}", file=sys.stderr)
#     raise

# def log_message(message):
#     print(f"Logging message: {message}", file=sys.stderr)
#     timestamp = datetime.now().isoformat()
#     log_entry = json.dumps({'timestamp': timestamp, 'message': message})
#     try:
#         redis_client.lpush('log_queue', log_entry)
#         redis_client.ltrim('log_queue', 0, 999)  # Keep only the last 1000 logs
#         print(f"Message pushed to Redis queue. Queue length: {redis_client.llen('log_queue')}", file=sys.stderr)
#     except redis.exceptions.RedisError as e:
#         print(f"Failed to push message to Redis: {e}", file=sys.stderr)
#     logging.info(message)  # Also log to the default logging output

# @logging_bp.route('/logs')
# def logs():
#     print("Logs route accessed", file=sys.stderr)
#     def generate_logs():
#         print("Starting log generation", file=sys.stderr)
#         pubsub = redis_client.pubsub()
#         pubsub.subscribe('log_channel')
#         print("Subscription successful", file=sys.stderr)
#         yield("kuch to log dikha de bhai\n\n")
#         for message in pubsub.listen():
#             if message['type'] == 'message':
#                 print(f"Received message from Redis: {message['data']}", file=sys.stderr)
#                 yield f"data: {message['data'].decode('utf-8')}\n\n"
#             else:
#                 yield(f"data: Waiting for logs\n\n")

#     return Response(generate_logs(), mimetype='text/event-stream')

# def publish_logs():
#     print("Starting publish_logs function", file=sys.stderr)
#     while True:
#         try:
#             log_entry = redis_client.rpop('log_queue')
#             if log_entry:
#                 print(f"Publishing log entry: {log_entry}", file=sys.stderr)
#                 redis_client.publish('log_channel', log_entry)

#         except redis.exceptions.RedisError as e:
#             print(f"Error in publish_logs: {e}", file=sys.stderr)
#         time.sleep(0.1)  # Adjust as needed

# print("Logging manager initialized", file=sys.stderr)