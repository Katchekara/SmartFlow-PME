import os
import requests
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/bert-base-uncased"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def query_hf(text: str):
    response = requests.post(API_URL, headers=headers, json={"inputs": text})
    return response.json()

if __name__ == "__main__":
    if HF_TOKEN:
        print("✅ Token trouvé :", HF_TOKEN[:10] + "...")
        result = query_hf("Bonjour, je teste mon API Hugging Face.")
        print("Réponse Hugging Face :", result)
    else:
        print("❌ Token introuvable. Vérifie ton fichier .env")
