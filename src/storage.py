import logging
import pandas as pd

logger = logging.getLogger(__name__)

class DatasetStorage:
    def __init__(self):
        self._store = {}
        self._counter = 0

    def save(self, df: pd.DataFrame, filename: str) -> int:
        self._counter += 1
        dataset_id = self._counter
        self._store[dataset_id] = {
            "filename": filename,
            "df": df.copy()
        }
        logger.debug(f"Stored dataset: id={dataset_id}, rows={len(df)}")
        return dataset_id

    def get(self, dataset_id: int):
        if dataset_id not in self._store:
            return None
        logger.debug(f"Retrieved dataset copy: id={dataset_id}, rows={len(self._store[dataset_id]['df'])}")
        return self._store[dataset_id]["df"].copy()

    def get_metadata(self, dataset_id: int):
        if dataset_id not in self._store:
            return None
        item = self._store[dataset_id]
        df = item["df"]
        return {
            "id": dataset_id,
            "filename": item["filename"],
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns)
        }

    def update(self, dataset_id: int, df: pd.DataFrame) -> bool:
        if dataset_id not in self._store:
            return False
        self._store[dataset_id]["df"] = df.copy()
        logger.debug(f"Updated dataset: id={dataset_id}")
        return True

    def clear(self):
        self._store.clear()
        self._counter = 0