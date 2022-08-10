import base64
import json
from json import JSONDecodeError

import aiohttp


async def make_request(url: str, method: str, headers, data=None):
    async with aiohttp.ClientSession() as session:
        valid = {'get', 'post', 'update', 'delete', 'patch'}
        if method not in valid:
            raise ValueError(f"results: status must be one of {valid}.")
        if method == 'post':
            async with session.post(url=url, data=data, headers=headers) as response:
                resp = await response.read()
                try:
                    return json.loads(resp)
                except JSONDecodeError:
                    print('There is no response')
                    return None
        elif method == 'get':
            async with session.get(url=url, data=data, headers=headers) as response:
                resp = await response.read()
                return json.loads(resp)
        elif method == 'patch':
            async with session.patch(url=url, data=data, headers=headers) as response:
                resp = await response.read()
                try:
                    return json.loads(resp)
                except JSONDecodeError:
                    print('There is no response')
                    return None


class SpaceBot:
    def __init__(self, base_url, bot_id, bot_secret):
        self.id = bot_id
        self.secret = bot_secret
        self.url = base_url
        self.token = None
        self.project_info = None
        self.tags = None
        self.boards = None
        self.project_statuses = None

    @classmethod
    async def rise(cls, base_url, bot_id, bot_secret, main_project: str):
        bot = SpaceBot(base_url, bot_id, bot_secret)
        await bot.auth()
        await bot.get_project_id(main_project)
        await bot.get_tags()
        await bot.get_issues_boards()
        await bot.get_project_statuses(bot.project_info["id"])
        return bot

    async def auth(self):
        secret = base64.b64encode(f'{self.id}:{self.secret}'.encode('ascii')).decode('utf-8')
        url = f'{self.url}/oauth/token'
        data = {
            'grant_type': 'client_credentials',
            'scope': '**'
        }
        headers = {
            'Authorization': f'Basic {secret}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        auth = await make_request(url, 'post', headers, data)
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
        await make_request(url, 'post', headers, data)

    async def get_tags(self):
        url = f'{self.url}/api/http/projects/{self.project_info["id"]}/planning/tags'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        self.tags = (await make_request(url, 'get', headers))['data']

    async def get_project_id(self, project_name):
        url = f'{self.url}/api/http/projects'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        all_projects = await make_request(url, 'get', headers)
        for project in all_projects['data']:
            if project['name'] == project_name:
                self.project_info = project

    async def get_issues_boards(self):
        url = f'{self.url}/api/http/projects/{self.project_info["id"]}/planning/boards'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        self.boards = (await make_request(url, 'get', headers))['data']

    async def get_issues_from_board(self, board_name):
        board_id = str()
        for board in self.boards:
            if board['name'] == board_name:
                board_id = board['id']
                break
        if board_id:
            url = f'{self.url}/api/http/projects/planning/boards/{board_id}/issues'
        else:
            print('There is no such board')
            return
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        issues_list = (await make_request(url, 'get', headers))['data']
        return issues_list

    async def update_issue_tag(self, board_name, issue_number, tag_name):
        issues = await self.get_issues_from_board(board_name)
        issue_id, tag_id = str(), str()
        for issue in issues:
            if issue['number'] == issue_number:
                issue_id = issue['id']
                break
        for tag in self.tags:
            if tag['name'] == tag_name:
                tag_id = tag['id']
                break
        if issue_id and tag_id:
            url = f'{self.url}/api/http/projects/{self.project_info["id"]}/planning/issues/{issue_id}/tags/{tag_id}'
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.token}'
            }
            await make_request(url, 'post', headers)
        else:
            if issue_id:
                print('There is no tag at this name')
            elif tag_id:
                print(f'There is no issue number {issue_number} at board {board_name}')
            else:
                print('Tag name and issue number are invalid!')

    async def base_board_info(self, board_id):
        url = f'{self.url}/api/http/projects/planning/boards/id:{board_id}?$fields=info(columns(columns(name))),id,name'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        return await make_request(url, 'get', headers)

    async def get_project_statuses(self, project_id):
        url = f'{self.url}/api/http/projects/id:{project_id}/planning/issues/statuses?$fields=id,name'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        self.project_statuses = await make_request(url, 'get', headers)

    async def update_issue_status(self, board_name, issue_number, status_name):
        board_id, status_id, issue_id = str(), str(), str()
        issues = await self.get_issues_from_board(board_name)
        for issue in issues:
            if issue['number'] == issue_number:
                issue_id = issue['id']
                break
        for board in self.boards:
            if board['name'] == board_name:
                board_id = board['id']
                break
        for status in self.project_statuses:
            if status['name'] == status_name:
                status_id = status['id']
        if board_id and status_id and issue_id:
            url = f'{self.url}/api/http/projects/{self.project_info["id"]}/planning/issues/id:{issue_id}'
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.token}'
            }
            data = json.dumps({"status": status_id})
            await make_request(url, 'patch', headers, data)
