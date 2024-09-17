# external imports:
import boto3
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import requests
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


# internal imports:
from utils.aws_util import (
    generate_presigned_urls,
    generate_presigned_url_for_file_with_keyword,
)

from clean_textract import clean_textract_row
from extract_header import extract_header


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
                    rows = []  # This will store all the cells in the current row
                    current_row_index = None  # To keep track of row positioning

                    # Iterate over all child blocks (cells)
                    for child_id in relationship["Ids"]:
                        for cell_block in blocks:
                            if (
                                cell_block["Id"] == child_id
                                and cell_block["BlockType"] == "CELL"
                            ):
                                # Extract row index to group cells into rows
                                row_index = cell_block["RowIndex"]
                                text = ""

                                # Check if the cell contains text or other children
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
                                text = text.strip()

                                # Ensure rows are grouped by RowIndex
                                if current_row_index is None:
                                    current_row_index = row_index

                                # If we detect a new row, append the previous row and reset
                                if row_index != current_row_index:
                                    table.append(rows)
                                    rows = []  # Reset for the new row
                                    current_row_index = row_index

                                # Append the cell's text to the current row
                                rows.append(text)

                    # After the loop, append the last row
                    if rows:
                        table.append(rows)

            tables.append(table)

    return tables


def display_table_data(tables: list, res_name: str):
    # Display the table data in a readable format
    for idx, table in enumerate(tables):
        print(f"Table {idx + 1}:")
        for row in table:
            print("this is row: ", row)
            # clean the row:
            cleaned_row = clean_textract_row(textract_row=row, curr_res_name=res_name)
            print("this is cleaned row: ", cleaned_row)
            print("\t".join(row))
        print("\n")


# function that will post process the table data from OCR


def extract_header_data():
    model = ChatOpenAI(model="gpt-4o-mini")

    system_message = SystemMessage(
        content=[
            {
                "type": "text",
                "text": " You are going to be given an image containing details about the header of a nutritional information table in base64 format. "
                + "Extract the header information and output it in a csv format.",
            },
            {
                "type": "text",
                "text": "An example of could be the following:"
                + "<user>: data:image/jpeg;base64,https://www.goprep.com/wp-content/uploads/2019/06/screen-shot-2019-06-19-at-6.09.23-pm.png"
                + "<system>: Cajun Chicken with Asapragus and Brown Rice,460,6,1.5,0,120,3530,61,7,3,0,42,1,0,960",
            },
        ],
    )

    res = model.invoke([system_message])

    return -1


if __name__ == "__main__":
    load_dotenv()
    bucket_name = "nutrition-menus"
    folder_base = "panda_express"
    folder_name = folder_base + "/"
    presigned_urls_cache = {}

    curr_header_url = generate_presigned_url_for_file_with_keyword(
        bucket_name=bucket_name, keyword="header", folder_prefix=folder_base
    )

    extract_header(curr_header_img_url=curr_header_url, curr_res_name=folder_base)

    presigned_urls_dict = generate_presigned_urls(
        presigned_urls_cache, bucket_name, folder_name
    )

    # find the header image in the presigned urls dict
    curr_header_img_url = None
    for file_key, menu_presigned_url in presigned_urls_dict.items():
        if file_key.find("header") != -1:
            curr_header_img_url = menu_presigned_url
            break

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
        display_table_data(tables, res_name=folder_base)
