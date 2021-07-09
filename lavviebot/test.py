#To run this locally you will need to remove "lavviebot." from "lavviebot.devices.lavviebot" and "lavviebot.cats.cat" in the lavviebotapi.py file
import asyncio
from lavviebotapi import LavvieBotApi


async def main() -> None:
    client = LavvieBotApi('username', 'password')
    print(client.discover_cats())



asyncio.get_event_loop().run_until_complete(main())
