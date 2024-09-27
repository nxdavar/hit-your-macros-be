# Hit Your Macros -- Backend

### Introduction

This is the backend repository for Hit Your Macros - an app intends to help you find macro-nutritionally friendly items at restaurants in your vicinity.

### Data Extraction Workflows

Below we will outline the major backend workflows that this repo. contains:

####

### Project Structure

```
Project-folder
  ├── README.md           <- The top-level README for using this project
  ├── .env                <- (You have to make your own env file -- more on this below) ->
  ├── alembic             <- This folder encapsulates migration data (once you setup your local db you will have to run db commands to sync migration data atop of the foundational database)
    |   └── versions           <- Each file within this folder represents a migration (i.e changing the db schema)
  ├── data                <- Holds yml files for project configs
      |   └── cleaned_textract_res_csvs     <- Represents csvs of menus post textract job data extractin + manual processing (i.e these files are ready to be seeded into our database)
      |   └── df_reading_anomalies          <- After each of the files in our cleaned_textract_res_csvs get processed by helper functions. If there are irregularities (one row has less/more cols. than other rows), that data is saved here
      |   └── image_to_res_csvs             <- Files in this folder were outputted by the GPT workflows during testing (we may have to create separate folders to segregate non tabular vs tabular data output folders for the GPT scripts)
  ├── explore             <- Contains my exploration notebooks and the teaching material for YouTube videos.
  ├── data                <- Contains the sample data for the project.
  ├── src                 <- Contains the source code(s) for executing the project.
  |   └── utils           <- Contains all the necessary project modules.
  └── images              <- Contains all the images used in the user interface and the README file.
```

### Installation
