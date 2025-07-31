import pytest


@pytest.mark.parametrize(
    "django_debug_toolbar_value, expected",
    [
        ("1", True),
        ("0", False),
    ],
)
def test_debug_toolbar_urls_are_toggled_by_environment_variable(
    django_debug_toolbar_value,
    expected,
    settings,
    remove_from_module_cache,
    monkeypatch,
):
    remove_from_module_cache("actions.settings")
    remove_from_module_cache("actions.urls")
    monkeypatch.setenv("DJANGO_DEBUG_TOOLBAR", django_debug_toolbar_value)

    # Patch settings based on imported actions.settings
    import actions.settings

    settings.DEBUG = actions.settings.DEBUG
    settings.DEBUG_TOOLBAR = actions.settings.DEBUG_TOOLBAR
    settings.INSTALLED_APPS = actions.settings.INSTALLED_APPS

    # Only import actions.urls after settings are patched
    import actions.urls

    patterns = {str(p.pattern) for p in actions.urls.urlpatterns}
    assert ("__debug__/" in patterns) is expected
