
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
    base_name = os.path.basename(input_pdf_path)
    file_name = os.path.splitext(base_name)[0]

    # Open the PDF file
    with open(input_pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(reader.pages)

        files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
        # Check if the PDF has more than one page
        if num_pages <= 1 or len(files) == num_pages:
            print(f"The PDF file has only {num_pages} page(s). No need to split.")
            return

        # Iterate over each page and save it as a separate PDF
        for i in range(num_pages):
            writer = PyPDF2.PdfWriter()
            writer.add_page(reader.pages[i])

            output_pdf_path = f"{output_dir}/{file_name}_page_{i + 1}.pdf"
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
    tables_str_arr = []

    for table in tables:
        # Convert the table to a DataFrame
        df = table.df

        
        # Convert the DataFrame to a string

        tables_str_arr.append(df.to_string(index=False, header=False))
        

    return tables_str_arr
    

# saves files to csv
def save_to_csv(response, file_path):
    # Check if the file exists
    file_exists = os.path.isfile(file_path)
    
    # Open the file in append mode if it exists, otherwise in write mode
    with open(file_path, mode='a' if file_exists else 'w', newline='') as file:
        writer = csv.writer(file)
        
        # If the file doesn't exist, write the header
        if not file_exists:
            writer.writerow(["Response"])
        
        # Write the response to the CSV file
        writer.writerow([response])

def main():
    load_dotenv()
    # Example usage
    input_pdf_path = 'restaurant_assets/torchys/pdf/torchys_nutritional_info.pdf'
    output_dir = 'restaurant_assets/torchys/pdf/pdf_split'       

    split_pdf(input_pdf_path, output_dir)


    nutrition_pdf_pages = extract_file_paths(output_dir)


    for page in nutrition_pdf_pages: 
        camelot_table_arr = extract_text_from_pdf(page)

        for camelot_table in camelot_table_arr:
            print('this is camelot_table:', camelot_table)
            prompt_template_str = '''
                Please convert the following nutritional information outputted from the camelot-py library {nutritional_information} into a csv file. Ensure the menu item is the first column of the csv.'''

            prompt = ChatPromptTemplate.from_template(prompt_template_str)


            model = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                max_tokens=5000,
                timeout=None,
                top_p=1,
                max_retries=2,
            )
            lcel_chain = prompt | model 
            res = lcel_chain.invoke({"nutritional_information": camelot_table})
            csv_filtered = res.content[res.content.find("```csv") + 6: res.content.find("```", res.content.find("```csv") + 6)]
            print(csv_filtered)
            print('this is page:', page)
            output_file_temp = page.split('/')[-1].split('.')[0]
            output_file_name = f'''res_csvs/{output_file_temp[0: output_file_temp.find("nutritional") - 1]}.csv'''
            save_to_csv(csv_filtered, output_file_name)

        

if __name__ == "__main__":
    main()


