from actions import urls


def test_something_to_do_with_urls():
    patterns = {str(p.pattern) for p in urls.urlpatterns}
    assert "__debug__/" in patterns
