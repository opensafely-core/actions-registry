def test_debug_toolbar_settings_are_disabled_by_default(
    monkeypatch, remove_from_module_cache
):
    remove_from_module_cache("actions.settings")
    monkeypatch.delenv("DJANGO_DEBUG_TOOLBAR", raising=False)
    import actions.settings

    assert actions.settings.DEBUG_TOOLBAR is False
    assert "debug_toolbar" not in actions.settings.INSTALLED_APPS
    assert (
        "debug_toolbar.middleware.DebugToolbarMiddleware"
        not in actions.settings.MIDDLEWARE
    )


def test_debug_toolbar_settings_are_enabled_when_environment_variable_set_to_true(
    monkeypatch, remove_from_module_cache
):
    remove_from_module_cache("actions.settings")
    monkeypatch.setenv("DJANGO_DEBUG_TOOLBAR", "1")
    import actions.settings

    assert actions.settings.DEBUG_TOOLBAR
    assert "debug_toolbar" in actions.settings.INSTALLED_APPS
    assert (
        actions.settings.MIDDLEWARE[0]
        == "debug_toolbar.middleware.DebugToolbarMiddleware"
    ), "Django Debug Toolbar's middleware must come as early as possible"
