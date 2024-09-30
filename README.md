# Hit Your Macros -- Backend

### Introduction

This is the backend repository for Hit Your Macros - an app intends to help you find macro-nutritionally friendly items at restaurants in your vicinity.

### Data Extraction Workflows

Below we will outline the major backend workflows that this repo. contains:

#### Workflow As An Image:

![Image description](assets/images/HitYourMacros_DataBottlenecks.png)

### Project Structure

```
Project-folder
  ├── README.md           <- The top-level README for using this project
  ├── .env                <- (You have to make your own env file -- more on this below) ->
  ├── alembic             <- This folder encapsulates migration data
    |   └── versions           <- Each file within this folder represents a migration (i.e changing the db schema)
  ├── data                <- Restaurant Data (mostly post processed data from workflows)
      |   └── cleaned_textract_res_csvs     <- Post Textract script processed files
      |   └── df_reading_anomalies          <- Post Pandas DF Helper function processed files
      |   └── image_to_res_csvs             <- Post GPT script processed fields
  ├── scripts
  |   └── testing           <- Archived, mostly unused testing scripts
  ├── db                  <- Restaurant Data (mostly post processed data from workflows)
      |   └── mapping       <- Mapping between CSV headers which are a subset of DB Table headers
      |   └── models        <- DB SQLAlchemy ORM models
      |   └── queries       <- SQLAlchemy based query functions
      |   └── utils         <- DB Utils (i.e session creation)
      |   └── table_type_mapping.py     <- dictionary mapping types for all tables in db
  ├── clean_textract.py   <- Textract script used to process menu item images in S3
  ├── extract_header.py   <- GPT based script used to extract header as CSV
  ├── gpt_vision_non_tabular_script.py    <- GPT based script for menu items with non-tabular data
  ├── gpt_vision_tabular_script.py    <- GPT based script for menu items with tabular data
  ├── clean_textract.py   <- Processes and cleans individual textract rows
```

### Installation
