class TestDebugToolbarURLs:
    def test_settings_on(self, settings, remove_from_module_cache):
        """Test that when Django debug toolbar settings are on, the related
        URL patterns DO appear in our URL configuration."""
        settings.DEBUG_TOOLBAR = True
        settings.INSTALLED_APPS = ["debug_toolbar"]

        remove_from_module_cache("actions.urls")
        import actions.urls

        patterns = {str(p.pattern) for p in actions.urls.urlpatterns}
        assert "__debug__/" in patterns

    def test_settings_off(self, settings, remove_from_module_cache):
        """Test that when Django debug toolbar settings are off, the related
        URL patterns DO NOT appear in our URL configuration."""
        settings.DEBUG_TOOLBAR = False

        remove_from_module_cache("actions.urls")
        import actions.urls

        patterns = {str(p.pattern) for p in actions.urls.urlpatterns}
        assert "__debug__/" not in patterns
