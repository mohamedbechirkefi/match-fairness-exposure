# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""M0 toolchain check only: the package imports. No algorithm is tested yet."""

import match_lab


def test_package_imports() -> None:
    assert match_lab.__version__ == "0.0.0"
