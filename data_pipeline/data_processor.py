import logging
import pandas as pd

logger = logging.getLogger(__name__)

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate rows."""
    initial_len = len(df)
    result_df = df.drop_duplicates()
    removed = initial_len - len(result_df)
    logger.debug(f"remove_duplicates: {initial_len}->{len(result_df)} rows")
    return result_df

def handle_missing(df: pd.DataFrame, axis: str = "rows") -> pd.DataFrame:
    """Drop rows or columns containing missing values."""
    initial_len = len(df)
    initial_cols = len(df.columns)
    
    if axis == "rows":
        result_df = df.dropna(axis=0)
        logger.debug(f"handle_missing: {initial_len}->{len(result_df)} rows")
    elif axis == "columns":
        result_df = df.dropna(axis=1)
        logger.debug(f"handle_missing: {initial_cols}->{len(result_df.columns)} columns")
    else:
        logger.error(f"Unsupported axis for missing values: {axis}")
        raise ValueError(f"Unsupported axis: {axis}")
        
    return result_df

def remove_outliers(df: pd.DataFrame, columns: list, method: str, threshold: float) -> pd.DataFrame:
    """Remove outliers from specified numeric columns."""
    result_df = df.copy()
    
    if method not in ["iqr", "zscore"]:
        logger.error(f"Unsupported outlier method: {method}")
        raise ValueError(f"Unsupported outlier method: {method}")

    for col in columns:
        if col not in result_df.columns:
            logger.warning(f"Column not found: {col}")
            continue
        if not pd.api.types.is_numeric_dtype(result_df[col]):
            logger.warning(f"Column is not numeric: {col}")
            continue
            
        initial_len = len(result_df)
        if method == "iqr":
            Q1 = result_df[col].quantile(0.25)
            Q3 = result_df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            
            logger.debug(f"{col}: lower={lower_bound}, upper={upper_bound}")
            result_df = result_df[(result_df[col] >= lower_bound) & (result_df[col] <= upper_bound)]
        elif method == "zscore":
            mean = result_df[col].mean()
            std = result_df[col].std()
            if std == 0 or pd.isna(std):
                continue
            z_scores = (result_df[col] - mean) / std
            result_df = result_df[abs(z_scores) <= threshold]
            
        removed = initial_len - len(result_df)
        logger.debug(f"{col}: method={method}, threshold={threshold}, removed={removed}")

    return result_df

def process_data(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Apply processing steps enabled in configuration."""
    proc_config = config.get("processing", {})
    result_df = df.copy()
    
    if proc_config.get("remove_duplicates", False):
        result_df = remove_duplicates(result_df)
        
    missing_config = proc_config.get("missing", {})
    if missing_config.get("enabled", False):
        axis = missing_config.get("axis", "rows")
        result_df = handle_missing(result_df, axis=axis)
        
    outlier_config = proc_config.get("outliers", {})
    if outlier_config.get("enabled", False):
        columns = outlier_config.get("columns", [])
        method = outlier_config.get("method", "iqr")
        threshold = outlier_config.get("threshold", 1.5)
        result_df = remove_outliers(result_df, columns, method, threshold)
        
    return result_df

def create_cleaning_report(df_before: pd.DataFrame, df_after: pd.DataFrame) -> dict:
    """Return a dictionary summarizing cleaning results."""
    return {
        "rows_before": len(df_before),
        "rows_after": len(df_after),
        "rows_removed": len(df_before) - len(df_after),
        "columns_before": len(df_before.columns),
        "columns_after": len(df_after.columns),
        "columns_removed": len(df_before.columns) - len(df_after.columns),
    }