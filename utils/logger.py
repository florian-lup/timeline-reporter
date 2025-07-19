"""Project-wide logging configuration.

Importing this module will configure root logging handlers/formatters.
"""

from __future__ import annotations

import logging
import sys

_LOG_FORMAT = "%(levelname)s | %(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=_LOG_FORMAT,
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Suppress HTTP request logs from httpx
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger("app")
