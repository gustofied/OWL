Below is a “drop-in” starter kit you can copy into a brand-new repo.
It wires **Python logging ⇢ Rerun ⇢ console/file** and **W\&B** in a single place, so you never have to sprinkle `wandb.log()` or `rr.log()` calls throughout your code again.

---

## 1 Install the tools

```bash
pip install rerun-sdk wandb pyyaml
```

- `rerun-sdk` gives you the visual logger and a built-in `LoggingHandler` for Python logs ([ref.rerun.io][1])
- `wandb` is the cloud tracker ([Weights & Biases Documentation][2])

---

## 2 Create **handlers.py**

```python
# handlers.py
import logging, wandb, rerun as rr
from typing import Any, Dict

class WandBHandler(logging.Handler):
    """Send LogRecord.extra['metrics'] to W&B."""
    def __init__(self, project: str = "demo", entity: str | None = None):
        super().__init__()
        self.run = wandb.init(project=project, entity=entity, config={}, reinit=True)

    def emit(self, record: logging.LogRecord) -> None:
        if hasattr(record, "metrics"):
            self.run.log(record.metrics, step=getattr(record, "step", None))

    def close(self) -> None:
        self.run.finish()
        super().close()
```

_Rerun_ ships its own handler, so you don’t have to write one:

```python
import rerun as rr
rr.LoggingHandler  # ready to use :contentReference[oaicite:2]{index=2}
```

---

## 3 Write **logging_cfg.yaml**

```yaml
version: 1
disable_existing_loggers: False

formatters:
  simple:
    format: "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: simple
  file:
    class: logging.handlers.RotatingFileHandler
    filename: "run.log"
    maxBytes: 5_000_000
    backupCount: 3
    level: DEBUG
    formatter: simple
  rerun:
    class: rerun.LoggingHandler # built-in
    level: DEBUG
    path_prefix: "logs" # appears under `logs/…` in the viewer
  wandb:
    (): handlers.WandBHandler # dotted-path to our subclass
    level: INFO
    project: "my-awesome-project" # constructor kwargs are legal :contentReference[oaicite:3]{index=3}

loggers:
  trainer:
    handlers: [console, file, rerun, wandb]
    level: INFO
    propagate: False
```

Why YAML? It’s easy to edit in prod; Python’s `dictConfig` parses YAML or JSON the same way ([Python documentation][3]).

---

## 4 Bootstrapping code (**log_setup.py**)

```python
import logging, logging.config, yaml, rerun as rr

def setup_logging(cfg_path: str = "logging_cfg.yaml",
                  rerun_app_id: str = "demo",
                  spawn_viewer: bool = True) -> None:
    # 1️⃣  Start Rerun first so its handler has somewhere to send events
    rr.init(rerun_app_id, spawn=spawn_viewer)   # opens a viewer window

    # 2️⃣  Load the YAML and hand it to dictConfig
    with open(cfg_path) as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)
```

---

## 5 Use it in **train.py**

```python
import logging, random, time
import rerun as rr, numpy as np
import wandb                     # only for Image helper

from log_setup import setup_logging
setup_logging()

log = logging.getLogger("trainer")

for step in range(10):
    loss = random.random()
    # scalar to all handlers
    log.info("step=%d loss=%.4f", step, loss,
             extra={"metrics": {"loss": loss}, "step": step})

    # batch-visual: send every image to Rerun only
    img = (np.random.rand(64, 64, 3) * 255).astype("uint8")
    rr.log(f"images/batch/{step}", rr.Image(img))

    # summary-visual: send one image per epoch to W&B
    if step % 5 == 0:
        log.info("", extra={
            "metrics": {"sample": wandb.Image(img)},   # goes to WandBHandler
            "step": step
        })
    time.sleep(0.2)
```

### How it behaves

| Destination | What you see in real time                          |
| ----------- | -------------------------------------------------- |
| **Console** | `INFO step=1 loss=0.432`                           |
| **Rerun**   | Live timeline: images/\*\*batch/\*\*_n_ + log text |
| **run.log** | Everything including `DEBUG`                       |
| **W\&B**    | Scalar plot of `loss`, table of `sample` images    |

All of it is indexed by the same **run ID** (W\&B gives you one; reuse it as `rerun_app_id` if you like).

---

## 6 Extending to frameworks

| Framework             | How to plug in                                                                                                                                                                                          |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **PyTorch Lightning** | Pass `wandb_logger = WandbLogger()` to `Trainer` and still call `setup_logging()` so Rerun & console/file stay active. Lightning only logs from rank 0 in DDP, so duplicates are avoided automatically. |
| **HF Trainer**        | Set `report_to="wandb"` in `TrainingArguments`; add a `TrainerCallback` that calls `rr.log()` for visuals or just rely on the global `logging` → Rerun handler.                                         |
| **Future handlers**   | Drop another section in `logging_cfg.yaml` (e.g. `tensorboard`, `sentry`) and add it to the `trainer` handler list; no code changes.                                                                    |

---

## 7 Operational tips

- **Frequency control** – Dump _lots_ of frames to Rerun (it’s local) but only periodic snapshots to W\&B to keep bandwidth reasonable.
- **Unique run names** – Use the same `run_id`/`app_id` for W\&B and Rerun; add tags like `"baseline"` or `"grid-search"` for grouping runs in the W\&B UI.
- **Fail-safe finish** – Wrap your main in `try/except` and always call `logging.exception` so errors land in both dashboards. W\&B marks the run as _failed_ automatically if an exception escapes ([Weights & Biases Documentation][4]).
- **Artifacts** – After training, upload the checkpoint with `wandb.Artifact`; the same ID lets you fetch the exact model later ([Weights & Biases Documentation][5]).
- **Record the Rerun session** – `rr.save("session.rrd")` at the end if you want a portable visual log file ([ref.rerun.io][6]).

---

### That’s it!

You now have a **single `logging` call** that can fan-out to as many back-ends as you need, keeps your console readable, gives you rich real-time visuals, and preserves a full experiment record in the cloud. Paste the three files above into a repo and start logging.

[1]: https://ref.rerun.io/docs/python/0.12.0/common/archetypes/?utm_source=chatgpt.com "Archetypes - Rerun Python APIs"
[2]: https://docs.wandb.ai/quickstart/?utm_source=chatgpt.com "W&B Quickstart - Weights & Biases Documentation - Wandb"
[3]: https://docs.python.org/3/howto/logging-cookbook.html?utm_source=chatgpt.com "Logging Cookbook — Python 3.13.5 documentation"
[4]: https://docs.wandb.ai/ref/python/sdk/classes/run/?utm_source=chatgpt.com "Run | Weights & Biases Documentation - Wandb"
[5]: https://docs.wandb.ai/guides/track/log/?utm_source=chatgpt.com "Log objects and media | Weights & Biases Documentation"
[6]: https://ref.rerun.io/docs/python/0.23.3/common/other_classes_and_functions/?utm_source=chatgpt.com "Other classes and functions"
