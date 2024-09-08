# external imports:
import boto3
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import requests


# internal imports:
from utils.aws_util import generate_presigned_urls


# Initialize the Amazon Textract client
textract_client = boto3.client("textract", region_name="us-east-1")


def analyze_image(presigned_url):
    # Download the image from the presigned S3 URL
    response = requests.get(presigned_url)

    if response.status_code == 200:
        image_bytes = response.content
    else:
        raise Exception(
            f"Failed to download image from S3. Status code: {response.status_code}"
        )

    # Call Amazon Textract to analyze the document
    textract_response = textract_client.analyze_document(
        Document={"Bytes": image_bytes}, FeatureTypes=["TABLES"]
    )

    return textract_response


def extract_table_data(textract_response):
    # Extract table information from Textract response
    blocks = textract_response["Blocks"]
    tables = []

    # Parse table blocks
    for block in blocks:
        if block["BlockType"] == "TABLE":
            table = []
            for relationship in block["Relationships"]:
                if relationship["Type"] == "CHILD":
                    rows = []
                    for child_id in relationship["Ids"]:
                        for cell_block in blocks:
                            if (
                                cell_block["Id"] == child_id
                                and cell_block["BlockType"] == "CELL"
                            ):
                                text = ""
                                if "Relationships" in cell_block:
                                    for inner_child in cell_block["Relationships"]:
                                        if inner_child["Type"] == "CHILD":
                                            for inner_child_id in inner_child["Ids"]:
                                                for word_block in blocks:
                                                    if (
                                                        word_block["Id"]
                                                        == inner_child_id
                                                        and word_block["BlockType"]
                                                        == "WORD"
                                                    ):
                                                        text += word_block["Text"] + " "
                                rows.append(text.strip())
                    table.append(rows)
            tables.append(table)

    return tables


def display_table_data(tables):
    # Display the table data in a readable format
    for idx, table in enumerate(tables):
        print(f"Table {idx + 1}:")
        for row in table:
            print("\t".join(row))
        print("\n")


# function that will post process the table data from OCR


def post_processing(table_row: str):
    return -1


if __name__ == "__main__":
    load_dotenv()
    bucket_name = "nutrition-menus"
    folder_base = "tatte"
    folder_name = folder_base + "/"
    presigned_urls_cache = {}

    presigned_urls_dict = generate_presigned_urls(
        presigned_urls_cache, bucket_name, folder_name
    )

    for file_key, menu_presigned_url in presigned_urls_dict.items():
        print(
            "this is the url we will be analyzing with textract: ", menu_presigned_url
        )

        if file_key == folder_name or file_key.find("header") != -1:
            continue
        response = analyze_image(menu_presigned_url)

        # Extract table data
        tables = extract_table_data(response)

        # Display the extracted table data
        display_table_data(tables)
