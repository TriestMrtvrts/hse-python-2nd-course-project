import httpx

OLLAMA_URL = "http://localhost:11434"
MODEL = "mistral:latest"  

class OllamaClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=120)

    async def generate(self, prompt: str) -> str:
        response = await self.client.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
            },
        )

        response.raise_for_status()
        data = response.json()

        print("OLLAMA RAW RESPONSE:", data)  # 👈 ДОБАВЬ

        text = data.get("response", "")
        if not text:
            return "(модель не ответила)"
        return text


qwen_client = OllamaClient()