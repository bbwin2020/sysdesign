import redis
import time
import json
from flask import Flask, request
from functools import wraps

REDIS_DB = 0
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PASSWORD = ''
IP_LIMIT = 1
TIME_LIMIT = 36 # Default is 1 request per 36s (100request/3600s)

app = Flask(__name__)
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB, socket_timeout=3000)

class FinalRes(Exception):
    """Wrapper a class for final response"""
    def __init__(self, code, status=200, message=None):
        self.code = code
        self.status = status
        self.message = message


def obj_to_dict(obj):
   return obj.__dict__


@app.before_request  # App decorator, it's going to work on every request
def before_request():
    ip = request.remote_addr
    ip_count = r.get(ip)
    print("ip: %s, ip_count: %s" % (ip, ip_count))
    if not ip_count:
        r.set(ip, 1)
        r.expire(ip, TIME_LIMIT)
    else:
        r.incr(ip)  # Increment the numeric value stored in key by one
        if int(ip_count) > IP_LIMIT:
            res = FinalRes(429, "Failure", "Rate limit exceeded. Try again in 36 second!")
            json_string = json.dumps(res.__dict__,  default = obj_to_dict)
            return json.loads(json_string)


# Decorators limit access to 10 local caches per clock
def stat_called_time(func):
    limit_times = [10]  # A variable in the decorator inherits changes after each call, and the variable must be set to a variable type
    cache = {}

    @wraps(func)
    def _called_time(*args, **kwargs):
        key = func.__name__
        if key in cache.keys():
            [call_times, updatetime] = cache[key]
            if time.time() - updatetime < TIME_LIMIT:
                cache[key][0] += 1
            else:
                cache[key] = [1, time.time()]
        else:
            call_times = 1
            cache[key] = [call_times, time.time()]
        print('Number of call times: %s' % cache[key][0])
        print('Limited call times: %s' % limit_times[0])
        if cache[key][0] <= limit_times[0]:
            res = func(*args, **kwargs)
            cache[key][1] = time.time()
            return res
        else:
            print("Rate limit exceeded")
            res = FinalRes(429, "Failure", "Rate limit exceeded. Try again in 36 second!")
            json_string = json.dumps(res.__dict__,  default = obj_to_dict)
            return json.loads(json_string)

    return _called_time


@app.route("/call")
@stat_called_time
def home():
    res = FinalRes(200, "SUCCESS", "Response OK!")
    json_string = json.dumps(res.__dict__,  default = obj_to_dict)
    return json.loads(json_string)


@app.route("/")
def index():
    res = FinalRes(200, "SUCCESS", "Response OK!")
    json_string = json.dumps(res.__dict__,  default = obj_to_dict)
    return json.loads(json_string)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)