import asyncio
import time
from aiohttp import ClientSession
from .lavviebot_client import LavviebotClient


async def main() -> None:
    async with ClientSession() as session:
        client = LavviebotClient('email', 'password', session)
        await client.login()
        await client.async_get_data()



start_time = time.time()
asyncio.get_event_loop().run_until_complete(main())
print("--- %s seconds ---" % (time.time() - start_time))
