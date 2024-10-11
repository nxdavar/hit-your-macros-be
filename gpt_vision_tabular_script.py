import base64
import csv
import os

import httpx
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from utils.aws_util import generate_presigned_urls
from utils.prompt_helpers import populate_base64_images
from utils.prompts import tabular_data_extraction_prompt


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


def main():
    load_dotenv()

    # s3 = boto3.client("s3")
    bucket_name = "nutrition-menus"
    folder_base = "tatte"
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

        message_content = populate_base64_images(
            tabular_data_extraction_prompt, menu_image_data, header_image_data
        )

        message = HumanMessage(content=message_content)

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

        save_to_csv(filtered_res, f"""data/image_to_res_csvs/{folder_base}.csv""")


if __name__ == "__main__":
    main()
