import logging
from pathlib import Path
import pandas as pd
import json
import yaml

logger = logging.getLogger(__name__)

def load_csv(filepath: Path) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""
    df = pd.read_csv(filepath)
    logger.info(f"Loaded CSV file: {filepath} ({len(df)} rows)")
    return df

def load_json(filepath: Path):
    """Load a JSON file into a Python object."""
    with open(filepath, "r") as f:
        data = json.load(f)
    logger.info(f"Loaded JSON file: {filepath}")
    return data

def load_yaml(filepath: Path):
    """Load a YAML file into a Python object."""
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
    logger.info(f"Loaded YAML file: {filepath}")
    return data

def load_data(filepath):
    """Load a file based on its extension."""
    path = Path(filepath)
    ext = path.suffix.lower()
    
    if ext == ".csv":
        return load_csv(path)
    elif ext == ".json":
        return load_json(path)
    elif ext == ".yaml" or ext == ".yml":
        return load_yaml(path)
    else:
        logger.error(f"Unsupported file format: {ext}")
        raise ValueError(f"Unsupported file format: {ext}")