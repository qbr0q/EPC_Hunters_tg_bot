def send_text_request(client, prompt):
    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        quality="high",
        n=1
    )

    return response.data[0].b64_json


def send_text_and_photo_request(client, image_url, template_instruction):
    vision_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": template_instruction},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        max_tokens=1000
    )

    prompt = vision_response.choices[0].message.content.strip()

    new_image_url = send_text_request(client, prompt)
    return new_image_url
