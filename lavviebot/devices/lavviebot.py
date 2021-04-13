import time
import collections


class LavvieBot(object):
    def __init__(self, data, api):
        self.api = api
        self.lavviebot_id = data['lavviebotId']
        self.name = data['lavviebotNickname']
        self.refresh()

    def refresh(self):
        lavviebot_status = self.api.lavviebot_status(self)
        self.waste_status = lavviebot_status['wasteDrawerStatus']
        self.top_litter_status = lavviebot_status['topLitterStatus']
        self.litter_top_amount = lavviebot_status['litterTopAmount'] / 455.1
        self.litter_bottom_amount = lavviebot_status['litterBottomAmount'] / 455.1
        self.litter_type = lavviebot_status['litterType']
        self.min_bottom_ben_weight = lavviebot_status['minBottomBenWeight'] / 455.1
        self.min_bottom_nat_weight = lavviebot_status['minBottomNatWeight'] / 455.1
        self.temperature = lavviebot_status['temperature']
        self.humidity = lavviebot_status['humidity']
        self.wait_time = lavviebot_status['waitTime']
