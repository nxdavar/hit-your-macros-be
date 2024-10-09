from pathlib import Path

# file path constants


BASE_DIR = Path("data")

DB_BASE_DIR = BASE_DIR / "db"

DB = BASE_DIR / "db"

IMAGE_TO_RES_CSVS = BASE_DIR / "image_to_res_csvs"

MAPPING = DB / "mapping"

DF_READING_ANOMALIES = BASE_DIR / "df_reading_anomalies"

CLEANED_TEXTRACT_RES_CSVS = BASE_DIR / "cleaned_textract_res_csvs"

CLEANED_TEXTRACT_TESTING = BASE_DIR / "cleaned_textract_res_csvs_testing"


# db mapping base paths:
db_mapping_base = "db.mapping"
