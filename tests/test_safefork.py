import gc
import os
import signal
import threading
import time
import unittest
import unittest.async_case

from safefork._safefork import (
    _check_gc_freeze_ran,
    _check_no_active_threads,
    _check_no_event_loop,
    _check_no_pending_signals,
)


class TestSafeFork(unittest.TestCase):
    def test_check_active_threads(self):
        self.assertEqual(_check_no_active_threads(), True)

        thread = threading.Thread(target=lambda: time.sleep(0.2))
        thread.start()
        self.assertEqual(_check_no_active_threads(), False)
        thread.join()
        self.assertEqual(_check_no_active_threads(), True)

    def test_check_gc_freeze_ran(self):
        self.assertEqual(_check_gc_freeze_ran(), False)
        gc.freeze()
        self.assertEqual(_check_gc_freeze_ran(), True)
        gc.unfreeze()
        self.assertEqual(_check_gc_freeze_ran(), False)

    def test_check_no_pending_signals(self):
        self.assertEqual(_check_no_pending_signals(), True)

        # add a pending signal
        signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGUSR1})
        signal.signal(signal.SIGUSR1, lambda x, y: None)
        os.kill(os.getpid(), signal.SIGUSR1)

        self.assertEqual(_check_no_pending_signals(), False)

        # unblock the signal
        signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGUSR1})

        self.assertEqual(_check_no_pending_signals(), True)

    def test_check_no_event_loop(self):
        self.assertEqual(_check_no_event_loop(), True)


class AsyncTestSafeFork(unittest.async_case.IsolatedAsyncioTestCase):
    async def test_check_no_event_loop(self):
        self.assertEqual(_check_no_event_loop(), False)
