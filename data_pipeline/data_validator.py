import logging
import pandas as pd

logger = logging.getLogger(__name__)

def validate_dataframe(df: pd.DataFrame, validation_config: dict) -> pd.DataFrame:
    """Validate the DataFrame and return valid data using a config dictionary."""
    required_columns = validation_config.get("required_columns", [])
    numeric_columns = validation_config.get("numeric_columns", [])
    
    # Check required columns
    for col in required_columns:
        if col not in df.columns:
            logger.error(f"Required column missing: {col}")
            raise ValueError(f"Required column missing: {col}")

    valid_df = df.copy()
    initial_len = len(valid_df)

    # Validate numeric columns
    for col in numeric_columns:
        if col not in valid_df.columns:
            logger.warning(f"Configured numeric column not found: {col}")
            continue
            
        invalid_indices = []
        for i, value in valid_df[col].items():
            if pd.notna(value):
                try:
                    float(value)
                except ValueError:
                    invalid_indices.append(i)
                    logger.warning(f"Invalid value in {col}: {value}")
        
        if invalid_indices:
            valid_df = valid_df.drop(index=invalid_indices)
            logger.warning(f"Removed {len(invalid_indices)} rows with invalid numeric values in {col}")

        valid_df[col] = pd.to_numeric(valid_df[col], errors='coerce')

    logger.debug(f"Validation: {initial_len}->{len(valid_df)} rows")
    return valid_df