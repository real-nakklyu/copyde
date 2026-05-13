from __future__ import annotations

import logging

from app.core.security import redact_sensitive


class SensitiveDataFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.args, dict):
            record.args = redact_sensitive(record.args)
        if isinstance(record.msg, dict):
            record.msg = redact_sensitive(record.msg)
        return True


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    logging.getLogger().addFilter(SensitiveDataFilter())

