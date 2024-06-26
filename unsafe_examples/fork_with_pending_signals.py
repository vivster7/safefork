"""
This script demonstrates why it is unsafe to `os.fork()` in with pending signals.

Pending signals are not copied when using `os.fork()`. To demonstrate why this is unsafe:
  1. Schedule a pending signal
  2. Fork a child process
  3. The child process never receives the signal

To keep the signal in a pending state, we SIG_BLOCK the signal until we are ready for it.

Example running this script:
    >>> python tests/unsafe/fork_with_pending_signals.py
    2024-06-25 04:34:28,029 [55685] Main process ID: 55685
    2024-06-25 04:34:28,029 [55685] Signal 10 blocked in process 55685
    2024-06-25 04:34:28,029 [55685] Signal 10 sent to process 55685, but it is blocked and pending
    2024-06-25 04:34:28,030 [55685] Parent process 55685 forked child process 55686
    2024-06-25 04:34:28,030 [55685] Signal 10 received by process 55685
    2024-06-25 04:34:28,030 [55686] Child process 55686 continuing
    2024-06-25 04:34:28,030 [55685] Parent process 55685 unblocked SIGUSR1
    2024-06-25 04:34:28,030 [55686] Child process 55686 unblocked SIGUSR1

NOTE: The signal is not received by the child process.
"""

import logging
import os
import signal
import time

# Configure logging to show the thread and process ID
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(process)d] %(message)s")


# Register the signal handler
signal.signal(
    signal.SIGUSR1,
    lambda signum, frame: logging.info(
        f"Signal {signum} received by process {os.getpid()}"
    ),
)


def main():
    logging.info(f"Main process ID: {os.getpid()}")

    # Block SIGUSR1
    signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGUSR1})
    logging.info(f"Signal {signal.SIGUSR1} blocked in process {os.getpid()}")

    # Send SIGUSR1 to itself (it will remain pending)
    os.kill(os.getpid(), signal.SIGUSR1)
    logging.info(
        f"Signal {signal.SIGUSR1} sent to process {os.getpid()}, but it is blocked and pending"
    )

    pid = os.fork()

    if pid == 0:
        # Child process
        logging.info(f"Child process {os.getpid()} continuing")
        # Unblock SIGUSR1 in child
        signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGUSR1})
        logging.info(f"Child process {os.getpid()} unblocked SIGUSR1")
        # Sleep to ensure any pending signals would be handled
        time.sleep(1)
    else:
        # Parent process
        logging.info(f"Parent process {os.getpid()} forked child process {pid}")
        # Unblock SIGUSR1 in parent
        signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGUSR1})
        logging.info(f"Parent process {os.getpid()} unblocked SIGUSR1")
        # Sleep to ensure any pending signals would be handled
        time.sleep(1)


if __name__ == "__main__":
    main()
