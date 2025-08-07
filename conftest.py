import sys

import pytest


# The following invocation allows all tests to access the database.
@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def remove_from_module_cache():
    """
    Factory fixture to remove a given module from sys.modules when called,
    and restore it during the test's teardown.
    """
    saved_modules = set()

    def _remove_from_module_cache(module_name):
        module_to_cache = sys.modules.pop(module_name, None)
        if module_to_cache is not None:
            saved_modules.add(module_to_cache)

    yield _remove_from_module_cache

    for module in saved_modules:
        sys.modules[module.__name__] = module
