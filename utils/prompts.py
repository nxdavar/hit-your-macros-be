from string import Template

# prompt used when extracting nutrition data from tabular data on images

tabular_data_extraction_prompt = [
    {
        "type": "text",
        "text": " You are going to be given urls to two images. One image will be part of a nutritional information table for a restaurant. "
        + " The second image will be the header of the nutritional information table. You will need to extract the nutritional information "
        + "from the table and output the data as a csv file. For the menu item name, ensure it is the first column of the csv file."
        + "Also if the menu item name contains a comma, please replace it with a hyphen. Likewise, strip any of the following characters"
        + " from the menu item name: ['†', '*, '®']",
    },
    # Template("data:image/jpeg;base64, $base64_image_1")
    {
        "type": "image_url",
        "image_url": Template("data:image/jpeg;base64, $base64_image_1"),
    },
    {
        "type": "image_url",
        "image_url": Template("data:image/jpeg;base64, $base64_image_2"),
    },
]
