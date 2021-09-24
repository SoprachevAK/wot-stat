import json
import os


class Config:
    config = {}
    defaultParams = {
        'version': '0.0.8',
        'urlSend': 'https://wotstat.soprachev.com/api/mod/sendShot',
        'urlInit': 'https://wotstat.soprachev.com/api/mod/initBattle'
    }

    def __init__(self, ConfigPath, DefaultParams=None):
        if DefaultParams:
            self.defaultParams = DefaultParams

        if os.path.exists(ConfigPath):
            with open(ConfigPath, "r") as f:
                self.config = json.loads(f.read())

    def get(self, key):
        return self.config[key] if key in self.config else self.defaultParams[
            key] if key in self.defaultParams else None


Config = Config