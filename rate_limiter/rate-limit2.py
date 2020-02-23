import pysnooper
import time
import threading
from collections import deque


class FinalRes(Exception):
    """Wrapper a class for final response"""

    def __init__(self, message, status=400, payload=None):
        self.message = message
        self.status = status
        self.payload = payload


@pysnooper.snoop()
class RequestTimestamps(object):

    # lock is for concurrency in a multi threaded system
    # 100 req/hour translates to requests = 100 and windowTimeInSec = 3600

    def __init__(self, requests, windowTimeInSec):
        self.timestamps = deque()
        self.lock = threading.Lock()
        self.requests = requests
        self.windowTimeInSec = windowTimeInSec
        self.timePerReq = float(windowTimeInSec / requests)

    # eviction of timestamps older than the window time
    def evictOlderTimestamps(self, currentTimestamp):
        while len(self.timestamps) != 0 and (
                currentTimestamp - self.timestamps[0] > self.windowTimeInSec):
            self.timestamps.popleft()


@pysnooper.snoop()
class SlidingWindowRateLimiter(object):
    def __init__(self):
        self.lock = threading.Lock()
        self.ratelimiterMap = {}

    # Default of 100 req/hour
    # Add a new client with a request rate
    def addClient(self, clientId, requests=100, windowTimeInSec=3600):
        # hold lock to add in the client-metadata map
        with self.lock:
            if clientId in self.ratelimiterMap:
                raise Exception("Client already present")
            self.ratelimiterMap[clientId] = RequestTimestamps(requests,
                                                              windowTimeInSec)

    # Remove a client from the ratelimiter
    def removeClient(self, clientId):
        with self.lock:
            if clientId in self.ratelimiterMap:
                del self.ratelimiterMap[clientId]

    # gives current time epoch in seconds
    @classmethod
    def getCurrentTimestampInSec(cls):
        return int(round(time.time()))

    # Checks if the service call should be allowed or not
    def shouldAllowServiceCall(self, clientId):
        time.sleep(3)
        with self.lock:
            if clientId not in self.ratelimiterMap:
                raise Exception("Client is not present. Please white \
                    list and register the client for service")
        clientTimestamps = self.ratelimiterMap[clientId]
        with clientTimestamps.lock:
            currentTimestamp = self.getCurrentTimestampInSec()
            # remove all the existing older timestamps if the sliding window
            # is larger than windowTimeInSec
            clientTimestamps.evictOlderTimestamps(currentTimestamp)
            clientTimestamps.timestamps.append(currentTimestamp)
            print("clientId: {0}, clientTimestamps.timestamps: {1}, \
              requests: {2}, windowTimeInSec: {3}"
                  .format(clientId, clientTimestamps.timestamps,
                          clientTimestamps.requests,
                          clientTimestamps.windowTimeInSec))
            if len(clientTimestamps.timestamps) > clientTimestamps.requests:
                return FinalRes('Rate limit exceeded. Try again in {0} seconds'
                                .format(clientTimestamps.timePerReq),
                                429, {'ext': 1})
            return FinalRes('Success', 200, {'ext': 0})


if __name__ == '__main__':
    rl = SlidingWindowRateLimiter()
    clientId1 = '01'
    clientId2 = '02'
    rl.addClient(clientId1, 2, 60)
    rl.addClient(clientId2, 5, 60)
    for i in range(10):
        ret1 = rl.shouldAllowServiceCall(clientId1)
        ret2 = rl.shouldAllowServiceCall(clientId2)
        print("clientId1:{0},ret1:{1}".format(clientId1, ret1))
        print("clientId2:{0},ret2:{1}".format(clientId2, ret2))
        time.sleep(20)
