import anthropic
import requests

from openai import AsyncOpenAI

from config_data import Config, load_config


config: Config = load_config()
client_anthropi = anthropic.AsyncAnthropic(api_key=config.claud.api_key, base_url="https://api.proxyapi.ru/anthropic/v1/messages")
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
