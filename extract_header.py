import base64
import os

import httpx
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from utils.aws_util import generate_presigned_url_for_file_with_keyword
from utils.file_names import CLEANED_TEXTRACT_RES_CSVS


def extract_header(curr_header_img_url: str, curr_res_name: str) -> str:

    model = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

    bucket_name = "nutrition-menus"
    # folder_base = "metadata"
    # folder_name = folder_base + "/"
    # keyword = "header"

    sample_header_img_url = generate_presigned_url_for_file_with_keyword(
        bucket_name=bucket_name, keyword="header", folder_prefix="metadata/"
    )

    print("this is sample header img url: ", sample_header_img_url)

    system_message = SystemMessage(
        content=[
            {
                "type": "text",
                "text": " You are going to be given an image containing details about the header of a nutritional information "
                + " table in base64 format. You need to extract the header information and output it in a csv format.",
            },
            {
                "type": "text",
                "text": f"""An example of could be the following:
                "<user>: data:image/jpeg;base64,{sample_header_img_url}"
                "<system>: Name, Cal., Cal. Fat, Total Fat, Sat. Fat, Trans. Fat, Chol, Sodium, Carb, Fiber, Sugar, Protein""",
            },
        ],
    )

    header_img_data = base64.b64encode(httpx.get(curr_header_img_url).content).decode(
        "utf-8"
    )

    human_message = HumanMessage(
        content=[
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{header_img_data}"},
            },
        ],
    )

    res = model.invoke([system_message, human_message])

    with open(f"""{CLEANED_TEXTRACT_RES_CSVS}/{curr_res_name}.csv""", "a") as file:
        file.write(res.content)
        file.write("\n")

    print("printing header row now ")

    print(res.content)

    return "-1"
