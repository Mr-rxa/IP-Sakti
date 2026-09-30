import logging
import re
import sys

_SENSITIVE_PATTERN = re.compile(
    r"(?i)(password|secret|token|api[_-]?key|authorization)(\s*[:=]\s*)([^,\s]+)"
)

class SensitiveValueRedactionFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = str(record.msg)
        sensitive_placeholder = re.search(r"(?i)(password|secret|token|api[_-]?key|authorization)(\s*[:=]\s*)%[a-z]", message)
        if sensitive_placeholder and record.args:
            message = message[:sensitive_placeholder.end(2)] + "[REDACTED]" + message[sensitive_placeholder.end():]
            args = list(record.args)
            if args and isinstance(args[0], str):
                args.pop(0)
            record.args = tuple(args)
        record.msg = _SENSITIVE_PATTERN.sub(r"\1\2[REDACTED]", message)
        if record.args:
            record.args = tuple(
                "[REDACTED]" if isinstance(arg, str) and _SENSITIVE_PATTERN.search(str(record.msg)) else arg
                for arg in record.args
            )
        return True

def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(SensitiveValueRedactionFilter())
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[handler]
    )
    return logging.getLogger("ip_sakti_backend")

logger = setup_logging()
