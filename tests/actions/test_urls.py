def test_debug_toolbar_urls_enabled_when_corresponding_settings_set_to_true(
    settings, remove_from_module_cache
):
    with remove_from_module_cache("actions.urls"):
        settings.DEBUG = True
        settings.DEBUG_TOOLBAR = True

        # Only import actions.urls after settings are patched
        import actions.urls

        pattern = str(actions.urls.urlpatterns[-1].pattern)
        assert pattern == "__debug__/"


def test_debug_toolbar_urls_disabled_when_corresponding_settings_set_to_false(
    settings, remove_from_module_cache
):
    with remove_from_module_cache("actions.urls"):
        settings.DEBUG = False
        settings.DEBUG_TOOLBAR = False

        # Only import actions.urls after settings are patched
        import actions.urls

        patterns = {str(p.pattern) for p in actions.urls.urlpatterns}
        assert "__debug__/" not in patterns
