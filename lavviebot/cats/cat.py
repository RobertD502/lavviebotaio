import time
import collections


class Cat(object):
    def __init__(self, data, idx, api):
        self.api = api
        self.index = idx
        if data['catName'] == '':
            self.cat_name = 'Unknown'
        else:
            self.cat_name = data['catName']
        self.refresh()

    def refresh(self):
        cat_status = self.api.cat_status(self)
        self.cat_attributes = {}
        if len(cat_status) > 0:
            cs = cat_status[self.index]
            if cs.get('catWeight') == None:
                self.cat_attributes['cat_weight'] = None
            else:
                self.cat_attributes['cat_weight'] = cs['catWeight'] / 453592
            if cs['poopLogs']['dailyPoops'][6].get('newCatWeightAvg') == None:
                self.cat_attributes['cat_weight_today'] = None
            else:
                self.cat_attributes['cat_weight_today'] = cs['poopLogs']['dailyPoops'][6]['newCatWeightAvg'] / 455.1
            if cs['poopLogs']['dailyPoops'][6].get('poopCount') == None:
                self.cat_attributes['poop_count'] = None
            else:
                self.cat_attributes['poop_count'] = cs['poopLogs']['dailyPoops'][6]['poopCount']
            if cs['poopLogs']['dailyPoops'][6].get('durationAvg') == None:
                self.cat_attributes['duration'] = None
            else:
                self.cat_attributes['duration'] = cs['poopLogs']['dailyPoops'][6]['durationAvg']
