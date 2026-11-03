import io
import json
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from data_pipeline import create_cleaning_report, process_data, validate_dataframe
from src import (
    DatasetInfo,
    DatasetStorage,
    HealthResponse,
    ProcessConfig,
    ProcessingReport,
    log_requests,
    setup_logging,
)

setup_logging(verbose=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Processing API", version="1.0.0")

# Register middleware
app.middleware("http")(log_requests)

storage = DatasetStorage()

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return the application status and version."""
    return {"status": "ok", "version": "1.0.0"}

@app.post("/upload", response_model=DatasetInfo)
async def upload_dataset(file: UploadFile = File(...)):
    """Read and store a CSV upload."""
    ext = Path(file.filename or "").suffix.lower()
    if ext != ".csv":
        logger.warning(f"Unsupported file format: {ext}")
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}. Only .csv files are allowed.")
    
    contents = await file.read()
    
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as e:
        logger.warning(f"Failed to parse CSV file: {e}")
        raise HTTPException(status_code=400, detail="Invalid CSV file format or contents.")

    dataset_id = storage.save(df, file.filename)
    metadata = storage.get_metadata(dataset_id)
    
    logger.info(f"Uploaded dataset: id={dataset_id}, filename={file.filename}, rows={metadata['rows']}")
    return metadata

@app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: int, limit: int = Query(default=100, ge=1)):
    """Return up to limit rows from a stored dataset."""
    df = storage.get(dataset_id)
    if df is None:
        logger.warning(f"Dataset not found: {dataset_id}")
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    sliced_df = df.head(limit)
    records = json.loads(sliced_df.to_json(orient="records"))
    
    logger.info(f"Retrieved dataset: id={dataset_id}, returned_rows={len(records)}")
    
    return {
        "id": dataset_id,
        "data": records,
        "total_rows": len(df)
    }

@app.post("/datasets/{dataset_id}/process", response_model=ProcessingReport)
def process_dataset(dataset_id: int, config: ProcessConfig):
    """Validate and process a stored dataset using MP1 functions."""
    df = storage.get(dataset_id)
    if df is None:
        logger.warning(f"Dataset not found: {dataset_id}")
        raise HTTPException(status_code=404, detail="Dataset not found")

    config_dict = config.model_dump()

    for col in config.validation.numeric_columns:
        if col not in df.columns:
            logger.warning(f"Configured numeric column not found: {col}")
            raise HTTPException(status_code=400, detail=f"Numeric column '{col}' not found in dataset.")

    try:
        initial_rows = len(df)
        validated_df = validate_dataframe(df, config_dict["validation"])
        validation_rows_removed = initial_rows - len(validated_df)
        df_to_process = validated_df.copy()

        processed_df = process_data(df_to_process, config_dict)
        cleaning_report = create_cleaning_report(validated_df, processed_df)

        storage.update(dataset_id, processed_df)

        logger.info(
            f"Processed dataset: id={dataset_id}, validation_removed={validation_rows_removed}, "
            f"rows_before={cleaning_report['rows_before']}, rows_after={cleaning_report['rows_after']}"
        )

        return {
            "id": dataset_id,
            "validation_rows_removed": validation_rows_removed,
            "cleaning_report": cleaning_report,
        }

    except ValueError as e:
        logger.warning(f"Processing error for dataset {dataset_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))