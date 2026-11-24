# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Toolchain check: the package imports and reports its version."""

import match_lab


def test_package_imports() -> None:
    assert match_lab.__version__ == "0.2.0"
