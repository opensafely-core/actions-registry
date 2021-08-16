import pytest


# The following invocation allows all tests to access the database.
@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass
