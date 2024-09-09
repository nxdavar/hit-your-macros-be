-- create_table.sql
CREATE TABLE IF NOT EXISTS nutritional_info (
    id SERIAL PRIMARY KEY,
    menu_item_name TEXT,
    calories INTEGER,
    fat INTEGER,
    protein INTEGER,
    carbohydrates INTEGER,
    restaurant_name TEXT
);


