import pytest


@pytest.mark.parametrize(
    "debug, debug_toolbar, expected",
    [
        (True, True, True),
        (False, False, False),
    ],
)
def test_debug_toolbar_urls_are_toggled_by_relevant_settings(
    debug, debug_toolbar, expected, settings, remove_from_module_cache
):
    remove_from_module_cache("actions.urls")
    settings.DEBUG = debug
    settings.DEBUG_TOOLBAR = debug_toolbar

    # Only import actions.urls after settings are patched
    import actions.urls

    patterns = {str(p.pattern) for p in actions.urls.urlpatterns}
    assert ("__debug__/" in patterns) is expected
