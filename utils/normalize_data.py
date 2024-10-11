import os
from urllib.parse import parse_qs, urlparse

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.queries.restaurant_queries import add_new_restaurant, get_restaurant_id_one
from db.table_type_mapping import menu_item_type_mapping
from db.utils.db_session import get_db, get_engine
from utils.file_names import CLEANED_TEXTRACT_TESTING, DF_READING_ANOMALIES
from utils.file_util import custom_read_csv, get_filenames_in_folder
from utils.mapping_helpers import get_function_from_module, get_restaurant_module

"""
This function normalizes seed data from a CSV file to match the database schema.

@param header_mapping: A dictionary that maps the CSV column names to the database column names.
@param file_name: The name of the CSV file to normalize.

"""


def normalize_seed_data(file_name, table_name):
    load_dotenv()

    print("this is the file name we are about to normalize: ", file_name)
    res_name = file_name.split("/")[-1].split(".")[-2]

    engine = get_engine()

    # get the mapping between the names of the restaurant csv header and the database column names
    attr_name = f"{res_name}_menu_item_mapping"

    res_mappping_module = get_restaurant_module(res_name)
    header_mapping = get_function_from_module(res_mappping_module, attr_name)
    print("this is the header mapping: ", header_mapping)

    df = custom_read_csv(
        file_name, f"""{DF_READING_ANOMALIES}/{res_name}_anomalies.csv"""
    )

    df.columns = df.columns.str.strip()

    # rename cols based on mapping

    df.rename(columns=header_mapping, inplace=True)
    df = df[list(header_mapping.values())]

    # Retrieve the foreign key value

    df["restaurant_id"] = get_foreign_key(res_name)

    # Ensure data types match the database schema

    filtered_menu_item_type_mapping = {
        key: value for key, value in menu_item_type_mapping.items() if key in df.columns
    }

    df, invalid_rows = convert_df_data(df, filtered_menu_item_type_mapping)

    print("these were the invalid rows: ", invalid_rows)

    df = df.astype(filtered_menu_item_type_mapping)

    # Parse the DATABASE_URL
    url = urlparse(os.getenv("DATABASE_URL"))
    query = parse_qs(url.query)

    # Construct a new connection string
    connection_string = f"postgresql://{url.username}:{url.password}@{url.hostname}:{url.port}/{url.path[1:]}"

    # Add SSL mode if not present
    if "sslmode" not in query:
        connection_string += "?sslmode=require"

    # Create the engine with the correct parameters
    engine = create_engine(
        connection_string, pool_pre_ping=True, pool_size=10, max_overflow=20
    )

    # Create a sessionmaker
    sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # with SessionLocal() as session:
    #     # Generate UUID for menu item if it doesn't exist
    #     if "menu_item_id" not in df.columns:
    #         df["menu_item_id"] = [str(uuid.uuid4()) for _ in range(len(df))]

    #     df.to_sql(table_name, con=session.bind, if_exists="append", index=False)
    #     session.commit()


"""
This function converts the data in a DataFrame to match the database schema."""


def convert_df_data(df: pd.DataFrame, mapping: dict):
    all_cols = [(col, col_type) for col, col_type in mapping.items()]
    print("these are all the cols: ", all_cols)

    float_columns = set([col for col, dtype in mapping.items() if dtype == "float64"])
    print("these are the float cols: ", float_columns)
    bool_columns = set([col for col, dtype in mapping.items() if dtype == "bool"])
    print("these are the bool cols: ", bool_columns)

    str_cols = [col for col, dtype in mapping.items() if dtype == "object"]
    print("these are the str cols: ", str_cols)

    invalid_rows = pd.DataFrame(columns=df.columns)

    for col in mapping.keys():
        if col in float_columns:
            invalid_mask = (
                pd.to_numeric(df[col], errors="coerce").isna() & df[col].notna()
            )
            invalid_rows = pd.concat([invalid_rows, df[invalid_mask]])

            try:
                df[col] = df[col].astype(float)
            except ValueError:
                print("error converting to float", col)
                df[col] = None  # Handle invalid numeric values as None

        elif col in bool_columns:

            bool_mapping = {
                "yes": True,
                "no": False,
                "1": True,
                "0": False,
                "true": True,
                "false": False,
            }
            for col in bool_columns:
                invalid_mask = ~df[col].isin(bool_mapping.keys()) & df[col].notna()
                invalid_rows = pd.concat([invalid_rows, df[invalid_mask]])
                df[col] = df[col].map(bool_mapping).fillna(False)

    invalid_rows = invalid_rows.drop_duplicates()

    return df, invalid_rows


"""
Gets the foreign key value for the restaurant_id column in the menu_item table.
@ param res_name: The name of the restaurant.
"""


def get_foreign_key(res_name: str):
    next(get_db())
    res_id = get_restaurant_id_one(res_name)
    if res_id:
        print("this is the restaurant id: ", res_id)
    else:
        restaurant = add_new_restaurant(res_name)
        if restaurant:
            res_id = restaurant.restaurant_id
        print("restaurant not found, created new one: ", restaurant)

    if res_id is None:
        raise ValueError(f"Restaurant {res_name} not found in the database")

    return res_id


def normalize_seed_for_folder(folder_name: str):
    data_file_names = get_filenames_in_folder(folder_name)
    for file_name in data_file_names:
        if file_name == "halal_guys.csv":
            continue
        normalize_seed_data(f"""{folder_name}/{file_name}""", "menu_item")


# TODO: create normalize seed for folder function for a file and test on one file and repeat


def main():
    folder_name = CLEANED_TEXTRACT_TESTING
    normalize_seed_for_folder(folder_name)


if __name__ == "__main__":
    main()
