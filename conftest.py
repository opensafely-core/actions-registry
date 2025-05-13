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
    and again during the test's teardown.
    """
    teardown_targets = set()

    def _remove_from_module_cache(module_name):
        sys.modules.pop(module_name, None)
        teardown_targets.add(module_name)

    yield _remove_from_module_cache

    for module_name in teardown_targets:
        sys.modules.pop(module_name, None)
