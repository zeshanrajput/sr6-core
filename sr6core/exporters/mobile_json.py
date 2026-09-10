"""
Shim for backward compatibility with sr6core.exporters.mobile_json.
Re-exports from sr6core.publishing.mobile_json.
"""

from sr6core.publishing.mobile_json import (
    export_mobile_json,
    generate_mobile_json_payload,
)

__all__ = [
    "export_mobile_json",
    "generate_mobile_json_payload",
]
