"""
This script demonstrates why it is unsafe to `os.fork()` in with asyncio tasks.

The event loop is NOT copied when using `os.fork()`. To demonstrate why this is unsafe:
  1. Schedule an asyncio task
  2. Fork a child process
  3. The child process crashes as it resumes the asyncio task.


Example running this script:
    >>> python tests/unsafe/fork_with_asyncio_loop.py
    2024-06-25 01:26:04,089 [49930] Using selector: EpollSelector
    2024-06-25 01:26:04,090 [49930] Main function in process 49930
    2024-06-25 01:26:04,090 [49930] Task started in process 49930
    2024-06-25 01:26:05,097 [49930] Parent process 49930 forked child process 49932
    2024-06-25 01:26:05,098 [49932] Child process 49932 continuing the event loop
    Traceback (most recent call last):
    File "/workspaces/Code/safefork/tests/unsafe/fork_with_asyncio_loop.py", line 45, in <module>
        asyncio.run(main())
    File "/usr/lib/python3.10/asyncio/runners.py", line 44, in run
        return loop.run_until_complete(main)
    File "/usr/lib/python3.10/asyncio/base_events.py", line 649, in run_until_complete
        return future.result()
    File "/workspaces/Code/safefork/tests/unsafe/fork_with_asyncio_loop.py", line 42, in main
        await asyncio.sleep(2)
    File "/usr/lib/python3.10/asyncio/tasks.py", line 599, in sleep
        loop = events.get_running_loop()
    RuntimeError: no running event loop
    2024-06-25 01:26:06,093 [49930] Task completed in process 49930
"""

import asyncio
import logging
import os

# Configure logging to show the thread and process ID
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(process)d] %(message)s")


async def pending_task():
    logging.info(f"Task started in process {os.getpid()}")
    await asyncio.sleep(2)
    logging.info(f"Task completed in process {os.getpid()}")


async def main():
    logging.info(f"Main function in process {os.getpid()}")
    asyncio.create_task(pending_task())
    await asyncio.sleep(1)  # Give the task a chance to start

    # Fork the process
    pid = os.fork()

    if pid == 0:
        # Child process
        logging.info(f"Child process {os.getpid()} continuing the event loop")

        # child process crashes with `RuntimeError: no running event loop`
    else:
        # Parent process
        logging.info(f"Parent process {os.getpid()} forked child process {pid}")

    await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
