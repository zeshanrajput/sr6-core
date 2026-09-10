"""
Shim for backward compatibility with sr6core.exporters.mobile_html.
Re-exports from sr6core.publishing.mobile_html.
"""

from sr6core.publishing.mobile_html import (
    export_mobile_html,
    get_mobile_html_template,
)

__all__ = [
    "export_mobile_html",
    "get_mobile_html_template",
]
