import os
import aiohttp
import httpx
import base64
import requests

from openai import AsyncOpenAI

from config_data import Config, load_config


config: Config = load_config()
client = AsyncOpenAI(api_key=config.claud.api_key, base_url="https://api.proxyapi.ru/openai/v1/chat/completions")

async def process_image(image_url) -> str:


    headers = {
        "Authorization": f"Bearer {config.claud.api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [

            {"role": "system", "content": [{"type": "text", "text": config.claud.user}]},
            {"role": "user", "content": [{"type": "text", "text": config.claud.prompt}]},
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": image_url}}]}
            # "role": "user",
            # "content": [
            #     {"type": "text", "text": "Что изображено на картинке?"},
            #     {"type": "image_url", "image_url": {"url": image_url}}
            # ]

        ],
        "max_tokens": 300
    }


    response = requests.post(config.claud.api_url, json=payload, headers=headers)
    if response.status_code == 200:
        print(response.json())
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "GPT-4o не вернул содержимого.")
    print(type(config.claud.api_key))
    return f"Ошибка API: {response.text}"

    # async with httpx.AsyncClient() as client:
    #     response = await client.post(config.claud.api_url, json=payload, headers=headers)
    #     data = await response.json()
    #     return data["choices"][0]["message"]["content"]
    #     # else:
    #     #     return f"Ошибка API: {await response.text()}"

    # async with aiohttp.ClientSession() as session:
    #     async with session.post(config.claud.api_url, headers=headers, json=payload) as response:
    #         if response.status == 200:
    #             data = await response.json()
    #             # Логируем в консоль модель и полный ответ
    #             print("Используемая модель:", data.get("model", "Не указана"))
    #             print("Полный ответ от API:", data)
    #             response_text = await response.text()
    #             print("--------------------------f", response.status, response_text)

    #             # Возвращаем текст ответа
    #             return data.get("choices", [{}])[0].get("message", {}).get("content", "GPT-4o не вернул содержимого.")
    #         else:
    #             error_text = await response.text()
    #             print("Ошибка запроса:", response.status, error_text)  # Логируем ошибку
    #             return f"Ошибка {response.status}: {error_text}"
   #-------------------------------
    # with open(image_path, "rb") as image_file:
    #     response = client.responses.create(
    #         model="gpt-3.5",
    #         message=[{"role": "user", "content": prompt}],
    #         max_tokens=100
    #     )
    # return response["choises"][0]["message"]["content"]
#--------------------------------
    # config: Config = load_config()
    # headers = {
    #     "x-api-key": config.claud.api_key,
    #     "anthropic-version": "2023-06-01",
    #     "Content-Type": "application/json",
    # }
    # data = {
    #     "model": "claude-3-opus",
    #     "messages": [{"role": "user", "content": prompt}],
    #     "max_tokens": 1
    # }
    # response = requests.post(config.claud.api_url, json=data, headers=headers)

    # if response.status_code == 200:
    #     return response.json()["content"]
    # print(type(config.claud.api_key))
    # return f"Ошибка API: {response.text}"