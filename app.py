from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from collections import defaultdict

app = Flask(__name__)
CORS(app)

#Rate limit settings
WINDOW = 60          #seconds (sliding window)
MAX_REQUESTS = 10    #max requests per window (sliding window)

BUCKET_CAPACITY = 10          #max tokens
REFILL_RATE = 10 / 60         #tokens per second 10 per min

ALGORITHM = 'token_bucket'  #sliding_window or token_bucket

#Space
request_log = defaultdict(list)   #timestamps for each IP
buckets = {}                       #token bucket, state per IP


#Sliding window technique, interchangeable
def is_rate_limited_sliding(ip):
    now = time.time()
    window_start = now - WINDOW #Since we used time(), its UNIX, time since midnight Jan 1 1970, easiest for tracking

    request_log[ip] = [t for t in request_log[ip] if t > window_start] #trash old reqs

    if len(request_log[ip]) >= MAX_REQUESTS:
        return True

    request_log[ip].append(now)
    return False


#Bucket of tokens
def is_rate_limited_bucket(ip):
    now = time.time()

    if ip not in buckets:
        # New IP gets a full bucket
        buckets[ip] = {'tokens': BUCKET_CAPACITY, 'last_refill': now}

    bucket = buckets[ip]

    #Refill tokens
    elapsed = now - bucket['last_refill']   #seconds since last refill,if 6 / elapes = 6
    bucket['tokens'] = min(BUCKET_CAPACITY, bucket['tokens'] + elapsed * REFILL_RATE) #refill tokens based on elapsed time, cap at max capacity
    bucket['last_refill'] = now  #resets refill clock 

    if bucket['tokens'] < 1:
        return True

    bucket['tokens'] -= 1
    return False



@app.route('/api/data')
def data():
    ip = request.remote_addr

    if ALGORITHM == 'token_bucket':
        limited = is_rate_limited_bucket(ip)
    else:
        limited = is_rate_limited_sliding(ip)

    if limited:
        return jsonify({
            'error': 'Rate limit exceeded. Try again later.',
            'algorithm': ALGORITHM
        }), 429

    return jsonify({
        'message': 'Success',
        'data': 'Here is your data',
        'algorithm': ALGORITHM
    })


if __name__ == '__main__':
    app.run(debug=True)