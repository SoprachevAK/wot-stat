import json
import os
import BigWorld
from ..utils import print_log

class Config:
    config = {}
    defaultParams = {
        'version': '1.0.0.0',
        'urlSend': 'https://wotstat.soprachev.com/api/mod/sendShot',
        'urlInit': 'https://wotstat.soprachev.com/api/mod/initBattle',
        'eventURL': ''
    }

    def __init__(self, ConfigPath, DefaultParams=None):
        if DefaultParams:
            self.defaultParams = DefaultParams

        if os.path.exists(ConfigPath):
            with open(ConfigPath, "r") as f:
                try:
                    self.config = json.loads(f.read())
                    print_log('found new config:')
                    print_log(self.config)
                except Exception, e:
                    print_log('load config error')
                    print_log(e)


    def get(self, key):
        return self.config[key] if key in self.config else self.defaultParams[
            key] if key in self.defaultParams else None


Config = Config