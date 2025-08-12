# Sanic Concurrency Test

This folder contains a test setup to explore concurrency behavior in a Sanic application with multiple workers. The goal is to understand how Sanic handles requests when one worker is blocked on a long-running task (blockig IO for example), while other workers remain available to process non-blocking requests.

## Overview

The test involves two scripts:

1. **`app.py`**: Defines a Sanic server with two endpoints:
   - `/blocked`: Simulates a blocking operation that freezes the worker's event loop.
   - `/unblocked`: Simulates a non-blocking operation that should complete quickly.
   - The server is configured to run with multiple workers.

2. **`client.py`**: Simulates a client sending requests to the server:
   - Sends 1 request to the `/blocked` endpoint.
   - Sends 9 concurrent requests to the `/unblocked` endpoint.

### Expected Behavior

- The blocking request to `/blocked` should occupy one worker.
- The remaining 9 requests to `/unblocked` should be handled by the other available worker(s) without delay.

### Observed Behavior

- Requests are almost evenly distributed across workers.
- Some requests to `/unblocked` are delayed because they are assigned to the same worker that is blocked on the `/blocked` endpoint.
- This raises the question: **Why aren't all the remaining 9 requests to `/unblocked` handled by the unblocked worker?**

## File Descriptions

### `app.py`

This script defines the Sanic server with two endpoints:

- **`/blocked`**: Simulates a blocking operation using `time.sleep`, which freezes the worker's event loop.
- **`/unblocked`**: Simulates a non-blocking operation using `asyncio.sleep`, which allows the event loop to remain responsive.

The server is configured to run with multiple workers (e.g., `--workers=2`).

### `client.py`

This script simulates the client behavior:

- Sends 1 request to the `/blocked` endpoint to occupy one worker.
- Sends 9 concurrent requests to the `/unblocked` endpoint.
- Uses `aiohttp` to manage asynchronous HTTP requests.
- Demonstrates the issue of delayed responses for the `/unblocked` endpoint.

## How to Run

1. **Start the Sanic server**:
   ```
   python app.py
   ```
2. **Run the Client**:
   ```
   python client.py
   ```
3. **Observe the Output**
   ```
   # Server
   Main process started with PID: 13262
    Srv 0 2025-08-12 08:47:02 +0530 INFO:     Worker started with PID: 13269
    Srv 1 2025-08-12 08:47:02 +0530 INFO:     Worker started with PID: 13270
    Srv 0 2025-08-12 08:47:02 +0530 INFO:     Starting worker [13269]
    Srv 1 2025-08-12 08:47:02 +0530 INFO:     Starting worker [13270]
    Srv 0 2025-08-12 08:47:13 +0530 INFO:     Request 0 START on BLOCKED endpoint, worker PID: 13269
    Srv 1 2025-08-12 08:47:13 +0530 INFO:     Request 1 START on UNBLOCKED endpoint, worker PID: 13270
    Srv 1 2025-08-12 08:47:13 +0530 INFO:     Request 3 START on UNBLOCKED endpoint, worker PID: 13270
    Srv 1 2025-08-12 08:47:13 +0530 INFO:     Request 5 START on UNBLOCKED endpoint, worker PID: 13270
    Srv 1 2025-08-12 08:47:13 +0530 INFO:     Request 7 START on UNBLOCKED endpoint, worker PID: 13270
    Srv 1 2025-08-12 08:47:13 +0530 INFO:     Request 9 START on UNBLOCKED endpoint, worker PID: 13270
    Srv 1 2025-08-12 08:47:14 +0530 INFO:     Request 1 END on UNBLOCKED endpoint, worker PID: 13270
    Srv 1 2025-08-12 08:47:14 +0530 INFO:     Request 3 END on UNBLOCKED endpoint, worker PID: 13270
    Srv 1 2025-08-12 08:47:14 +0530 INFO:     Request 5 END on UNBLOCKED endpoint, worker PID: 13270
    Srv 1 2025-08-12 08:47:14 +0530 INFO:     Request 7 END on UNBLOCKED endpoint, worker PID: 13270
    Srv 1 2025-08-12 08:47:14 +0530 INFO:     Request 9 END on UNBLOCKED endpoint, worker PID: 13270
    Srv 0 2025-08-12 08:47:33 +0530 INFO:     Request 0 END on BLOCKED endpoint, worker PID: 13269
    Srv 0 2025-08-12 08:47:33 +0530 INFO:     Request 2 START on UNBLOCKED endpoint, worker PID: 13269
    Srv 0 2025-08-12 08:47:33 +0530 INFO:     Request 4 START on UNBLOCKED endpoint, worker PID: 13269
    Srv 0 2025-08-12 08:47:33 +0530 INFO:     Request 6 START on UNBLOCKED endpoint, worker PID: 13269
    Srv 0 2025-08-12 08:47:33 +0530 INFO:     Request 8 START on UNBLOCKED endpoint, worker PID: 13269
    Srv 0 2025-08-12 08:47:33 +0530 INFO:     Request 10 START on UNBLOCKED endpoint, worker PID: 13269
    Srv 0 2025-08-12 08:47:34 +0530 INFO:     Request 2 END on UNBLOCKED endpoint, worker PID: 13269
    Srv 0 2025-08-12 08:47:34 +0530 INFO:     Request 4 END on UNBLOCKED endpoint, worker PID: 13269
    Srv 0 2025-08-12 08:47:34 +0530 INFO:     Request 6 END on UNBLOCKED endpoint, worker PID: 13269
    Srv 0 2025-08-12 08:47:34 +0530 INFO:     Request 8 END on UNBLOCKED endpoint, worker PID: 13269
    Srv 0 2025-08-12 08:47:34 +0530 INFO:     Request 10 END on UNBLOCKED endpoint, worker PID: 13269
   ```
## Key Question: Why aren't all unblocked requests handled by the unblocked worker?
My expectation was that the blocking request would freeze the event loop of Worker-A and it won't
be able to accept() any more requests. Worker-B though would be able to concurrently run accept()
and process all other requests and hence all other request should be done by the time Worker-A unblocks.
However, it seems Worker-A did manage to win the accept() race for roughly half the requests which
could happen if the blocking code happended later in the handler as is the case here.

## Conclusion
This test highlights the importance of avoiding blocking operations in asynchronous frameworks like Sanic.
Understanding and addressing these limitations is crucial for building high-performance applications.

## Quick Points on Sanic's Runtime
* Each worker is a process
* Each worker runs an async event loop that await() incoming connection from the listening socket and processes the requests concurrently
* Blocking coroutine freezes that coroutine i,e no other request in that worker would make progress nor that worker's event loop will be able to accept() new connections from the kernel socket