import os
import requests
from dotenv import load_dotenv

load_dotenv()
hf_api_key = os.getenv("HF_API_KEY")
model = "Qwen/Qwen2.5-7B-Instruct"

urls = [
    f"https://router.huggingface.co/models/{model}",
    f"https://router.huggingface.co/hf-inference/models/{model}",
    f"https://router.huggingface.co/v1/chat/completions",
    f"https://api.huggingface.co/v1/chat/completions"
]

payload = {
    "model": model,
    "messages": [
        {"role": "user", "content": "hi"}
    ]
}

headers = {"Authorization": f"Bearer {hf_api_key}"}

for url in urls:
    try:
        r = requests.post(url, json=payload, headers=headers)
        print(f"{url} => {r.status_code}")
        if r.status_code != 200:
            print(f"   {r.text}")
    except Exception as e:
        print(f"{url} => Error: {e}")
