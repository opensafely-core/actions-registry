import sys
from contextlib import contextmanager

import pytest


# The following invocation allows all tests to access the database.
@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def remove_from_module_cache():
    """
    Get a context manager that removes a given module from sys.modules
    at the start and end of the context block.
    """

    @contextmanager
    def _remove_from_module_cache(module_name):
        sys.modules.pop(module_name, None)
        yield
        sys.modules.pop(module_name, None)

    return _remove_from_module_cache
