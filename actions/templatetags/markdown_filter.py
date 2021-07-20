import bleach
import pycmarkgfm
from django import template
from django.conf import settings


def apply_css(markdown_str: str) -> str:
    markdown_str = markdown_str.replace(
        "<h3>", '<h3 class="text-sm font-semibold text-gray-600"> '
    )
    markdown_str = markdown_str.replace(
        "<p>", '<p class="mt-1 text-sm text-gray-900"> '
    )
    markdown_str = markdown_str.replace("<h5>", '<h5 class="text-sm font-semibold"> ')
    markdown_str = markdown_str.replace("<ul>", '<div class="list-disc">')

    return markdown_str


register = template.Library()


@register.filter
def markdown_filter(text):
    gfm_text = pycmarkgfm.markdown_to_html(text)

    markdown_str = apply_css(gfm_text)

    html = bleach.clean(
        markdown_str,
        tags=settings.MARKDOWN_FILTER_WHITELIST_TAGS,
        attributes=settings.MARKDOWN_FILTER_WHITELIST_ATTRIBUTES,
        styles=settings.MARKDOWN_FILTER_WHITELIST_STYLES,
    )
    return html
