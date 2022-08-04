"""Python API for Lavviebot S Litter Box"""

from __future__ import annotations
from typing import Any

import time
from datetime import datetime
from zoneinfo import ZoneInfo
import asyncio
from http.cookies import SimpleCookie
from aiohttp import ClientResponse, ClientSession



from lavviebot.exceptions import LavviebotAuthError, LavviebotError
from lavviebot.model import Cat, LavviebotData, LitterBox
from lavviebot.constants import *


class LavviebotClient:
    """Lavviebot Client"""

    def __init__(
            self, email: str, password: str,
            session: ClientSession | None = None,
            timeout: int = TIMEOUT
    ) -> None:
        """
        email: PurrSong App account email
        password: PurrSong App account password
        session: aiohttp.ClientSession or None to create a new session
        """
        self.email: str = email
        self.password: str = password
        self._session = session if session else ClientSession()
        self.cookie: SimpleCookie | None = None
        self.token: str | None = None
        self.has_cat: bool | None = None
        self.user_id: int | None = None
        self.timeout: int = timeout


    async def login(self) -> None:
        """ Get cookie and token to be used in subsequent API calls """
        self.cookie = await self.get_cookie()
        self.token, self.has_cat, self.user_id = await self.get_token()
        return self.user_id


    async def get_cookie(self) -> ClientResponse:
        """ Get cookie by checking PurrSong server status """
        headers = {
        'Accept': ACCEPT,
        'Accept-Encoding': ACCEPT_ENCODING,
        'Accept-Language': ACCEPT_LANGUAGE,
        'Connection': CONNECTION,
        'Content-Type': CONTENT_TYPE,
        'User-Agent': USER_AGENT
        }

        cookie_payload = {
            "operationName": "CheckServerStatus",
            "variables": {
                "data": {
                    "language": LANGUAGE
                }
            },
            "query": COOKIE_QUERY
        }

        response = await self._post(headers, cookie_payload, is_cookie=True)
        return response

    async def get_token(self):
        """ Use email/password to obtain token """
        headers = {
            'Accept': ACCEPT,
            'Cookie': self.cookie,
            'Accept-Encoding': ACCEPT_ENCODING,
            'Accept-Language': ACCEPT_LANGUAGE,
            'Connection': CONNECTION,
            'Content-Type': CONTENT_TYPE,
            'User-Agent': USER_AGENT
        }
        token_payload = {
            "operationName": "Login",
            "variables": {
                "data": {
                    "email": self.email,
                    "password": self.password,
                    "appVersion": APP_VERSION,
                    "timezone": TIME_ZONE,
                    "timezoneCountry": "US"
                }
            },
            "query": TOKEN_QUERY
        }

        response = await self._post(headers,token_payload)
        if 'errors' in response:
            message = response['errors'][0]['message']
            raise LavviebotAuthError(message)
        else:
            data = response['data']['login']
            return data['userToken'], data['hasCat'], data['userId']


    async def async_discover_cats(self) -> ClientResponse:
        """ Gets all cats linked to PurrSong account"""
        headers = {
        'Accept': ACCEPT,
        'Cookie': self.cookie,
        'Accept-Encoding': ACCEPT_ENCODING,
        'Accept-Language': ACCEPT_LANGUAGE,
        'Authorization': self.token,
        'Connection': CONNECTION,
        'Content-Type': CONTENT_TYPE,
        'User-Agent': USER_AGENT
        }
        dc_payload = {
            "operationName": "CatMainDrawerLocations",
            "variables":{},
            "query": DISCOVER_CATS
        }
        response =  await self._post(headers,dc_payload)
        if 'errors' in response:
            message = response['errors'][0]['message']
            if message == "Please login again.":
                await self.login()
                return await self.async_discover_cats()
            else:
                raise LavviebotError(message)
        else:
            return response


    async def async_discover_litter_boxes(self) -> ClientResponse:
        """ Gets all litter boxes linked to PurrSong account """
        headers = {
            'Accept': ACCEPT,
            'Cookie': self.cookie,
            'Accept-Encoding': ACCEPT_ENCODING,
            'Accept-Language': ACCEPT_LANGUAGE,
            'Authorization': self.token,
            'Connection': CONNECTION,
            'Content-Type': CONTENT_TYPE,
            'User-Agent': USER_AGENT
        }
        dlb_payload = {
            "operationName": "IotMainDrawerLocations",
            "variables": {},
            "query": DISCOVER_LB
        }
        response = await self._post(headers, dlb_payload)
        if 'errors' in response:
            message = response['errors'][0]['message']
            if message == "Please login again.":
                await self.login()
                return await self.async_discover_litter_boxes()
            else:
                raise LavviebotError(message)
        else:
            return response


    async def async_get_data(self) -> LavviebotData:
        """ Return dataclass with litter boxes and cats associated with account """

        if self.cookie is None or self.token is None:
            await self.login()
        litter_boxes = []
        response = await self.async_discover_litter_boxes()
        locations = response['data']['getLocations']
        for location in locations:
            for device in location['getIots']:
                litter_boxes.append(device)

        litter_box_data: dict[int, LitterBox] = {}
        litter_box: dict
        for litter_box in litter_boxes:
            device_id: int = litter_box.get('id')
            device_name: str = litter_box['lavviebot'].get('nickname')

            state = await self.async_fetch_all_endpoints(device_id)

            iot_code_tail: str = state[0]['data']['getIotDetail'].get('iotCodeTail')
            latest_firmware: str = state[0]['data']['getIotDetail'].get('latestFirmwareVersion')
            router_ssid: str = state[0]['data']['getIotDetail']['lavviebot'].get('routerSSID')
            """ Weight in Pounds """
            min_bottom_weight_pnds: float = state[0]['data']['getIotDetail']['lavviebot'].get('minBottomWeight') / 455.1
            beacon_battery = state[0]['data']['getIotDetail']['lavviebot'].get('beaconBattery')
            current_firmware: str = state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get('currentFirmwareVersion')
            motor_state: int = state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get('motorState')
            top_litter_status: int = state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get('topLitterStatus')
            waste_drawer_status: int = state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get('wasteDrawerStatus')
            wait_time: int = state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get('waitTime')
            litter_type: int = state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get('litterType')
            """ Weight in Pounds """
            litter_bottom_amount_pnds: float = state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get('litterBottomAmount') / 455.1
            humidity: int = state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get('humidity')
            temperature_c: int = state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get('temperature')
            last_seen: datetime = datetime.fromtimestamp(int(state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get('creationTime')) / 1000, tz=ZoneInfo('Asia/Seoul')).astimezone()

            """ Variables from Cat Usage Log """
            if state[1]['data']['getLavviebotPoopRecord']['catUsageHistory'][00].get('nickname') is None:
                last_cat_used_name: str = 'Unknown'
            else:
                last_cat_used_name: str = state[1]['data']['getLavviebotPoopRecord']['catUsageHistory'][00].get('nickname')

            last_used_duration: int = state[1]['data']['getLavviebotPoopRecord']['catUsageHistory'][00].get('duration')
            last_used: datetime = datetime.fromtimestamp(int(state[1]['data']['getLavviebotPoopRecord']['catUsageHistory'][00].get('creationTime')) / 1000, tz=ZoneInfo('Asia/Seoul')).astimezone()

            litter_box_data[device_id] = LitterBox(
                device_id = device_id,
                device_name = device_name,
                iot_code_tail = iot_code_tail,
                latest_firmware = latest_firmware,
                router_ssid = router_ssid,
                min_bottom_weight_pnds = min_bottom_weight_pnds,
                beacon_battery = beacon_battery,
                current_firmware = current_firmware,
                motor_state =  motor_state,
                top_litter_status = top_litter_status,
                waste_drawer_status = waste_drawer_status,
                wait_time = wait_time,
                litter_type = litter_type,
                litter_bottom_amount_pnds = litter_bottom_amount_pnds,
                humidity = humidity,
                temperature_c = temperature_c,
                last_seen = last_seen,
                last_cat_used_name = last_cat_used_name,
                last_used_duration = last_used_duration,
                last_used = last_used,
            )

        cats = []
        cat_data: dict[int, Cat] = {}
        if self.has_cat:
            response = await self.async_discover_cats()
            locations = response['data']['getLocations']
            for location in locations:
                if location['hasUnknownCat']:
                    unknown_cat = {
                        'id': location['id'],
                        'is_unknown': True
                    }
                    cats.append(unknown_cat)
                for cat in location['getPetCats']:
                    cat['is_unknown'] = False
                    cats.append(cat)

            cat: dict
            for cat in cats:
                cat_id: int = cat.get('id')

                if cat.get('is_unknown'):
                    cat_name: str = "Unknown"
                    state = await self.async_get_unknown_status(cat_id)
                    cat_weight_pnds: float = state['data']['getCatMainUnknownGraphData'][0]['graphData'][-1] / 455.1
                    duration: float = state['data']['getCatMainUnknownGraphData'][1]['graphData'][-1]
                    poop_count: int = state['data']['getCatMainUnknownGraphData'][2]['graphData'][-1]
                else:
                    cat_name: str = cat['cat'].get('nickname')
                    state =await self.async_get_cat_status(cat_id)
                    try:
                        cat_weight_pnds: float = state['data']['getCatMainGraphData'][0]['graphData'][-1] / 455.1
                        duration: float = state['data']['getCatMainGraphData'][1]['graphData'][-1]
                        poop_count: int = state['data']['getCatMainGraphData'][2]['graphData'][-1]
                    except IndexError:
                        cat_weight_pnds = 0
                        duration = 0
                        poop_count = 0

                cat_data[cat_id] = Cat(
                    cat_id = cat_id,
                    cat_name = cat_name,
                    cat_weight_pnds = cat_weight_pnds,
                    duration = duration,
                    poop_count = poop_count,
                )

        return LavviebotData(litterboxes=litter_box_data, cats=cat_data)


    async def async_fetch_all_endpoints(self, device_id: int) -> tuple[Any, Any]:
        """
        Parallel request are made to all endpoints for each litter box.
        returns a list containing latest status, and cat usage log
        """
        results = await asyncio.gather(*[
            self.async_get_litter_box_status(device_id),
            self.async_get_litter_box_cat_log(device_id)
            ],
        )
        return results


    async def async_get_litter_box_status(self, device_id: int) -> ClientResponse:
            """ Get most recent status available for litter box"""
            headers = {
                'Accept': ACCEPT,
                'Cookie': self.cookie,
                'Accept-Encoding': ACCEPT_ENCODING,
                'Accept-Language': ACCEPT_LANGUAGE,
                'Authorization': self.token,
                'Connection': CONNECTION,
                'Content-Type': CONTENT_TYPE,
                'User-Agent': USER_AGENT
            }
            lbs_payload = {
                "operationName": "GetLavviebotDetails",
                "variables": {
                    "data": {
                        "iotId": device_id
                    }
                },
                "query": LB_STATUS
            }
            response = await self._post(headers, lbs_payload)
            if 'errors' in response:
                message = response['errors'][0]['message']
                if message == "Please login again.":
                    await self.login()
                    return await self.async_get_litter_box_status(device_id)
                else:
                    raise LavviebotError(message)
            else:
                return response

    async def async_get_litter_box_cat_log(self, device_id: int) -> ClientResponse:
            """ Get usage log that is associated with the litter box"""
            headers = {
                'Accept': ACCEPT,
                'Cookie': self.cookie,
                'Accept-Encoding': ACCEPT_ENCODING,
                'Accept-Language': ACCEPT_LANGUAGE,
                'Authorization': self.token,
                'Connection': CONNECTION,
                'Content-Type': CONTENT_TYPE,
                'User-Agent': USER_AGENT
            }
            lbcl_payload = {
                "operationName": "GetLavviebotPoopRecord",
                "variables": {
                    "data": {
                        "iotId": device_id
                    }
                },
                "query": LB_CAT_LOG
            }
            response = await self._post(headers, lbcl_payload)
            if 'errors' in response:
                message = response['errors'][0]['message']
                if message == "Please login again.":
                    await self.login()
                    return await self.async_get_litter_box_cat_log(device_id)
                else:
                    raise LavviebotError(message)
            else:
                return response



    async def async_get_unknown_status(self, cat_id: int) -> ClientResponse:
            """ Get most recent status for Unknown cat if present """
            headers = {
                'Accept': ACCEPT,
                'Cookie': self.cookie,
                'Accept-Encoding': ACCEPT_ENCODING,
                'Accept-Language': ACCEPT_LANGUAGE,
                'Authorization': self.token,
                'Connection': CONNECTION,
                'Content-Type': CONTENT_TYPE,
                'User-Agent': USER_AGENT
            }
            cs_payload = {
                "operationName": "GetCatMainUnknownGraphData",
                "variables": {
                    "data": {
                        "locationId": cat_id,
                        "graphTypes": [
                            "weight",
                            "duration",
                            "poopCount"
                        ]
                    }
                },
                "query": UNKNOWN_STATUS
            }
            response = await self._post(headers, cs_payload)
            if 'errors' in response:
                message = response['errors'][0]['message']
                if message == "Please login again.":
                    await self.login()
                    return await self.async_get_unknown_status(cat_id)
                else:
                    raise LavviebotError(message)
            else:
                return response



    async def async_get_cat_status(self, cat_id: int) -> ClientResponse:
            """ Get most recent status for single cat """
            headers = {
                'Accept': ACCEPT,
                'Cookie': self.cookie,
                'Accept-Encoding': ACCEPT_ENCODING,
                'Accept-Language': ACCEPT_LANGUAGE,
                'Authorization': self.token,
                'Connection': CONNECTION,
                'Content-Type': CONTENT_TYPE,
                'User-Agent': USER_AGENT
            }
            cs_payload = {
                "operationName": "GetCatMainGraphData",
                "variables": {
                    "data": {
                        "petId": cat_id,
                        "graphTypes": [
                            "weight",
                            "duration",
                            "poopCount"
                        ]
                    }
                },
                "query": CAT_STATUS
            }
            response = await self._post(headers, cs_payload)
            if 'errors' in response:
                message = response['errors'][0]['message']
                if message == "Please login again.":
                    await self.login()
                    return await self.async_get_cat_status(cat_id)
                else:
                    raise LavviebotError(message)
            else:
                return response


    async def _post(
            self, headers: dict[str, Any],
            payload: dict[str,Any], is_cookie: bool | None = None) -> SimpleCookie | ClientResponse:
        """ Make Post API call to PurrSong servers """
        async with self._session.post(
                BASE_URL, headers=headers, json=payload,
                timeout=self.timeout) as resp:
            return await self._response(resp, is_cookie)

    @staticmethod
    async def _response(resp: ClientResponse, is_cookie: bool) -> SimpleCookie | ClientResponse:
        """ Check response for any errors & return original response if none """
        if resp.status != 200:
            raise LavviebotError(f'Lavviebot API error: {resp}')

        try:
            if is_cookie:
                response: SimpleCookie = resp.cookies
            else:
                response: dict[str, Any] = await resp.json()
        except Exception as e:
            raise LavviebotError(f'Could not return json: {e}') from e
        return response