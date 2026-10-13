import os
import sys
import pytest
from pathlib import Path
from sr6core.session import format_timestamp, setup_cuda_dlls


def test_format_timestamp():
    assert format_timestamp(0) == "00:00:00"
    assert format_timestamp(45) == "00:00:45"
    assert format_timestamp(125) == "00:02:05"
    assert format_timestamp(3665) == "01:01:05"
    assert format_timestamp(23405) == "06:30:05"


def test_setup_cuda_dlls():
    # Should run without crashing and configure DLL paths on Windows
    res = setup_cuda_dlls()
    assert isinstance(res, bool)
