
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import PyPDF2
import camelot
import csv
import os
import openai
from dotenv import load_dotenv



def split_pdf(input_pdf_path, output_dir):
    # Open the PDF file
    with open(input_pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(reader.pages)

        # Check if the PDF has more than one page
        if num_pages <= 1:
            print(f"The PDF file has only {num_pages} page(s). No need to split.")
            return

        # Iterate over each page and save it as a separate PDF
        for i in range(num_pages):
            writer = PyPDF2.PdfWriter()
            writer.add_page(reader.pages[i])

            output_pdf_path = f"{output_dir}/page_{i + 1}.pdf"
            with open(output_pdf_path, 'wb') as output_pdf:
                writer.write(output_pdf)

            print(f"Saved page {i + 1} to {output_pdf_path}")



# extracts the path names for all files in a folder
def extract_file_paths(folder_path):
    file_paths = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            file_paths.append(full_path)

    return file_paths


# use the camelot library to extract text from pdf
def extract_text_from_pdf(file_path: str) -> str:
    tables = camelot.read_pdf(file_path)
    tables_str = ""

    for table in tables:
        # Convert the table to a DataFrame
        df = table.df
        
        # Convert the DataFrame to a string
        table_string = df.to_string(index=False, header=False)
        
        # Append the table string to the large string
        tables_str += table_string + "\n\n"  # Adding some space between tables

    return tables_str
    

# saves files to csv
def save_to_csv(self, response, file_path):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Response"])
        writer.writerow([response])


def main():
    # prompt = ChatPromptTemplate.from_template([
    # ("system", "You are an agent that will be converting " + 
    #   " nutritional information outputted from the camelot-py " + 
    #    " library and converting it to a csv file." + 
    #    "Ensure the menu item is the first column of the csv"),
    # ])
    load_dotenv()

    # Example usage
    input_pdf_path = 'restaurant_assets/panda_express/pdf/panda_express_nutritional_menu.pdf'
    output_dir = 'restaurant_assets/panda_express/pdf/pdf_split'       

    split_pdf(input_pdf_path, output_dir)


    nutrition_pdf_pages = extract_file_paths(output_dir)


    for page in nutrition_pdf_pages[:1]: 
        camelot_res = extract_text_from_pdf(page)

        prompt_template_str = '''
            Please convert the following nutritional information outputted from the camelot-py library {result} into a csv file. Ensure the menu item is the first column of the csv.'''

        prompt = ChatPromptTemplate.from_template(prompt_template_str)

        model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=1,
            max_tokens=3000,
            timeout=None,
            top_p=1,
            max_retries=2,
        )

        runnable_save_to_csv = RunnableLambda(save_to_csv)


        lcel_chain = prompt | model 
        res = lcel_chain.invoke({"result": camelot_res, "file_path": "restaurant_assets/panda_express/csv/panda_express_nutritional_menu.csv"})
        print(res.content)
        



if __name__ == "__main__":
    main()


