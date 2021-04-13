import asyncio
from lavviebotapi import LavvieBotApi


async def main() -> None:
    client = LavvieBotApi('username', 'password')
    print(client.discover_cats())



asyncio.get_event_loop().run_until_complete(main())
