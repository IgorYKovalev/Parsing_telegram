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


async def dump_last_n_messages(channel, n):
    limit_msg = min(n, 100)
    all_messages = []

    class DateTimeEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            if isinstance(o, bytes):
                return list(o)
            return json.JSONEncoder.default(self, o)

    try:
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=0,
            offset_date=None,
            add_offset=0,
            limit=limit_msg,
            max_id=0,
            min_id=0,
            hash=0
        ))
    except Exception as e:
        print(f"Ошибка при получении истории чата: {e}")
        return

    if not history.messages:
        print("Чат не содержит сообщений.")
        return

    messages = history.messages
    for message in messages:
        user = await client.get_entity(message.from_id)
        sender_username = user.username or f"{user.first_name} {user.last_name}"
        message_info = {
            'text': message.message,
            'sender_username': sender_username
        }
        all_messages.append(message_info)

    with open('last_n_messages.json', 'w', encoding='utf8') as outfile:
        json.dump(all_messages, outfile, ensure_ascii=False, cls=DateTimeEncoder)

    print(f"Выгружено последних {len(all_messages)} сообщений.")


async def main():
    url = input("Введите ссылку на канал или чат: ")
    channel = await client.get_entity(url)
    n = int(input("Введите количество сообщений для выгрузки: "))
    await dump_last_n_messages(channel, n)

with client:
    client.loop.run_until_complete(main())
