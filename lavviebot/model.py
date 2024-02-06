""" Data classes for Lavviebot """
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from datetime import datetime


@dataclass
class LavviebotData:
    """ Dataclass for Lavviebot data. """

    litterboxes: dict[int, LitterBox]
    lavvie_scanners: dict[int, LavvieScanner]
    lavvie_tags: dict[int, LavvieTag]
    cats: dict[int, Cat]


@dataclass
class LitterBox:
    """ Dataclass for Lavviebot litter box. """

    device_id: int
    device_name: str
    iot_code_tail: str
    latest_firmware: str
    router_ssid: str
    min_bottom_weight_pnds: float
    beacon_battery: Any | None
    current_firmware: str
    motor_state: int
    top_litter_status: int
    waste_drawer_status: int
    wait_time: int
    litter_type: int
    litter_bottom_amount_pnds: float
    humidity: int
    temperature_c: int
    last_seen: datetime
    last_cat_used_name: str
    last_used_duration: int
    last_used: datetime
    times_used_today: int
    error_log: list


@dataclass
class LavvieScanner:
    """ Dataclass for LavvieScanner. """

    device_id: int
    device_name: str
    iot_code_tail: str
    latest_firmware: str
    router_ssid: str
    wifi_status: bool
    current_firmware: str
    last_seen: datetime


@dataclass
class LavvieTag:
    """ Dataclass for LavvieTag. """

    device_id: int
    device_name: str
    iot_code_tail: str
    latest_firmware: str
    current_firmware: str
    battery: int
    last_seen: datetime


@dataclass
class Cat:
    """ Dataclass for Lavviebot cat. """

    cat_id: int
    location_id: int
    cat_name: str
    has_lavvietag: bool
    cat_weight_pnds: float
    duration: float
    poop_count: int
    zoomies: int  # expressed as a count
    running: int  # expressed in seconds
    walking: int  # expressed in seconds
    resting: int  # expressed in seconds
    sleeping: int # expressed in seconds

