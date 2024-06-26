"""
This script demonstrates why it is unsafe to `os.fork()` in a multithreaded environment.

Threads are NOT copied when using `os.fork()`. To demonstrate why this is unsafe:
  1. Acquire a lock in a thread
  2. Fork a child process
  3. Try and fail to access the lock in the child process

Because the thread was not copied into the child process, the child process is unable
to acquire the lock. It's being held by a thread that does not exist in the child process.

ASCII digram:

                                               ┌───────────────────┐
                                               │                   │
                                               │                   │
                                  ┌───────────►│   PARENT PROCESS  │
                                  │            │         ┌─────────┐
                                  │            │         │ THREAD  │
                                  │            └──────── └─────────┘
                                  │
    ┌───────────────────┐         │              │x│
    │                   │         │              └─┘
    │                   │         │             LOCK
    │    MAIN PROCESS   ├─────────┤
    │ (BECOMES PARENT)  │         │
    │         ┌─────────┐         │
    │         │ THREAD  │         │
    └─────────└─────────┘         │
                                  │
      │x│                         │
      └─┘                         │            ┌───────────────────┐
     LOCK                         │            │                   │
                                  │            │                   │
                                  │            │   CHILD PROCESS   │
                                  └───────────►│ (NOTE: NO THREAD) │
                                               │                   │
                                               └───────────────────┘

                                                 │x│
                                                 └─┘
                                                LOCK

"""

import logging
import os
import threading
import time

# Configure logging to show the thread and process ID
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(process)d] [%(threadName)s] %(message)s"
)

# Shared lock
lock = threading.Lock()


def thread_function():
    logging.info("Thread starting, acquiring lock")
    lock.acquire()
    logging.info("Lock acquired by thread")

    # Simulate long operation
    time.sleep(1)

    logging.info("Thread releasing lock")
    lock.release()
    logging.info("Thread released lock")


def main():
    thread = threading.Thread(target=thread_function, name="WorkerThread")
    thread.start()

    # Ensure the thread is holding the lock while parent forks
    time.sleep(0.2)

    logging.info("Main process about to fork")
    pid = os.fork()

    if pid == 0:
        # Child process unable to access lock
        logging.info(
            "Forked child process started, trying to acquire lock, but will be stuck"
        )
        lock.acquire()

        # Never gets here
        logging.info("This message will not be print")

    else:
        # Parent process can still access the lock
        logging.info(f"Forked parent process, forked child PID: {pid}")
        thread.join()

        logging.info("Forked parent process, acquiring lock")
        lock.acquire()
        logging.info("Lock acquired by thread")

        logging.info("Forked parent process releasing lock")
        lock.release()
        logging.info("Forked parent process released lock")

        # This line keeps the parent process alive so we can ctrl+c out of the program.
        os.waitpid(pid, 0)


if __name__ == "__main__":
    main()
