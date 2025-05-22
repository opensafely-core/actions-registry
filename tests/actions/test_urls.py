import sys

import pytest


@pytest.fixture
def clear_cached_urls_module():
    """
    Remove the actions.urls module from the module cache before and after the test.
    """
    sys.modules.pop("actions.urls", None)
    yield
    sys.modules.pop("actions.urls", None)


def test_debug_toolbar_urls_enabled_in_debug_mode(settings, clear_cached_urls_module):
    settings.DEBUG = True
    settings.DEBUG_TOOLBAR = True

    import actions.urls

    pattern = str(actions.urls.urlpatterns[-1].pattern)
    assert pattern == "__debug__/"


def test_debug_toolbar_urls_disabled_in_production(settings, clear_cached_urls_module):
    settings.DEBUG = False
    settings.DEBUG_TOOLBAR = False

    import actions.urls

    patterns = {str(p.pattern) for p in actions.urls.urlpatterns}
    assert "__debug__/" not in patterns
