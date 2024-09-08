# external imports:
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from openai import OpenAI
import csv
import os
import boto3
import base64
import httpx
from dotenv import load_dotenv


# internal imports:
from utils.file_names import IMAGE_TO_RES_CSVS
from utils.aws_util import generate_presigned_urls


# saves files to csv
def save_to_csv(response, file_path):
    # Check if the file exists
    file_exists = os.path.isfile(file_path)

    # Open the file in append mode if it exists, otherwise in write mode
    with open(file_path, mode="a" if file_exists else "w", newline="") as file:
        writer = csv.writer(file)
        # Write the response to the CSV file
        writer.writerow([response])


# Store presigned URLs and their expiration times


def main():
    load_dotenv()

    bucket_name = "nutrition-menus"
    folder_base = "mcdonalds"
    folder_name = folder_base + "/"

    presigned_urls_cache = {}
    presigned_urls_dict = generate_presigned_urls(
        presigned_urls_cache, bucket_name, folder_name
    )

    print("presigned urls dict: ", presigned_urls_dict)
    print("presigned urls dict keys: ", presigned_urls_dict.keys())

    for file_key, menu_presigned_url in presigned_urls_dict.items():

        if file_key == folder_name:
            continue

        model = ChatOpenAI(model="gpt-4o-mini")
        menu_image_data = base64.b64encode(
            httpx.get(menu_presigned_url).content
        ).decode("utf-8")

        system_message = SystemMessage(
            content=[
                {
                    "type": "text",
                    "text": " You are going to be given a url to an image and macronutritional information fields. The image will contain "
                    + " nutritional information for a restaurant's menu item. Your goal is to extract the nutritional information fields "
                    + "from the image and output that menu item's nutritional information as a csv row with the menu item name as the first column."
                    + "The image may also contain information about the menu item's size: if a size is present, include it in the menu item name."
                    + "If you cannot extract nutritional information for a specific field, leave it blank."
                    + "Also, if the menu item name contains a comma, please replace it with a hypen with a whitespace before the hyphen and after"
                    + " the hyphen. Likewise, strip any of the following characters from the menu item name: ['†', '*, '®', '™']. These are the "
                    + "nutrition information fields you should extract: calories, total fat, saturated fat, trans fat, cholestrol, sodium,"
                    + "total carbohydratesm dietary fiber, sugars, protein, calcium, iron, potassium",
                },
                {
                    "type": "text",
                    "text": "An example of could be the following:"
                    + "<user>: data:image/jpeg;base64,https://www.goprep.com/wp-content/uploads/2019/06/screen-shot-2019-06-19-at-6.09.23-pm.png"
                    + "<system>: Cajun Chicken with Asapragus and Brown Rice,460,6,1.5,0,120,3530,61,7,3,0,42,1,0,960",
                },
            ],
        )

        human_message = HumanMessage(
            content=[
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{menu_image_data}"},
                },
            ],
        )

        res = model.invoke([system_message, human_message])
        print(res.content)
        print(type(res.content))
        res_tmp = res.content
        print("this is prefiltered res: ", res_tmp)
        # res_tmp_start_idx = res_tmp.find("```csv")
        # res_tmp_end_idx = res_tmp.find("```", res_tmp_start_idx + 6)
        # print("res start idx: ", res_tmp_start_idx)
        # print("res end idx: ", res_tmp_end_idx)
        # filtered_res = res_tmp[res_tmp_start_idx + 6 : res_tmp_end_idx]
        # print("this is filtered res: ", filtered_res)

        save_to_csv(res_tmp, f"""{IMAGE_TO_RES_CSVS}/{folder_base}.csv""")


if __name__ == "__main__":
    main()
