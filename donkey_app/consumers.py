import json
import aiohttp
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "chat"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        print("✅ WebSocket connected")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        print("❌ WebSocket disconnected")

    async def receive(self, text_data):
        data = json.loads(text_data)
        prompt = data.get("prompt", "")
        print(f"📩 Message taken: {prompt}")

        if not prompt:
            await self.send(text_data=json.dumps({"error": "Empty prompt"}))
            return

        response = await self.get_ollama_response(prompt)

        await self.send(text_data=json.dumps({"response": response}))

    async def get_ollama_response(self, prompt):
        print(f"🚀 Call Ollama: {prompt}")
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "llama3",
            "prompt": prompt,
            "response_format": "json",
            "stream": False  # ВИМКНЕННЯ СТРИМІНГУ!
        }

        headers = {
            'Accept': 'application/json',
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    try:
                        data = await resp.json()  # ✅ Чіткий JSON, без потоків
                        print(f"✅ Have response from Ollama: {json.dumps(data, indent=2)}")
                        return data.get("response", "Take response error")
                    except aiohttp.client_exceptions.ContentTypeError:
                        print("❌ Error: server did not return JSON format")
                        return "Format error"
                else:
                    print(f"❌ Error Ollama: {resp.status}")
                    return "Call Ollama error"
