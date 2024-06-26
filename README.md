# safefork

Safefork is a small utility to check if your program is safe to be forked.


## Motivation

In production environments, it’s common for web servers like [Gunicorn](https://docs.gunicorn.org/en/stable/settings.html#preload-app) and background task processors like [Celery](https://github.com/celery/celery/blob/main/celery/concurrency/prefork.py#L1) to offer a forking option. This forking approach can save significant memory and reduce startup times, but it can be difficult to audit if your application is safe to fork. It's even more difficult to maintain this safety as your application grows. Did a recent PR introduce a threaded metrics collector? Or maybe a threaded database connection pool?

Safefork tries to alleviate this problem by checking some common issues that can arise when forking. It ensures that there are no active threads, no pending signals, and no running event loops, and that the garbage collector has been configured to optimize memory savings.


## Installation

```console
pip install safefork
```

## Example Usage: Flask + Gunicorn

```py
## app.py
import gc
import flask
import safefork

# Disable GC until after we fork to avoid "memory holes".
gc.disable()

def create_app():
    app = flask.Flask(__name__)
    initialize_systems()
    # Freeze an object generation to maximize shared memory across forked childs.
    gc.freeze()
    assert safefork.is_safe_to_fork(), "Uh-oh! The application is unsafe to fork"
    return app

## gunicorn.conf.py
import gc

def post_fork(server, worker):
    """
    Called just after a worker has been forked.
    Enables garbage collection in the worker process.
    """
    gc.enable()
    server.log.info("Garbage collection enabled in worker process after fork.")

bind = '0.0.0.0:8000'
workers = 4


## Command to start application:
## gunicorn -c gunicorn.conf.py 'app:create_app()'
```

## Contribution

Contributions are welcome! If you would like to contribute to this project, please include an example script in the unsafe_examples/ directory demonstrating how forking can be unsafe. This will help me and others understand potential issues. Appreciate your help in making this project better!


[![PyPI - Version](https://img.shields.io/pypi/v/safefork.svg)](https://pypi.org/project/safefork)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/safefork.svg)](https://pypi.org/project/safefork)
