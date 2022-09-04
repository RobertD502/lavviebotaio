# Lavviebotaio
Asynchronous Python library for the PurrSong API utilized by LavvieBot S litter boxes.

This package provides an API client for the [PurrSong](https://purrsong.com/en/) API allowing you to fetch the status of Lavviebot S litter boxes and cats associated with a PurrSong account.


**The API is not published by PurrSong, so it may break without notice.**


## Installation

```
pip3 install lavviebotaio
```

This package depdends on [aiohttp](https://docs.aiohttp.org/en/stable/), and requires Python 3.9 or greater.

## Usage

```python
import asyncio
from lavviebot import LavviebotClient
from aiohttp import ClientSession

async def main():
    async with ClientSession() as session:
    
        # Create a client using PurrSong account email and password
        client = LavviebotClient("email", "password", session)

        # Discover all litter boxes associated with account
        litter_boxes = await client.async_discover_litter_boxes()
        
        # Discover all cats associated with account. Requires `location id` as an `int`.
        cats = await client.async_discover_cats(123)
        
        # Get info pertaining to a particular litter box using device_id integer
        litter_box_status = await client.async_get_litter_box_status(device_id)
        
        # Get litter box usage log pertaining to a particular litter box using device_id integer
        litter_box_log = await client.async_get_litter_box_cat_log(device_id)
        
        # Get weights, durations, and usage counts for "Unknown" cat using cat_id integer (cat_id for unknown cats is equal to the location_id)
        unknown_cat_status = await client.async_get_unknown_status(cat_id)
        
        # Get weights, durations, and usage counts for a particular cat using cat_id integer
        cat_status = await client.async_get_cat_status(cat_id)
        
        # Get all associated litter boxes and cats and store in a LavviebotData object
        get_all = await client.async_get_data()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```
