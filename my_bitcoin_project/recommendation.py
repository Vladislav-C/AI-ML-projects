"""Script to call ChatGPT for recommendations"""

import base64
from openai import OpenAI

# Path to image and news
IMAGE_PATH = "bitcoin_price.png"
NEWS_PATH = "bitcoin_news.txt"

def main():
    client = OpenAI()

    # Getting the Base64 string
    base64_image = encode_image(IMAGE_PATH)
    prompt = build_prompt(NEWS_PATH)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    },
                ],
            }
        ],
    )

    recommendation = response.choices[0].message.content

    with open("recommendation.txt", "w", encoding="utf-8") as file:
        file.write(recommendation)


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def build_prompt(news_path):
    news_articles = open(news_path, "r")

    prompt = f"""
    Based on the following Bitcoin data:

    Price trend: see the attached image.

    News highlights: {news_articles.read()}

    Should I buy or sell Bitcoin? Please provide a brief explanation!
    Note: This is for experimental purposes only and not financial advice.
    """
    return prompt


main()