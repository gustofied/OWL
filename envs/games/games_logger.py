import json
import logging
import logging.config
import time
from pathlib import Path
import rerun as rr

CONFIG_PATH = Path(__file__).with_name("logger_config.json")

# named app logger; no handlers here (root handles everything)
logger = logging.getLogger("games_logger")

def setup_logging() -> None:
    # Start the Rerun Viewer/session once before emitting logs
    rr.init("rerun_logging", spawn=True)

    # Apply dictConfig
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        cfg = json.load(f)
    logging.config.dictConfig(cfg)

    # Make %(asctime)s render in UTC for console formatter
    root = logging.getLogger()
    for h in root.handlers:
        fmt = getattr(h, "formatter", None)
        if fmt is not None:
            fmt.converter = time.gmtime  # UTC timestamps

if __name__ == "__main__":
    setup_logging()
    logger.debug("This DEBUG is filtered by root level INFO")
    logger.info("Hello from games_logger (INFO)")
    logger.warning("Something to see (WARNING)")
    logger.error("Oops (ERROR)")
    logger.critical("Critical path (CRITICAL)")
