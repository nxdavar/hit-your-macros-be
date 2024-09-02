from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import PyPDF2
from openai import OpenAI
import camelot
import csv
import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import base64
import httpx
from dotenv import load_dotenv
import time


# saves files to csv
def save_to_csv(response, file_path):
    # Check if the file exists
    file_exists = os.path.isfile(file_path)

    # Open the file in append mode if it exists, otherwise in write mode
    with open(file_path, mode="a" if file_exists else "w", newline="") as file:
        writer = csv.writer(file)

        # If the file doesn't exist, write the header
        if not file_exists:
            writer.writerow(["Response"])

        # Write the response to the CSV file
        writer.writerow([response])


# Store presigned URLs and their expiration times


def generate_presigned_urls(
    presigned_urls_cache: dict, bucket_name: str, folder_prefix: str, expiration=3600
):
    """
    Generates presigned URLs for all files within a specific folder in an S3 bucket.
    Checks if the presigned URLs have expired before generating new ones.

    :param bucket_name: Name of the S3 bucket.
    :param folder_prefix: The prefix (folder path) within the bucket.
    :param expiration: Time in seconds for the presigned URL to remain valid (default: 3600 seconds).
    :return: A dictionary mapping file names to their presigned URLs.
    """
    s3_client = boto3.client("s3")

    try:
        # List objects within the specified folder
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)

        if "Contents" not in response:
            print("No files found in the specified folder.")
            return {}

        # Generate presigned URLs for each object
        current_time = int(time.time())
        for obj in response["Contents"]:
            file_key = obj["Key"]
            print("file key: ", file_key)

            # Check if a valid presigned URL already exists in the cache
            if file_key in presigned_urls_cache:
                cached_url, expiry_time = presigned_urls_cache[file_key]
                if current_time < expiry_time:
                    # Presigned URL is still valid, skip generation
                    print(f"Using cached URL for {file_key}")
                    continue

            # Generate a new presigned URL
            presigned_url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": file_key},
                ExpiresIn=expiration,
            )
            # Store the presigned URL and its expiration time in the cache
            expiry_time = current_time + expiration
            presigned_urls_cache[file_key] = (presigned_url, expiry_time)
            print(f"Generated new URL for {file_key}")

        return {file_key: url for file_key, (url, _) in presigned_urls_cache.items()}

    except boto3.exceptions.S3UploadFailedError as e:
        print(f"Error: {e}")
        return {}


def main():
    load_dotenv()

    prompt_template_str = """
        You are going to be given urls to two images. One image will be part of a nutritional information table for a restaurant. The second image will be the header of the nutritional information table. You will need to extract the nutritional information from the table and output the data as a csv file. This is the first image {nutritional_information}. This is the second image {header}."""

    s3 = boto3.client("s3")
    bucket_name = "nutrition-menus"
    folder_base = "popeyes"
    folder_name = folder_base + "/"

    presigned_urls_cache = {}
    presigned_urls_dict = generate_presigned_urls(
        presigned_urls_cache, bucket_name, folder_name
    )

    print("presigned urls dict: ", presigned_urls_dict)
    print("presigned urls dict keys: ", presigned_urls_dict.keys())

    header_presigned_url = presigned_urls_dict[
        f"""{folder_base}/{folder_base}_header.png"""
    ]
    header_image_data = base64.b64encode(
        httpx.get(header_presigned_url).content
    ).decode("utf-8")

    for file_key, menu_presigned_url in presigned_urls_dict.items():

        if file_key == folder_name or file_key.find("header") != -1:
            continue

        model = ChatOpenAI(model="gpt-4o-mini")
        menu_image_data = base64.b64encode(
            httpx.get(menu_presigned_url).content
        ).decode("utf-8")

        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": " You are going to be given urls to two images. One image will be part of a nutritional information table for a restaurant. The second image will be the header of the nutritional information table. You will need to extract the nutritional information from the table and output the data as a csv file.",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{menu_image_data}"},
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{header_image_data}"},
                },
            ],
        )

        res = model.invoke([message])
        print(res.content)
        print(type(res.content))
        res_tmp = res.content
        res_tmp_start_idx = res_tmp.find("```csv")
        res_tmp_end_idx = res_tmp.find("```", res_tmp_start_idx + 6)
        print("res start idx: ", res_tmp_start_idx)
        print("res end idx: ", res_tmp_end_idx)
        filtered_res = res_tmp[res_tmp_start_idx + 6 : res_tmp_end_idx]
        print("this is filtered res: ", filtered_res)

        save_to_csv(filtered_res, f"""res_csvs/{folder_base}.csv""")


if __name__ == "__main__":
    main()
