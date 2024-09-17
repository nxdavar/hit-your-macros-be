from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

client = OpenAI()

response = client.images.generate(
    model="dall-e-3",
    prompt="Panda Express Hot Szechuan Tofu",
    size="1024x1024",
    quality="standard",
    style="natural",
    n=1,
)

image_url = response.data[0].url

print(image_url)
