import importlib

import actions.settings


def test_debug_toolbar_settings_are_toggled_by_environment_variable(monkeypatch):
    # Setup / Exercise
    # It is not possible to patch at import time, so reload the module
    with monkeypatch.context() as monkeypatch:
        monkeypatch.setenv("DJANGO_DEBUG_TOOLBAR", "1")
        importlib.reload(actions.settings)

    # Assert
    assert actions.settings.DEBUG_TOOLBAR is True
    assert "debug_toolbar" in actions.settings.INSTALLED_APPS
    assert (
        "debug_toolbar.middleware.DebugToolbarMiddleware" in actions.settings.MIDDLEWARE
    )

    # Teardown
    importlib.reload(actions.settings)
    assert actions.settings.DEBUG_TOOLBAR is False  # Check teardown is successful
