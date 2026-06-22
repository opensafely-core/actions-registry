import logging
from os import environ
from pathlib import Path

import httpretty as _httpretty
import pytest


def remove_cache_file_if_exists():
    test_cache_path = Path(__file__).parent.parent / "test_cache.sqlite"
    if test_cache_path.exists():  # pragma: no cover
        test_cache_path.unlink()


def pytest_sessionstart(session):
    """
    Modify logging and clean up old test cache files before session starts

    requests_cache emits an annoying and unnecessary warning about unrecognised kwargs
    because we're using a custom cache name.  Set its log level to ERROR just for the tests
    """
    logger = logging.getLogger("requests_cache")
    logger.setLevel("ERROR")

    remove_cache_file_if_exists()


def pytest_sessionfinish(session, exitstatus):
    """clean up test cache files after session starts"""
    remove_cache_file_if_exists()  # pragma: no cover


@pytest.fixture
def httpretty():
    _httpretty.reset()
    _httpretty.enable()
    yield _httpretty
    _httpretty.disable()


@pytest.fixture
def reset_environment_after_test():
    old_environ = dict(environ)
    yield
    environ.clear()
    environ.update(old_environ)
