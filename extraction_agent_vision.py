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


def generate_presigned_urls(bucket_name, folder_prefix, expiration=3600):
    """
    Generates presigned URLs for all files within a specific folder in an S3 bucket.

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
        presigned_urls = {}
        for obj in response["Contents"]:
            file_key = obj["Key"]
            print('this is the file key: ', file_key)
            presigned_url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": file_key},
                ExpiresIn=expiration,
            )
            presigned_urls[file_key] = presigned_url
            print(f"Generated URL for {file_key}")

        return presigned_urls

    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Error: {e}")
        return {}


def main():
    load_dotenv()

    menu_image_url = "https://nutrition-menus.s3.us-east-1.amazonaws.com/torchys/torchys_breakfast_tacos.png?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEIL%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIFAAY52t3Yn7xbGxs5Hb0gi3%2BvLpCZXBST3GGwgMZwD9AiEA%2FS%2FFKlFaKkgL2V%2BZH9ousGFSjraEhhCpWpG3QN73C3wqtQIImv%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2NDg3MzU3MTQ0ODUiDJ%2FtiayLG2AM1gFk0iqJAoRlCJ1MGkLE9xltefI3UOOlrboAW7d90GCOJPgtH2xXxSMSpDntLXzBNgX5wP0%2BrBzT5TJyhA%2BLna3okodarKChvn8637q2DJgJhvATrjZcr42S8pdeOxBuPYFTG44bJd0huu1JYFG8upQD%2Bx0iDGW5jLYzma5wKtOqLKbBAUODglbeEExX8RwZZzq3J1LNj9grADCtMDZVQgWZUhp0cfT5vC7STGVvoeKsMHAClWxOft4DLDqkkQHj5eDdPgMjwh8C4mzxjJGiaGiiJJni21gUNL1CKTlfDmgr2n3q814HkuSa%2BTDUhjkPN48FSsqbED2e%2FP%2B1HVerFi8JbMldT3RHGthyQpoGn3EwvJDUtgY63wHSyH0diBbFegyzIV0jja7wzOdsaZYeaCOBSb2NGEg0iSz7Ef88ZCqAr3Eax2DuCFJMDLM8rQyu6EOY8SuHZC5EDJ9T3nmnArQMPX5IFxg7vzesMA46g9tnOQq4L36A6rfyWb7ixZpE4okOxCsW2jgNYsxtrlN4Afdgk5hq5gu18QjWi0%2FLSoWCl%2BrBdDdLVcsnMqh0QGjRtY9EW66huraeOg5%2FM0hKwcKRW2C3HvI7ph%2F7ilHNGdYTVP7RFqWp4GS8QdBSgDtfGo24vJuXjvnzj8wjkOu6ERkbPFbrxgm6&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240902T024418Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=ASIAZOC5JNS2VLMKX66D%2F20240902%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=ae21107d5b8f6b53b00147a3498f2d4ac73f80b6b8802bd3347b9482573edddb"

    menu_image_data = base64.b64encode(httpx.get(menu_image_url).content).decode(
        "utf-8"
    )

    header_image_url = "https://nutrition-menus.s3.us-east-1.amazonaws.com/torchys/torchys_header.png?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEIL%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIFAAY52t3Yn7xbGxs5Hb0gi3%2BvLpCZXBST3GGwgMZwD9AiEA%2FS%2FFKlFaKkgL2V%2BZH9ousGFSjraEhhCpWpG3QN73C3wqtQIImv%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2NDg3MzU3MTQ0ODUiDJ%2FtiayLG2AM1gFk0iqJAoRlCJ1MGkLE9xltefI3UOOlrboAW7d90GCOJPgtH2xXxSMSpDntLXzBNgX5wP0%2BrBzT5TJyhA%2BLna3okodarKChvn8637q2DJgJhvATrjZcr42S8pdeOxBuPYFTG44bJd0huu1JYFG8upQD%2Bx0iDGW5jLYzma5wKtOqLKbBAUODglbeEExX8RwZZzq3J1LNj9grADCtMDZVQgWZUhp0cfT5vC7STGVvoeKsMHAClWxOft4DLDqkkQHj5eDdPgMjwh8C4mzxjJGiaGiiJJni21gUNL1CKTlfDmgr2n3q814HkuSa%2BTDUhjkPN48FSsqbED2e%2FP%2B1HVerFi8JbMldT3RHGthyQpoGn3EwvJDUtgY63wHSyH0diBbFegyzIV0jja7wzOdsaZYeaCOBSb2NGEg0iSz7Ef88ZCqAr3Eax2DuCFJMDLM8rQyu6EOY8SuHZC5EDJ9T3nmnArQMPX5IFxg7vzesMA46g9tnOQq4L36A6rfyWb7ixZpE4okOxCsW2jgNYsxtrlN4Afdgk5hq5gu18QjWi0%2FLSoWCl%2BrBdDdLVcsnMqh0QGjRtY9EW66huraeOg5%2FM0hKwcKRW2C3HvI7ph%2F7ilHNGdYTVP7RFqWp4GS8QdBSgDtfGo24vJuXjvnzj8wjkOu6ERkbPFbrxgm6&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240902T030203Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=ASIAZOC5JNS2VLMKX66D%2F20240902%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=b2b9e6dacef27168fd884b9245458c5f9f234da83ec64ead551ad8fd85e5beb5"
    header_image_data = base64.b64encode(httpx.get(header_image_url).content).decode(
        "utf-8"
    )

    prompt_template_str = """
        You are going to be given urls to two images. One image will be part of a nutritional information table for a restaurant. The second image will be the header of the nutritional information table. You will need to extract the nutritional information from the table and output the data as a csv file. This is the first image {nutritional_information}. This is the second image {header}."""


    s3 = boto3.client("s3")
    bucket_name = "nutrition-menus"
    folder_name = "torchys/"

    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)

    # Construct URLs for all the images in the folder
    image_urls = []
    if "Contents" in response:
        for obj in response["Contents"]:
            image_key = obj["Key"]
            # Skip any folder placeholders (e.g., keys ending with '/')
            if not image_key.endswith("/"):
                # Construct the URL (assuming your bucket is public, adjust as necessary for your setup)
                image_url = f"https://{bucket_name}.s3.amazonaws.com/{image_key}"
                image_urls.append(image_url)
    else:
        print(f"No objects found in {bucket_name}/{folder_name}")

    model = ChatOpenAI(model="gpt-4o-mini")

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

    save_to_csv(filtered_res, f"""res_csvs/omni_test.csv""")


if __name__ == "__main__":
    main()
