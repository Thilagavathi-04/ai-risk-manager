from pathlib import Path

import kagglehub
import pandas as pd


DATASET_SLUG = "ealaxi/paysim1"
DATASET_FILE = "PS_20174392719_1491204439457_log.csv"


def download_dataset() -> Path:
    return Path(kagglehub.dataset_download(DATASET_SLUG))


def load_raw_data(dataset_dir: Path | None = None) -> pd.DataFrame:
    root = dataset_dir or download_dataset()
    return pd.read_csv(root / DATASET_FILE)
