# rate-limit1.py
## python flask has flask_limiter module, which can meet the requirement to limit request calls according to requester's IP address

  1) Use redis to store the call times for each ip address(I use my local redis server)
  

# rate-limit2.py Use sliding window log method for user's rate limit
By using google, I know that there are lots of method for server side rate limit.
eg:
 1) leaky Bucket
 2) Fixed window
 3) sliding window log

 Here I will use sliding window Log method.
 1) For each client, I have a RequestTimestamps object, which have timestamps, requests, windowTimeInSec properties
 2) This is a in memory design, so I use a dict called "ratelimiterMap" to store all the clientId and its corresponding RequestTimestamps properties. eg:
    {
      "clientId01": RequestTimestamps().
      "clientId02": RequestTimestamps()
    }
  3) timestamps property of RequestTimestamps is a deque(). Every time a new request is issued, we should judge if the time is in the sliding window, if true, return "SUCCESS", else return "429" and then empty the deque by using the "evictOlderTimestamps" function.

Test result for the method:
  1) Use main test method
  2) give example of two clientIds
  
