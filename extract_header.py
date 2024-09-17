# external imports:

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from string import Template


# internal imports:
from utils.aws_util import generate_presigned_url_for_file_with_keyword
from utils.file_names import CLEANED_TEXTRACT_RES_CSVS
from utils.prompt_helpers import populate_base64_images


def extract_header(curr_header_img_url: str, curr_res_name: str) -> str:
    model = ChatOpenAI(model="gpt-4o-mini")

    bucket_name = "nutrition-menus"
    folder_base = "metadata"
    folder_name = folder_base + "/"
    keyword = "header"

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

    human_message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": f"""{curr_header_img_url}""",
            },
        ],
    )

    res = model.invoke([system_message, human_message])

    with open(f"""{CLEANED_TEXTRACT_RES_CSVS}/{curr_res_name}.csv""", "a") as file:
        file.write(res.content)
        file.write("\n")

    print("printing header row now ")

    print(res.content)

    return -1
