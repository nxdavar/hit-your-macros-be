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


CREATE TABLE Menu_Item (
    item_id SERIAL PRIMARY KEY,
    restaurant_id INT REFERENCES Restaurant(restaurant_id),
    name VARCHAR(255) NOT NULL,
    grams_protein DECIMAL(5,2),
    grams_carbs DECIMAL(5,2),
    grams_fat DECIMAL(5,2),
    ingredients TEXT,
    allergens TEXT
);


CREATE TABLE Item_Attributes (
    item_id INT PRIMARY KEY REFERENCES Menu_Item(item_id),
    is_breakfast BOOLEAN,
    is_dessert BOOLEAN,
    is_side_condiment BOOLEAN,
    is_add_on BOOLEAN,
    is_vegetarian BOOLEAN,
    contains_caffeine BOOLEAN,
    contains_alcohol BOOLEAN,
    contains_seafood BOOLEAN,
    is_kids_meal BOOLEAN,
    is_beverage BOOLEAN,
    is_dairy_free BOOLEAN,
    is_pescatarian BOOLEAN,
    is_vegan BOOLEAN,
    is_gluten_free BOOLEAN,
    is_keto BOOLEAN
);
