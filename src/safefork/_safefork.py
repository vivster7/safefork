import asyncio
import gc
import logging
import os
import signal
import threading

logger = logging.getLogger(__name__)


class UnsafeForkError(Exception):
    """Custom exception raised when it's unsafe to fork."""

    pass


def safefork() -> int:
    """
    Forks the current process if it's safe to do so.

    This is an alternative to `os.fork()`.

    Returns:
        int: The PID of the child process in the parent, and 0 in the child.

    Raises:
        UnsafeForkError: If it is determined to be unsafe to fork.
    """
    if is_safe_to_fork():
        return os.fork()
    else:
        raise UnsafeForkError("Unsafe to fork.")


def is_safe_to_fork() -> bool:
    """
    Checks if it is safe to fork the current process.

    Returns:
        bool: True if it is safe to fork, False otherwise.
    """
    checks = [
        _check_no_active_threads(),
        _check_no_pending_signals(),
        _check_no_event_loop(),
        _check_gc_freeze_ran(),
    ]
    return all(checks)


def _check_no_active_threads() -> bool:
    threads = threading.enumerate()

    # First thread is main thread and should not be counted
    if len(threads) > 1:
        logger.warning(
            "Active threads detected. All threads should be `join()` before forking. See unsafe_examples/fork_with_threads.py"
        )
        for thread in threads:
            logger.warning(f"Thread: {thread.name} (ID: {thread.ident})")
        return False
    return True


def _check_no_pending_signals() -> bool:
    pending_signals = signal.sigpending()
    if pending_signals:
        logger.warning(
            "Pending signals detected. Signal handler should be registered after forking. See unsafe_examples/fork_with_signals.py"
        )
        for signum in pending_signals:
            logger.warning(f"Pending signal: {signum}")
        return False
    return True


def _check_no_event_loop() -> bool:
    try:
        asyncio.get_running_loop()
        logger.warning(
            "Event loop detected. Event loops should be stopped before forking. See unsafe_examples/fork_with_asyncio_loop.py"
        )
        return False
    except RuntimeError:
        return True


def _check_gc_freeze_ran() -> bool:
    freeze_count = gc.get_freeze_count()
    if freeze_count == 0:
        logger.warning(
            "It's recommended to run `gc.freeze()` before forking to avoid 'holes' in memory. "
            "You likely want to `gc.disable()` before forking and `gc.enable()` after forking. "
            "See https://docs.python.org/3/library/gc.html#gc.freeze"
        )
        return False
    return True
