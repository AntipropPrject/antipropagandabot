import asyncio
import aiohttp
import json
import base64


async def make_request(url, headers, data):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url=url, data=data) as response:
            print(response.status)
            resp = await response.read()
            print(json.loads(resp))
            return json.loads(resp)


class SpaceBot:
    def __init__(self, base_url, bot_id, bot_secret):
        self.id = bot_id
        self.secret = bot_secret
        self.url = base_url
        self.token = None

    async def auth(self):
        secret = base64.b64encode(f'{self.id}:{self.secret}'.encode('ascii')).decode('utf-8')
        print(secret)
        url = f'{self.url}/oauth/token'
        data = {
            'grant_type': 'client_credentials',
            'scope': '**'
        }
        headers = {
            'Authorization': f'Basic {secret}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        auth = await make_request(url, headers, data)
        self.token = auth['access_token']
        return auth['access_token']

    async def send_message(self, channel_name, text):
        url = f'{self.url}/api/http/chats/messages/send-message'
        data = json.dumps(
            {"content": {
                "className": "ChatMessage.Text",
                "text": text
            },
                "channel": f"channel:name:{channel_name}"
            })
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        await make_request(url, headers, data)