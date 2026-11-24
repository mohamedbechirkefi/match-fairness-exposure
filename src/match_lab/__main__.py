# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Entry point for ``python -m match_lab``."""

import sys

from .cli import main

sys.exit(main())
