import os

import BigWorld

from constants import ARENA_BONUS_TYPE
from avatar import PlayerAvatar
from vehiclegunrotator import VehicleGunRotator
from helpers import getShortClientVersion
from account_shared import readClientServerVersion

from hook import g_overrideLib


@g_overrideLib.registerEvent(PlayerAvatar, 'showTracer')
def showTracer(self, *a, **k):
    wotApiProvider.invoke('PlayerAvatar.showTracer', self, *a, **k)


@g_overrideLib.registerEvent(PlayerAvatar, 'shoot')
def shoot(self, *a, **k):
    wotApiProvider.invoke('PlayerAvatar.shoot', self, *a, **k)


@g_overrideLib.registerEvent(PlayerAvatar, 'onEnterWorld')
def onEnterWorld(self, *a, **k):
    wotApiProvider.invoke('PlayerAvatar.onEnterWorld', self, *a, **k)


@g_overrideLib.registerEvent(PlayerAvatar, 'updateTargetingInfo')
def updateTargetingInfo(self, *a, **k):
    wotApiProvider.invoke('PlayerAvatar.updateTargetingInfo', self, *a, **k)


@g_overrideLib.registerEvent(VehicleGunRotator, 'setShotPosition')
def setShotPosition(self, *a, **k):
    wotApiProvider.invoke('VehicleGunRotator.setShotPosition', self, *a, **k)


@g_overrideLib.registerEvent(VehicleGunRotator, '_VehicleGunRotator__updateGunMarker')
def updateGunMarker(self, *a, **k):
    wotApiProvider.invoke('VehicleGunRotator.updateGunMarker', self, *a, **k)


class WotApiProvider:
    listeners = {}

    def add_listener(self, name, callback):
        if name not in self.listeners:
            self.listeners[name] = []
        self.listeners[name].append(callback)

    def remove_listener(self, name, calback):
        if name in self.listeners:
            self.listeners = filter(lambda t: t != calback, self.listeners)

    def invoke(self, name, obj, *a, **k):
        if name in self.listeners:
            for f in self.listeners[name]:
                f(obj, *a, **k)

    arenaTags = dict(
        [(v, k) for k, v in ARENA_BONUS_TYPE.__dict__.iteritems() if isinstance(v, int)])

    @staticmethod
    def short_tank_tag(tag):
        tags = {
            'lightTank': 'LT',
            'mediumTank': 'MT',
            'heavyTank': 'HT',
            'AT-SPG': 'AT',
            'SPG': 'SPG',
        }
        return tags[tag] if tag in tags else tag

    @staticmethod
    def short_shell_tag(tag):
        tags = {
            'ARMOR_PIERCING_CR': 'APCR',
            'HIGH_EXPLOSIVE': 'HE',
            'HOLLOW_CHARGE': 'HC',
            'ARMOR_PIERCING': 'AP',
        }
        return tags[tag] if tag in tags else tag

    @staticmethod
    def num_game_version():
        return getShortClientVersion().split('v.')[1].strip()

    def get_game_version(self):
        return readClientServerVersion()[1]

    def get_arena_name(self):
        return BigWorld.player().arena.arenaType.geometry

    def get_arena_unique_ID(self):
        return BigWorld.player().arenaUniqueID

    def get_tank_name(self):
        return BigWorld.entities[BigWorld.player().playerVehicleID].typeDescriptor.name

    def get_tank_type(self):
        tags = BigWorld.player().vehicleTypeDescriptor.type.tags
        type = \
            'mediumTank' if 'mediumTank' in tags \
            else 'heavyTank' if 'heavyTank' in tags \
            else 'AT-SPG' if 'AT-SPG' in tags \
            else 'SPG' if 'SPG' in tags \
            else 'lightTank' if 'lightTank' in tags \
            else 'None'
        return type

    def get_tank_level(self):
        return BigWorld.player().vehicleTypeDescriptor.level

    def get_tank_equipments(self):
        return map(lambda x: x.groupName if x else None, BigWorld.player().vehicle.getOptionalDevices())

    def get_gun_name(self):
        return BigWorld.player().vehicleTypeDescriptor.gun.name

    def get_gun_dispersion_angle(self):
        return BigWorld.player().vehicleTypeDescriptor.gun.shotDispersionAngle

    def get_player_name(self):
        return BigWorld.player().name

    def get_player_BDID(self):
        player = BigWorld.player()
        return player.arena.vehicles[player.playerVehicleID]['accountDBID']

    def get_player_clan(self):
        player = BigWorld.player()
        return player.arena.vehicles[player.playerVehicleID]['clanAbbrev']

    def get_player_position(self):
        return BigWorld.player().getOwnVehiclePosition()

    def get_battle_mode(self):
        return self.arenaTags[BigWorld.player().arena.bonusType]


wotApiProvider = WotApiProvider()
