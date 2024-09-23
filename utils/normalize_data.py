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

    df["restaurant_id"] = res_id

    # Step 8: Ensure data types match the database schema

    filtered_menu_item_type_mapping = {
        key: value for key, value in menu_item_type_mapping.items() if key in df.columns
    }

    df = df.astype(filtered_menu_item_type_mapping)

    with next(get_db()) as session:
        df.to_sql(table_name, con=session.bind, if_exists="append", index=False)
        session.commit()


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
