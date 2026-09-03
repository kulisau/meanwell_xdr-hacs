"""Make the vendored ``xdr_modbus`` device library importable.

The device library ships inside this integration (``vendor/xdr_modbus``) so
the integration has no PyPI dependency on it; this module puts that directory
on ``sys.path``. Import this module before importing ``xdr_modbus``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_VENDOR_DIR = Path(__file__).parent / "vendor"

if str(_VENDOR_DIR) not in sys.path:
    sys.path.insert(0, str(_VENDOR_DIR))
