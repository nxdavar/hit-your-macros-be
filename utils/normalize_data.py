# external imports:
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


# internal imports:
from utils.file_names import MAPPING, CLEANED_TEXTRACT_RES_CSVS
from utils.file_util import get_filenames_in_folder
from db.models.restaurant import Restaurant
from db.table_type_mapping import menu_item_type_mapping
from utils.mapping_helpers import get_restaurant_module, get_function_from_module
from db.utils.db_session import get_db, get_engine
from db.models.restaurant import Restaurant
from db.queries.restaurant_queries import get_restaurant_id_one, add_new_restaurant


"""
This function normalizes seed data from a CSV file to match the database schema.

@param header_mapping: A dictionary that maps the CSV column names to the database column names.
@param file_name: The name of the CSV file to normalize.

"""


def normalize_seed_data(file_name, table_name):
    load_dotenv()

    df = pd.read_csv(file_name)

    engine = get_engine()

    res_name = file_name.split("/")[-1].split(".")[-2]

    attr_name = f"{res_name}_menu_item_mapping"

    res_mappping_module = get_restaurant_module(res_name)
    header_mapping = get_function_from_module(res_mappping_module, attr_name)

    df.columns = df.columns.str.strip()

    df.rename(columns=header_mapping, inplace=True)
    df = df[list(header_mapping.values())]

    # Step 6: Retrieve the foreign key value

    df["restaurant_id"] = get_foreign_key(res_name)

    # Step 8: Ensure data types match the database schema

    filtered_menu_item_type_mapping = {
        key: value for key, value in menu_item_type_mapping.items() if key in df.columns
    }

    df, invalid_rows = convert_df_data(df, filtered_menu_item_type_mapping)

    print("these were the invalid rows: ", invalid_rows)

    df = df.astype(filtered_menu_item_type_mapping)

    print("this is the dataframe info: ")
    print(df.head())

    # with next(get_db()) as session:
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
    session = next(get_db())
    res_id = get_restaurant_id_one(session, res_name)
    if res_id:
        print("this is the restaurant id: ", res_id)
    else:
        restaurant = add_new_restaurant(session, res_name)
        if restaurant:
            res_id = restaurant.restaurant_id
        print("restaurant not found, created new one: ", restaurant)

    if res_id is None:
        raise ValueError(f"Restaurant {res_name} not found in the database")

    return res_id


def normalize_seed_for_folder():
    data_file_names = get_filenames_in_folder(CLEANED_TEXTRACT_RES_CSVS)
    for file_name in data_file_names:
        if file_name == "halal_guys.csv":
            continue
        normalize_seed_data(
            f"""{CLEANED_TEXTRACT_RES_CSVS }/{file_name}""", "menu_item"
        )


def main():
    normalize_seed_for_folder()


if __name__ == "__main__":
    main()
