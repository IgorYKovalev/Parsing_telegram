from decouple import config
import json
from telethon.sync import TelegramClient
from datetime import datetime
from telethon.tl.functions.messages import GetHistoryRequest

api_id = config('API_ID')
api_hash = config('API_HASH')
phone = config('PHONE')

client = TelegramClient(phone, api_id, api_hash)
client.start()


async def dump_all_messages(channel):
    offset_msg = 0
    limit_msg = 100
    all_messages = []
    total_messages = 0
    total_count_limit = 0

    class DateTimeEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            if isinstance(o, bytes):
                return list(o)
            return json.JSONEncoder.default(self, o)

    while True:
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_msg,
            offset_date=None,
            add_offset=0,
            limit=limit_msg,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            all_messages.append(message.message)
        offset_msg = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break

    with open('channel_messages.json', 'w', encoding='utf8') as outfile:
        json.dump(all_messages, outfile, ensure_ascii=False, cls=DateTimeEncoder)


async def main():
    url = input("Введите ссылку на канал или чат: ")
    channel = await client.get_entity(url)
    await dump_all_messages(channel)

with client:
    client.loop.run_until_complete(main())

print("Парсинг сообщений группы успешно выполнен.")
