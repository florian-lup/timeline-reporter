"""Project-wide logging configuration.

Importing this module will configure root logging handlers/formatters.
"""

from __future__ import annotations

import logging
import sys

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=_LOG_FORMAT,
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Suppress HTTP request logs from httpx
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger("timeline-reporter")
