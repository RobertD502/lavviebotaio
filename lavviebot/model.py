""" Data classes for Lavviebot """
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from datetime import datetime


@dataclass
class LavviebotData:
    """ Dataclass for Lavviebot data. """

    litterboxes: dict[int, LitterBox]
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

@dataclass
class Cat:
    """ Dataclass for Lavviebot cat. """

    cat_id: int
    cat_name: str
    cat_weight_pnds: float
    duration: float
    poop_count: int

