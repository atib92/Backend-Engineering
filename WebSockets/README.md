# Introduction
WebSockets allow bidirectional Client <-> Server communication. Without WebSockets, the traditional
way to achive bidirectional communication has been via Polling (Short/Long) or HTTP Streaming. More
on these later.

## Background
The standard HTTP Protocol is a Client(Request) -> (Response) Server model i,e a Client initiates a
HTTP Request to a Server and the Server responds with data in a HTTP Resonse. The model doesn't allow
a Server to send asynchronously to a Client i,e a Reponse without any Request. a.k.a there isn't a
way for Servers to "Push Notifications" to Clients. The traditional way to achieve this using the
standard HTTP Protocol is by Polling the Server for any data while the Server responds if it has some
data to send. Obviously Polling is resource intenseive (wasted connections and resources when there
is not data to send) and inefficient (Client's responsiveness takes a hit since data is queue in the
Server until it receives a Polling request). The two most common Server Push mechanism used are Long
Polling and HTTP Streaming. (covered in the Alternatives section)

## What are WebSockets ?


## Why do we need WebSockets

## Alternative ways to Push Notifications

### HTTP Short Polling
The Client keeps on Polling the Server for data. The server either responds with the Data when there
is any or sends an empty response when there isn't any data to push. The polling frequency of the
Client can be arrived at by considering the accepatable latency. However Short Polling is very ineff-
iecient in terms of the network/server + client resources used in establishing all these HTTP connections
over which no data is exchanged.


### HTTP Long Polling
The Client keeps on Polling the Server but the Server keeps the HTTP Connection open until there is
data to send. Once the Reponse is done, the Client Polls again (new Long Polling HTTP Request). This
improves upon Short Polling by minimizing resource usage of establishing multiple HTTP connections
for when there is no data to push. The subsequent Long Polling Request is only sent after the Server
responds with a Long Polling Response to the previous Long Polling Request.

Note: Both short and long Polling can be implemented either by non-persistent or persistent HTTP
connections. In the former, new Long Polling HTTP Requests are over a new TCP connection while in
the latter the same TCP connection is used.
Irrespective of that, each Polling Req/Resp is still
a complete HTTP Req/Resp msg and thereby containt all the HTTP Headers. For small Push messages
the headers can represent a large overhead.
Also, the OS allocates resources for any open TCP/IP and HTTP Connections. Too many of these open
connections can cause graceful degradation in performance. 

### HTTP Streaming
The Server keeps the http connection open indefinitely even after it has sent the response (unlike
long/shot polling where the connection is closed as soon as a response is sent). This significantly
reduces latency and overhead since new connections need not be established everytime. HTTP Streaming
allows Servers to push Chuncked pieces of information in the same response. Some of the common problems
with Http Streaming are a. Proxies: The Http Protocol allows for Proxies to be involved in the 
request-response exchange. There is no requirement for a Proxy to immediately forward partial response
and it is legal for these proxies to buffer chunks before sending the complete response to the Client. 
Streaming breaks in these cases. b. Client Buffering : A similar problem can happen on the Client side
where a client caches all the chucked response before building the complete response and making it
available to the application. There is nothing in the HTTP Protocol to prevent client from doing that.

## Common Use Cases
Instant messaging applications, Gaming applications, Video Calling applications, Finance Tickers,
Collab like Google Docs, etc...

# Links 
Websocket Protocol RFC : https://datatracker.ietf.org/doc/html/rfc6455 
For understanding Long Polling and HTTP Streaming which are precursors to websockets :  https://datatracker.ietf.org/doc/html/rfc6202 

## Building a chat app using WebSocket
