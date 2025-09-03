
import logging

def get_logger(name: str = "pdf2xml"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    fmt = "[%(levelname)s] %(message)s"
    try:
        from rich.logging import RichHandler  # optional
        handler = RichHandler(rich_tracebacks=False, markup=True)
        fmt = "%(message)s"
    except Exception:
        pass
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)
    return logger
