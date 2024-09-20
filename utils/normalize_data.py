# this function will normalize CSV data to data that can be seeded in a PostgreSQL DB


# external imports:
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


def normalize_data(header_mapping, file_name):
    load_dotenv()

    df = pd.read_csv("data.csv")

    res_name = file_name.split(".")[0]

    df.rename(columns=header_mapping, inplace=True)
    df = df[list(header_mapping.values())]

    # Step 6: Retrieve the foreign key value
    engine = create_engine(os.getenv("DATABASE_URL"))
    foreign_key_query = "SELECT restaurant_id FROM restaurant WHERE name = :res_name"

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
    df = df.astype(
        {
            "DB_Column1": "int",
            "DB_Column2": "float",
            "foreign_key_column": "int",
            # Add other columns as necessary
        }
    )

    # Step 9: Insert data into the database
    with engine.begin() as connection:
        df.to_sql("your_table_name", con=connection, if_exists="append", index=False)
