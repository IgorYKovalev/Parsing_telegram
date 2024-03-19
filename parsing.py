from decouple import config
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantCreator
import pandas as pd
import asyncio

api_id = config('API_ID')
api_hash = config('API_HASH')
phone = config('PHONE')


async def get_creator(client, channel):
    participants = await client(GetParticipantsRequest(
        channel, ChannelParticipantsAdmins(), 0, 100, hash=0
    ))
    for participant in participants.participants:
        if isinstance(participant, ChannelParticipantCreator):
            user_id = participant.user_id
            user = next((u for u in participants.users if u.id == user_id), None)
            return user.username if user else None
    return None


async def main():
    async with TelegramClient(phone, api_id, api_hash) as client:
        await client.start(phone=phone)
        channels_info = []
        with open('groups.txt', 'r') as file:
            for line in file:
                channel_url = line.strip()
                if channel_url:
                    channel = await client.get_entity(channel_url)
                    creator_login = await get_creator(client, channel)
                    channels_info.append([channel.title, f'@{creator_login}' if creator_login else '-'])

        df = pd.DataFrame(channels_info, columns=['Group', 'Creator Login'])
        df.to_excel('channels_creators.xlsx', index=False)


if __name__ == "__main__":
    asyncio.run(main())
    print('Парсинг участников группы успешно выполнен.')
