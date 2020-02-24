# Question
To produce a rate-limiting module that stops a particular requestor
from making too many http requests within a particular period of time.

The module should expose a method that keeps track of requests and limits it
such that a requester can only make 100 requests per hour. After the limit has
been reached, return a 429 with the text "Rate limit exceeded. Try again in #{n}
seconds".

Although you are only required to implement the strategy described above, it
should be easy to extend the rate limiting module to take on different
rate-limiting strategies.

How you do this is up to you. Think about how easy your rate limiter will be to
maintain and control. Write what you consider to be production-quality code,
with comments and tests if and when you consider them necessary.