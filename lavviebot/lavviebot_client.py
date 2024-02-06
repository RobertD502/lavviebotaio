"""Python API for Lavviebot S Litter Box"""
from __future__ import annotations

from typing import Any, Tuple

from datetime import date, datetime
from zoneinfo import ZoneInfo

import asyncio
import logging

from http.cookies import SimpleCookie

from aiohttp import ClientResponse, ClientSession

from .exceptions import LavviebotAuthError, LavviebotError, LavviebotRateLimit
from .model import Cat, LavviebotData, LavvieScanner, LavvieTag, LitterBox
from .constants import (ACCEPT, ACCEPT_ENCODING, ACCEPT_LANGUAGE,
                        APP_VERSION, BASE_URL, CAT_STATUS, CONNECTION,
                        CONTENT_TYPE, COOKIE_QUERY, DISCOVER_CATS,
                        DISCOVER_DEVICES, LANGUAGE, LAVVIE_SCANNER_STATUS,
                        LAVVIE_TAG_STATUS, LB_CAT_LOG, LB_ERROR_LOG, LB_STATUS,
                        TIMEOUT, TIME_ZONE, TOKEN_QUERY, UNKNOWN_STATUS, USER_AGENT,)

LOGGER = logging.getLogger("lavviebotaio")

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
        return None

    async def get_cookie(self) -> SimpleCookie:
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

    async def get_token(self) -> Tuple:
        """ Use email/password to obtain token """

        if self.cookie is None:
            await self.login()
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

        response = await self._post(headers, token_payload)
        if 'errors' in response:
            message = response['errors'][0]['message']
            raise LavviebotAuthError(message)
        else:
            data = response['data']['login']
            return data['userToken'], data['hasCat'], data['userId']

    async def async_discover_cats(self, location_id: int) -> dict[str, Any]:
        """ Gets all cats linked to PurrSong account """

        if self.cookie is None or self.token is None:
            await self.login()
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
            "operationName": "CatMain",
            "variables": {
                "includeLavvieCare": True,
                "includeLavvieTag": True,
                "includeDetailCatInfo": True,
                "includeLocation": True,
                "locationId": location_id
            },
            "query": DISCOVER_CATS
        }
        response = await self._post(headers, dc_payload)
        if 'errors' in response:
            message = response['errors'][0]['message']
            if message == "Please login again.":
                await self.login()
                return await self.async_discover_cats(location_id)
            else:
                raise LavviebotError(message)
        else:
            return response


    async def async_discover_devices(self) -> dict[str, Any]:
        """ Gets all iot devices linked to PurrSong account """

        if self.cookie is None or self.token is None:
            await self.login()
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
            "operationName": "PurrsongTabLocations",
            "variables": {},
            "query": DISCOVER_DEVICES
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
        litter_boxes: list = []
        lavvie_scanners: list = []
        lavvie_tags: list = []
        response = await self.async_discover_devices()
        LOGGER.debug(f'Device discovery response: {response}')
        locations = response['data']['getLocations']
        for location in locations:
            for device in location['getIots']:
                if device['lavviebot']:
                    litter_boxes.append(device)
                if device['lavvieScanner']:
                    lavvie_scanners.append(device)
                if device['lavvieTag']:
                    lavvie_tags.append(device)

        # Handle Litter boxes
        litter_box_data: dict[int, LitterBox] = {}
        litter_box: dict

        for litter_box in litter_boxes:
            device_id: int = litter_box.get('id')
            device_name: str = litter_box['lavviebot'].get('nickname')

            state = await self.async_get_litter_box_status(device_id)
            LOGGER.debug(f'Litter box {device_name} response: {state}')
            iot_code_tail: str = state[0]['data']['getIotDetail'].get('iotCodeTail')
            latest_firmware: str = state[0]['data']['getIotDetail'].get('latestFirmwareVersion')
            router_ssid: str = state[0]['data']['getIotDetail']['lavviebot'].get('routerSSID')
            """ Weight in Pounds """
            min_bottom_weight_pnds: float = state[0]['data']['getIotDetail']['lavviebot'].get('minBottomWeight') / 455.1
            beacon_battery = state[0]['data']['getIotDetail']['lavviebot'].get('beaconBattery')
            current_firmware: str = state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get(
                'currentFirmwareVersion')
            motor_state: int = state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get('motorState')
            top_litter_status: int = state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get(
                'topLitterStatus')
            waste_drawer_status: int = state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get(
                'wasteDrawerStatus')
            wait_time: int = state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get('waitTime')
            litter_type: int = state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get('litterType')
            """ Weight in Pounds """
            litter_bottom_amount_pnds: float = state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get(
                'litterBottomAmount') / 455.1
            humidity: int = state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get('humidity')
            temperature_c: int = state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get('temperature')
            last_seen: datetime = datetime.fromtimestamp(
                int(state[0]['data']['getIotDetail']['lavviebot']['recentLavviebotLog'].get('creationTime')) / 1000,
                tz=ZoneInfo('Asia/Seoul')).astimezone()

            """ Variables from Cat Usage Log """
            nickname = state[1]['data']['getLavviebotPoopRecord']['catUsageHistory'][00].get('nickname')
            last_cat_used_name = 'Unknown' if nickname is None else nickname

            last_used_duration: int = state[1]['data']['getLavviebotPoopRecord']['catUsageHistory'][00].get('duration')
            last_used: datetime = datetime.fromtimestamp(
                int(state[1]['data']['getLavviebotPoopRecord']['catUsageHistory'][00].get('creationTime')) / 1000,
                tz=ZoneInfo('Asia/Seoul')).astimezone()
            # Get the oldest usage record for today in order to determine number of times litter box was used today
            today_date: date = date.today()
            today_usage_list: list = []
            for usage_record in state[1]['data']['getLavviebotPoopRecord']['catUsageHistory']:
                epoch_to_date = datetime.fromtimestamp(int(usage_record['creationTime']) / 1000).date()
                if epoch_to_date == today_date:
                    today_usage_list.append(usage_record)
                else:
                    break
            times_used_today: int = len(today_usage_list)

            # Litter box error log
            error_log: list = state[2]['data']['getIotErrorLog']['errorLogs']

            litter_box_data[device_id] = LitterBox(
                device_id=device_id,
                device_name=device_name,
                iot_code_tail=iot_code_tail,
                latest_firmware=latest_firmware,
                router_ssid=router_ssid,
                min_bottom_weight_pnds=min_bottom_weight_pnds,
                beacon_battery=beacon_battery,
                current_firmware=current_firmware,
                motor_state=motor_state,
                top_litter_status=top_litter_status,
                waste_drawer_status=waste_drawer_status,
                wait_time=wait_time,
                litter_type=litter_type,
                litter_bottom_amount_pnds=litter_bottom_amount_pnds,
                humidity=humidity,
                temperature_c=temperature_c,
                last_seen=last_seen,
                last_cat_used_name=last_cat_used_name,
                last_used_duration=last_used_duration,
                last_used=last_used,
                times_used_today=times_used_today,
                error_log=error_log,
            )

        # Handle LavvieScanners
        lavvie_scanner_data: dict[int, LavvieScanner] = {}
        lavvie_scanner: dict

        for lavvie_scanner in lavvie_scanners:
            device_id: int = lavvie_scanner.get('id')
            device_name: str = lavvie_scanner['lavvieScanner'].get('nickname')

            state = await self.async_get_iot_device_status(device_id, "lavvie_scanner")
            LOGGER.debug(f'LavvieScanner {device_name} response: {state}')
            iot_code_tail: str = state['data']['getIotDetail'].get('iotCodeTail')
            latest_firmware: str = state['data']['getIotDetail'].get('latestFirmwareVersion')
            router_ssid: str = state['data']['getIotDetail']['lavvieScanner'].get('routerSSID')
            wifi_status: bool = state['data']['getIotDetail']['lavvieScanner'].get('wifiStatus')
            current_firmware: str = state['data']['getIotDetail']['lavvieScanner']['recentLavvieScannerLog'].get(
                'currentFirmwareVersion')
            last_seen: datetime = datetime.fromtimestamp(
                int(state['data']['getIotDetail']['lavvieScanner']['recentLavvieScannerLog'].get('creationTime')) / 1000,
                tz=ZoneInfo('Asia/Seoul')).astimezone()

            lavvie_scanner_data[device_id] = LavvieScanner(
                device_id=device_id,
                device_name=device_name,
                iot_code_tail=iot_code_tail,
                latest_firmware=latest_firmware,
                router_ssid=router_ssid,
                wifi_status=wifi_status,
                current_firmware=current_firmware,
                last_seen=last_seen
            )

        # Handle LavvieTags
        lavvie_tag_data: dict[int, LavvieTag] = {}
        lavvie_tag: dict

        for lavvie_tag in lavvie_tags:
            device_id: int = lavvie_tag.get('id')
            device_name: str = lavvie_tag['lavvieTag'].get('nickname')

            state = await self.async_get_iot_device_status(device_id, "lavvie_tag")
            LOGGER.debug(f'LavvieTag {device_name} response: {state}')
            iot_code_tail: str = state['data']['getIotDetail'].get('iotCodeTail')
            latest_firmware: str = state['data']['getIotDetail'].get('latestFirmwareVersion')
            current_firmware: str = state['data']['getIotDetail']['lavvieTag'].get(
                'currentFirmwareVersion')
            battery: int = state['data']['getIotDetail']['lavvieTag'].get('battery')
            last_seen: datetime = datetime.fromtimestamp(
                int(state['data']['getIotDetail']['lavvieTag'].get('recentConnectionTime')) / 1000,
                tz=ZoneInfo('Asia/Seoul')).astimezone()

            lavvie_tag_data[device_id] = LavvieTag(
                device_id=device_id,
                device_name=device_name,
                iot_code_tail=iot_code_tail,
                latest_firmware=latest_firmware,
                current_firmware=current_firmware,
                battery=battery,
                last_seen=last_seen
            )

        """ Get all cats """

        cats = []
        cat_data: dict[int, Cat] = {}
        if self.has_cat:
            for location in locations:
                response = await self.async_discover_cats(location['id'])
                LOGGER.debug(f'Discovered cats response: {response}')
                if location['hasUnknownCat']:
                    unknown_cat = {
                        'id': location['id'],
                        'location_id': location['id'],
                        'is_unknown': True,
                        "has_lavvietag": False
                    }
                    cats.append(unknown_cat)
                """ Append all cats to cat list. """
                for cat in response['data']['getPets']:
                    cat["is_unknown"] = False
                    cat["location_id"] = location['id']
                    cat["has_lavvietag"] = True if cat['lavvieTag'] else False
                    cats.append(cat)

            cat: dict
            for cat in cats:
                cat_id: int = cat.get('id')
                cat_location_id: int = cat.get('location_id')
                has_lavvietag: bool = cat.get('has_lavvietag')
                # Today's Activity data
                zoomies: int = 0
                running: int = 0
                walking: int = 0
                resting: int = 0
                sleeping: int = 0

                # Handle getting Unknown cat data
                if cat.get('is_unknown'):
                    cat_name: str = "Unknown"
                    unknown_status = await self.async_get_unknown_status(cat_id)
                    LOGGER.debug(f'Unknown cat status response: {unknown_status}')
                    today_weight = unknown_status['data']['weightData']
                    today_duration = unknown_status['data']['poopDuration']
                    today_count = unknown_status['data']['poopCount']
                    if today_weight:
                        cat_weight_pnds = 0.0 if today_weight['today'] is None else (today_weight['today'] / 455.1)
                    else:
                        cat_weight_pnds = 0.0
                    if today_duration:
                        duration = 0.0 if today_duration['today'] is None else today_duration['today']
                    else:
                        duration = 0.0
                    if today_count:
                        poop_count = 0 if today_count['today'] is None else today_count['today']
                    else:
                        poop_count = 0
                    zoomies = zoomies
                    running = running
                    walking = walking
                    resting = resting
                    sleeping = sleeping
                # Handle regular Cats
                else:
                    cat_name: str = cat['cat'].get('nickname')
                    cat_status = await self.async_get_cat_status(cat_id, cat_location_id)
                    LOGGER.debug(f'Cat {cat_name} status response: {cat_status}')
                    weight_data = cat_status['data']['weightData']
                    duration_data = cat_status['data']['poopDuration']
                    count_data = cat_status['data']['poopCount']
                    activity_data = cat_status['data']['todayActivity']
                    if weight_data:
                        cat_weight_pnds = 0.0 if weight_data['today'] is None else (weight_data['today'] / 455.1)
                    else:
                        cat_weight_pnds = 0.0
                    if duration_data:
                        duration = 0.0 if duration_data['today'] is None else duration_data['today']
                    else:
                        duration = 0.0
                    if count_data:
                        poop_count = 0 if count_data['today'] is None else count_data['today']
                    else:
                        poop_count = 0
                    # Today's Activity data. Only go through logic if cat has associated LavvieTAG
                    if has_lavvietag:
                        for data in activity_data:
                            if data['woodadaCount']:
                                zoomies += data['woodadaCount']
                            if data['run']:
                                running += data['run']
                            if data['walk']:
                                walking += data['walk']
                            if data['rest']:
                                sleeping += data['rest']
                            if data['grooming']:
                                resting += data['grooming']

                cat_data[cat_id] = Cat(
                    cat_id=cat_id,
                    location_id=cat_location_id,
                    cat_name=cat_name,
                    has_lavvietag=has_lavvietag,
                    cat_weight_pnds=cat_weight_pnds,
                    duration=duration,
                    poop_count=poop_count,
                    zoomies=zoomies,
                    running=running,
                    walking=walking,
                    resting=resting,
                    sleeping=sleeping,
                )

        purrsong_data = LavviebotData(
            litterboxes=litter_box_data,
            lavvie_scanners=lavvie_scanner_data,
            lavvie_tags=lavvie_tag_data,
            cats=cat_data
        )
        LOGGER.debug(f'Purrsong API data returned: {purrsong_data}')
        return purrsong_data

    async def async_get_litter_box_status(self, device_id: int) -> list[dict[str, Any]]:
        """ Get most recent status available for litter box """

        if self.cookie is None or self.token is None:
            await self.login()
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
        lbs_payload = [
            {
                "operationName": "GetLavviebotDetails",
                "variables": {
                    "data": {
                        "iotId": device_id
                    }
                },
                "query": LB_STATUS
            },
            {
                "operationName": "GetLavviebotPoopRecord",
                "variables": {
                    "data": {
                        "iotId": device_id
                    }
                },
                "query": LB_CAT_LOG
            },
            {
                "operationName": "GetIotErrorLog",
                "variables": {
                    "data": {
                        "iotId": device_id
                    }
                },
                "query": LB_ERROR_LOG
            }
        ]

        response = await self._post(headers, lbs_payload)
        for resp in response:
            if 'errors' in resp:
                message = resp['errors'][0]['message']
                if message == "Please login again.":
                    await self.login()
                    return await self.async_get_litter_box_status(device_id)
                else:
                    raise LavviebotError(resp)
        return response

    async def async_get_litter_box_cat_log(self, device_id: int) -> dict[str, Any]:
        """ Get usage log that is associated with the litter box """

        if self.cookie is None or self.token is None:
            await self.login()
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

    async def async_get_litter_box_error_log(self, device_id: int) -> dict[str, Any]:
        """ Get error log that is associated with the litter box """

        if self.cookie is None or self.token is None:
            await self.login()
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
        lbel_payload = {
            "operationName": "GetIotErrorLog",
            "variables": {
                "data": {
                    "iotId": device_id
                }
            },
            "query": LB_ERROR_LOG
        }
        response = await self._post(headers, lbel_payload)
        if 'errors' in response:
            message = response['errors'][0]['message']
            if message == "Please login again.":
                await self.login()
                return await self.async_get_litter_box_error_log(device_id)
            else:
                raise LavviebotError(message)
        else:
            return response

    async def async_get_iot_device_status(self, iot_id: int, device_type: str) -> dict[str, Any]:
        """
        Get details about an IoT device. Only used for LavvieScanners and LavvieTAGs.
        device_type needs to be one of lavvie_scanner or lavvie_tag.
        """

        operation_name: str | None = None
        query: str | None = None

        if device_type == "lavvie_scanner":
            operation_name = "GetLavvieScannerDetails"
            query = LAVVIE_SCANNER_STATUS
        if device_type == "lavvie_tag":
            operation_name = "GetLavvieTagDetails"
            query = LAVVIE_TAG_STATUS

        if self.cookie is None or self.token is None:
            await self.login()

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
        iot_payload = {
            "operationName": operation_name,
            "variables": {
                "data": {
                    "iotId": iot_id
                }
            },
            "query": query
        }

        iot_response = await self._post(headers, iot_payload)
        if 'errors' in iot_response:
            message = iot_response['errors'][0]['message']
            if message == "Please login again.":
                await self.login()
                return await self.async_get_iot_device_status(iot_id, device_type)
            else:
                raise LavviebotError(message)
        return iot_response

    async def async_get_unknown_status(self, cat_id: int) -> dict[str, Any]:
        """ Get most recent status for Unknown cat, if present. """

        if self.cookie is None or self.token is None:
            await self.login()
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
        unknown_payload = {
            "operationName": "GetUnknownPoopData",
            "variables": {
                    "locationId": cat_id,
                    "days": "days",
                    "weight": "weight",
                    "poopCount": "poopCount",
                    "poopDuration": "duration"
            },
            "query": UNKNOWN_STATUS
        }

        unknown_response = await self._post(headers, unknown_payload)
        if 'errors' in unknown_response:
            message = unknown_response['errors'][0]['message']
            if message == "Please login again.":
                await self.login()
                return await self.async_get_unknown_status(cat_id)
            else:
                raise LavviebotError(message)
        return unknown_response

    async def async_get_cat_status(self, cat_id: int, cat_location_id: int) -> dict[str, Any]:
        """ Get most recent status for single cat """

        if self.cookie is None or self.token is None:
            await self.login()
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
        cat_status_payload = {
            "operationName": "GetCatHealthInfo",
            "variables": {
                "locationId": cat_location_id,
                "petId": cat_id,
                "days": "days",
                "weight": "weight",
                "poopCount": "poopCount",
                "poopDuration": "duration"
            },
            "query": CAT_STATUS
        }

        cat_status_response = await self._post(headers, cat_status_payload)
        if 'errors' in cat_status_response:
            message = cat_status_response['errors'][0]['message']
            if message == "Please login again.":
                await self.login()
                return await self.async_get_cat_status(cat_id, cat_location_id)
            else:
                raise LavviebotError(message)
        return cat_status_response

    async def _post(
            self, headers: dict[str, Any],
            payload: dict[str, Any] | list[dict[str, Any]], is_cookie: bool | None = None) -> SimpleCookie | dict[str, Any]:
        """ Make Post API call to PurrSong servers """

        async with self._session.post(
                BASE_URL, headers=headers, json=payload,
                timeout=self.timeout) as resp:
            return await self._response(resp, is_cookie)

    @staticmethod
    async def _response(resp: ClientResponse, is_cookie: bool) -> SimpleCookie | dict[str, Any]:
        """ Check response for any errors & return original response if none """

        # 500 status returned when current token has been rate-limited
        if resp.status != 200:
            response_message = await resp.json()
            if 'errors' in response_message:
                error_message = response_message['errors'][0]['message']
                if error_message == "Too many requests, please try again in a few minutes.":
                    raise LavviebotRateLimit(
                        'You have been rate limited by the Purrsong API. Decrease the polling frequency or create a new ClientSession.'
                    )
                else:
                    raise LavviebotError(f'Lavviebot API error: {response_message}')
            else:
                raise LavviebotError(f'Lavviebot API error: {response_message}')

        try:
            if is_cookie:
                response: SimpleCookie = resp.cookies
            else:
                response: dict[str, Any] = await resp.json()
        except Exception as e:
            raise LavviebotError(f'Could not return json: {e}') from e
        return response
