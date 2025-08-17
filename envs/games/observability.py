import json
import logging
import logging.config
import time
from pathlib import Path
import rerun as rr

CONFIG_PATH = Path(__file__).with_name("observability_config.json")

logger = logging.getLogger("owl_logger")

def setup_logging(*, app_name: str = "owl") -> None:
    """Configure stdlib logging from dictConfig and init Rerun with a given app name."""
    # Gotta start the rerun first, when we do wandb we do that even before rerun
    rr.init(app_name, spawn=True)

    # Get our config
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        cfg = json.load(f)

    # Ensure JSON log dir exists if present in config
    try:
        logfile = cfg["handlers"]["json_file"]["filename"]
        Path(logfile).parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass  

    # we configure our logging by passing in a json-config file and make use of dicConfig to do so
    # our idea behind logging is that root handles it all, every child logger propagates to it
    logging.config.dictConfig(cfg)

    # Some time formatting thingy
    root = logging.getLogger()
    for h in root.handlers:
        fmt = getattr(h, "formatter", None)
        if fmt is not None:
            fmt.converter = time.gmtime  

if __name__ == "__main__":
    setup_logging(app_name="owl_logging_test")
    logger.info("observability self-test")
