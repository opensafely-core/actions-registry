import bleach
from django import template
from django.conf import settings


def apply_css(html_str: str) -> str:
    html_str = html_str.replace(
        "<h3>", '<h3 class="text-sm font-semibold text-gray-600 pt-2"> '
    )
    html_str = html_str.replace("<p>", '<p class="mt-1 text-sm text-gray-900 pt-2"> ')
    html_str = html_str.replace("<h5>", '<h5 class="text-sm font-semibold pt-2"> ')
    html_str = html_str.replace("<ul>", '<div class="list-disc">')
    html_str = html_str.replace(
        '<svg class="octicon octicon-link" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5 2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25 1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95 0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z"></path></svg>',
        "",
    )
    return html_str


register = template.Library()


@register.filter
def markdown_filter(text):
    html_str = apply_css(text)

    html = bleach.clean(
        html_str,
        tags=settings.MARKDOWN_FILTER_WHITELIST_TAGS,
        attributes=settings.MARKDOWN_FILTER_WHITELIST_ATTRIBUTES,
        styles=settings.MARKDOWN_FILTER_WHITELIST_STYLES,
    )
    return html
