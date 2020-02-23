import redis
import time
from flask import Flask, jsonify, request
from functools import wraps

REDIS_DB = 0
REDIS_HOST = '172.16.4.120'
REDIS_PORT = 6379
REDIS_PASSWORD = ''
IP_LIMIT = 10
TIME_LIMIT = 60

app = Flask(__name__)
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB, socket_timeout=3000)


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
            return jsonify({'code': 401, 'status': "reach the ip limit", 'message': {}})


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
            return jsonify({'code': 429, 'status': "Rate limit exceeded. Try again in **
seconds", 'message': {}})

    return _called_time


@app.route("/call")
@stat_called_time
def home():
    return jsonify({'code': 200, 'status': "SUCCESS", 'message': {}})


@app.route("/")
def index():
    return jsonify({'code': 200, 'status': "SUCCESS", 'message': {}})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)
参考文档