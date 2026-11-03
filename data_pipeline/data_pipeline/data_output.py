import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

def save_data(df: pd.DataFrame, filepath) -> Path:
    """Save a DataFrame as a CSV file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info(f"Saved {len(df)} rows to {path}")
    return path