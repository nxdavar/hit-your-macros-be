# external imports:
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


# internal imports:
from utils.file_names import MAPPING, CLEANED_TEXTRACT_RES_CSVS
from utils.file_util import get_filenames_in_folder
from db.schema import Restaurant
from db.table_type_mapping import menu_item_type_mapping
from utils.mapping_helpers import get_restaurant_module, get_function_from_module


"""
This function normalizes seed data from a CSV file to match the database schema.

@param header_mapping: A dictionary that maps the CSV column names to the database column names.
@param file_name: The name of the CSV file to normalize.

"""


def normalize_seed_data(file_name, table_name):
    load_dotenv()

    df = pd.read_csv(file_name)

    res_name = file_name.split("/")[-1].split(".")[-2]

    attr_name = f"{res_name}_menu_item_mapping"

    res_mappping_module = get_restaurant_module(res_name)
    header_mapping = get_function_from_module(res_mappping_module, attr_name)

    df.columns = df.columns.str.strip()

    df.rename(columns=header_mapping, inplace=True)
    df = df[list(header_mapping.values())]

    # Step 6: Retrieve the foreign key value
    engine = create_engine(os.getenv("DATABASE_URL"))
    foreign_key_query = "SELECT restaurant_id FROM restaurant WHERE name = :res_name"

    print("this is the foreign key: ", foreign_key_query)

    with engine.connect() as connection:
        result = connection.execute(
            foreign_key_query, {"res_name": res_name}
        ).fetchone()

        if result:
            foreign_key_value = result[0]
        else:
            raise ValueError("Foreign key value not found.")

    df["restaurant_id"] = foreign_key_value

    # Step 8: Ensure data types match the database schema

    df = df.astype(menu_item_type_mapping)

    with engine.begin() as connection:
        df.to_sql(f"""{table_name}""", con=connection, if_exists="append", index=False)


def normalize_seed_for_folder():
    data_file_names = get_filenames_in_folder(CLEANED_TEXTRACT_RES_CSVS)
    for file_name in data_file_names:
        normalize_seed_data(
            f"""{CLEANED_TEXTRACT_RES_CSVS }/{file_name}""", "menu_item"
        )


def main():
    normalize_seed_for_folder()


if __name__ == "__main__":
    main()
