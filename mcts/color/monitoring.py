# telemetry.py  – import this at process start
import logging, logging.config, sys, pathlib
import rerun as rr
import wandb

LOG_DIR = pathlib.Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def init(app_id: str = "color_game"):
    # --- 1. initialise Rerun and WandB ---------------------------------
    rr.init(app_id, spawn=True)
    wandb.init(project="color-game", name=app_id, save_code=True)

    # --- 2. build logging handlers ------------------------------------
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )
    )

    rotate = logging.handlers.RotatingFileHandler(
        LOG_DIR / f"{app_id}.log", maxBytes=2_000_000, backupCount=5
    )
    rotate.setLevel(logging.DEBUG)
    rotate.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s:%(lineno)d %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
    )

    # Rerun has a ready-made logging handler
    rr_handler = rr.LoggingHandler("logs")
    rr_handler.setLevel(logging.INFO)

    # WandB handler – custom; logs DEBUG/INFO as text, everything ≥WARNING as alert
    class WandBHandler(logging.Handler):
        def emit(self, record):
            wandb.log(
                {
                    "log/level": record.levelname,
                    "log/message": record.getMessage(),
                    "log/module": record.name,
                    "log/step": wandb.run.step,
                },
                commit=False,
            )
    wb_handler = WandBHandler(level=logging.INFO)

    # --- 3. configure root logger -------------------------------------
    logging.basicConfig(level=logging.DEBUG, handlers=[console, rotate, rr_handler, wb_handler])
