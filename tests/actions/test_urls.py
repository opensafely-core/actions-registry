import importlib

from actions import urls


class TestDebugToolbarURLs:
    def test_settings_off(self, settings):
        """Test that when Django debug toolbar settings are off, the related
        URL patterns DO NOT appear in our URL configuration."""
        settings.DEBUG_TOOLBAR = False
        importlib.reload(urls)

        patterns = {str(p.pattern) for p in urls.urlpatterns}
        assert "__debug__/" not in patterns

    def test_settings_on(self, settings):
        """Test that when Django debug toolbar settings are on, the related
        URL patterns DO appear in our URL configuration."""
        settings.DEBUG_TOOLBAR = True
        settings.INSTALLED_APPS = ["debug_toolbar"]
        importlib.reload(urls)

        patterns = {str(p.pattern) for p in urls.urlpatterns}
        assert "__debug__/" in patterns
