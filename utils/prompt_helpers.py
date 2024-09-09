# populate base64 image urls for the tabular_data_extraction_prompt
def populate_base64_images(template, base64_image_1, base64_image_2):
    # Replace the placeholders in the template dictionary
    populated_dict = [
        {
            "type": item["type"],
            "image_url": {
                "url": item["image_url"]["url"].substitute(
                    base64_image_1=base64_image_1, base64_image_2=base64_image_2
                )
            },
        }
        for item in template
    ]
    return populated_dict
