# external imports:

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

# internal imports:
from utils.file_names import CLEANED_TEXTRACT_RES_CSVS


def clean_textract_row(textract_row: str, curr_res_name: str) -> str:
    model = ChatOpenAI(model="gpt-4o-mini")

    system_message = SystemMessage(
        content=[
            {
                "type": "text",
                "text": "You are going to be given a row of nutritional information data extracted from a table. "
                + "The first column represents the name of the menu item. Strip this column of any of the following "
                + "characters: ['†', '*, '®', '™']. Also, if the menu item name contains a comma, please replace it with a - "
                + "and add a space before and after the hyphen. All other columns are numerical. If any numerical column has "
                + "a string, replace it with the closest number to what the column is describing. If a column is numerical, "
                + "ensure that the number is a float and has no commas.",
            },
            {
                "type": "text",
                "text": "An example of could be the following:"
                + "<user>: ['Add Splash of Oat Milk,(2 oz)', '30', '1.5', '0', '0', '0', '25', '4', "
                + "'less than 1 gram', '2', '1']"
                + "<system>: 'Add Splash of Oat Milk - (2 oz)', 30, 1.5, 0, 0, 0, 25, 4, 0, 2, 1",
            },
        ],
    )

    human_message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": f"""{textract_row}""",
            },
        ],
    )

    res = model.invoke([system_message, human_message])

    with open(f"""{CLEANED_TEXTRACT_RES_CSVS}/{curr_res_name}.csv""", "a") as file:
        file.write(res.content)
        file.write("\n")

    print("printing cleaned row now: ")

    print(res.content)

    return "-1"
