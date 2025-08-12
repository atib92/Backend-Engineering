# app.py
from sanic import Sanic, response
from sanic.log import logger
import asyncio
import os
import time

app = Sanic("worker_test")
app.config.FALLBACK_ERROR_FORMAT = "json"

@app.listener("main_process_start")
def main_process_start(app, loop):
    print(f"Main process started with PID: {os.getpid()}")

@app.listener("after_server_start")
async def after_server_start(app, loop):
    worker_pid = os.getpid()
    logger.info(f"Worker started with PID: {worker_pid}")
    
@app.route("/blocked")
async def blocked_endpoint(request):
    worker_pid = os.getpid()
    request_id = request.args.get("id")
    logger.info(f"Request {request_id} START on BLOCKED endpoint, worker PID: {worker_pid}")
    # Simulate blocking IO
    time.sleep(20)  # This will block the entire event loop for 5 seconds
    logger.info(f"Request {request_id} END on BLOCKED endpoint, worker PID: {worker_pid}")
    return response.json({"message": f"Request {request_id} processed by worker {worker_pid}"})

@app.route("/unblocked")
async def unblocked_endpoint(request):
    worker_pid = os.getpid()
    request_id = request.args.get("id")
    logger.info(f"Request {request_id} START on UNBLOCKED endpoint, worker PID: {worker_pid}")
    await asyncio.sleep(0.1)  # Simulate a non-blocking delay
    logger.info(f"Request {request_id} END on UNBLOCKED endpoint, worker PID: {worker_pid}")
    return response.json({"message": f"Request {request_id} processed by worker {worker_pid}"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, workers=2)