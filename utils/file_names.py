from pathlib import Path

# file path constants


BASE_DIR = Path("data")

DB = BASE_DIR / "db"

IMAGE_TO_RES_CSVS = BASE_DIR / "image_to_res_csvs"

MAPPING = DB / "mapping"

DF_READING_ANOMALIES = BASE_DIR / "df_reading_anomalies"

CLEANED_TEXTRACT_RES_CSVS = BASE_DIR / "cleaned_textract_res_csvs"
