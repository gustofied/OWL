import json
import logging
import logging.config
import time
from pathlib import Path
import rerun as rr

# Config file sits next to this module
CONFIG_PATH = Path(__file__).with_name("observability_config.json")

# Named app logger; no handlers here (root handles everything)
logger = logging.getLogger("games_logger")

def setup_logging(*, app_name: str = "games_logging") -> None:
    """Configure stdlib logging from dictConfig and init Rerun with a given app name."""
    # Start the Rerun Viewer/session before emitting logs
    rr.init(app_name, spawn=True)

    # Load config
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        cfg = json.load(f)

    # Ensure JSON log dir exists if present in config
    try:
        logfile = cfg["handlers"]["json_file"]["filename"]
        Path(logfile).parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass  # fine if json_file handler isn't configured

    # Apply dictConfig
    logging.config.dictConfig(cfg)

    # Make %(asctime)s render in UTC for formatter-based handlers (console/file)
    root = logging.getLogger()
    for h in root.handlers:
        fmt = getattr(h, "formatter", None)
        if fmt is not None:
            fmt.converter = time.gmtime  # asctime ends with 'Z' per datefmt

if __name__ == "__main__":
    setup_logging(app_name="games_logging")
    logger.info("observability self-test")
