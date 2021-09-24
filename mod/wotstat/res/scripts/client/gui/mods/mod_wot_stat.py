# -*- coding: utf-8 -*-


import json

import BigWorld
import BattleReplay

from vehicle_systems.tankStructure import TankPartNames
from gui import SystemMessages

from wot_stat.asyncResponse import post_async
from wot_stat.config import Config
from wot_stat.wotApiProvider import wotApiProvider
from wot_stat.modAutoUpdate import update_game_version, update_mod_version
# from wot_stat.crypto import encrypt
from wot_stat.cryptoPlaceholder import encrypt

configPath = './mods/configs/wot_stat/config.cfg'

config = None

pre_init = None
token = None

dis_angle_server = None
dis_angle_server_shot = None
pos_marker_server = None
pos_marker_server_shot = None

dis_angle_client = None
dis_angle_client_shot = None
pos_marker_client = None
pos_marker_client_shot = None

shot = None
shot_tag = None
auto_aim = None
gun_pos = None


def vector(t): return {'x': t.x, 'y': t.y, 'z': t.z}


def print_log(log):
    print("[MOD_WOT_STAT]: %s" % str(log))


def mod_name_version(version):
    return 'mod.wotStat_' + version + '.wotmod'


def mod_name():
    return mod_name_version(config.get('version'))


def set_token(val):
    global token
    token = val
    print_log('set token: ' + str(val))


def init_mod():
    global config

    config = Config(configPath)
    print_log('version ' + config.get('version'))

    update_game_version(mod_name())
    update_mod_version('https://wotstat.soprachev.com/cache/mod/version', 'mod.wotStat', config.get('version'),
                       on_start_update=lambda t: print_log(
                           'Found new mod version ' + t),
                       on_updated=lambda t: SystemMessages.pushMessage(
                           '[WotStat] успешно обновлён до версии ' + t +
                           '. После перезапуска игры обновление будет применено',
                           type=SystemMessages.SM_TYPE.Warning))

    wotApiProvider.add_listener('PlayerAvatar.onEnterWorld', on_enter_world)
    wotApiProvider.add_listener('PlayerAvatar.updateTargetingInfo', update_targeting_info)
    wotApiProvider.add_listener('VehicleGunRotator.updateGunMarker', update_gun_marker_client)
    wotApiProvider.add_listener('VehicleGunRotator.setShotPosition', update_gun_marker_server)
    wotApiProvider.add_listener('PlayerAvatar.showTracer', show_tracer)
    wotApiProvider.add_listener('PlayerAvatar.shoot', shoot)


def on_enter_world(self, *a):
    global pre_init
    global dis_angle_server
    global pos_marker_server

    dis_angle_server = None
    pos_marker_server = None
    set_token(None)

    pre_init = True

    print_log('----------onEnterWorld----------')


def update_targeting_info(self, turretYaw, gunPitch, maxTurretRotationSpeed, maxGunRotationSpeed,
                          shot_disp_multiplier_factor, *a):
    global pre_init

    if not pre_init:
        return

    pre_init = False

    if not BattleReplay.isPlaying():
        print_log('----------OnINIT----------')

        data = {
            'arenaName': str(wotApiProvider.get_arena_name()),
            'tankName': str(wotApiProvider.get_tank_name()),
            'playerName': str(wotApiProvider.get_player_name()),
            'playerID': wotApiProvider.get_player_BDID(),
            'arenaID': wotApiProvider.get_arena_unique_ID(),
            'gun': str(wotApiProvider.get_gun_name()),
            'tankTag': str(wotApiProvider.short_tank_tag(wotApiProvider.get_tank_type())),
            'startDis': (wotApiProvider.get_gun_dispersion_angle() * shot_disp_multiplier_factor),
            'gunPos': vector(wotApiProvider.get_player_position()),
            'tankLevel': wotApiProvider.get_tank_level(),
            'tankDevices': wotApiProvider.get_tank_equipments(),
            'modVersion': config.get('version'),
            'gameVersion': str(wotApiProvider.get_game_version()),
            'arenaBounds': str(wotApiProvider.get_battle_mode()),
            'clanAbbrev': wotApiProvider.get_player_clan()
        }

        print_log("send: %s" % json.dumps(
            {'map': data['arenaName'],
             'tank': data['tankName'],
             'mod': data['modVersion']}))

        post_async(config.get('urlInit'), encrypt(json.dumps(data)), set_token)


def update_gun_marker_server(self, vehicleID, shotPos, shotVec, dispersionAngle, *a, **k):
    global dis_angle_server
    global pos_marker_server
    dis_angle_server = dispersionAngle
    pos_marker_server = self._VehicleGunRotator__getGunMarkerPosition(
        shotPos, shotVec, (dispersionAngle, dispersionAngle))[0]


def update_gun_marker_client(self, *a, **k):
    global gun_pos
    global dis_angle_client
    global pos_marker_client

    player = BigWorld.player()

    if player.vehicle and player.vehicle.isStarted and player.vehicle.appearance:
        gun_pos = player.vehicle.appearance.compoundModel.node(
            TankPartNames.GUN).position
    else:
        gun_pos = player.getOwnVehiclePosition()
        gun_pos += player.vehicleTypeDescriptor.hull.turretPositions[0] + \
            player.vehicleTypeDescriptor.turret.gunPosition

    shotPos, shotVec = self.getCurShotPosition()
    pos_marker_client = self._VehicleGunRotator__getGunMarkerPosition(
        shotPos, shotVec, self._VehicleGunRotator__dispersionAngles)[0]

    dis_angle_client = self._VehicleGunRotator__dispersionAngles[0]


def shoot(self, isRepeat=False):
    global pos_marker_client_shot
    global pos_marker_server_shot
    global dis_angle_client_shot
    global dis_angle_server_shot
    global shot
    global shot_tag
    global auto_aim
    can_shoot, error = self.guiSessionProvider.shared.ammo.canShoot(isRepeat)
    if can_shoot:
        player = BigWorld.player()
        shell = player.vehicleTypeDescriptor.shot.shell

        pos_marker_client_shot = pos_marker_client
        pos_marker_server_shot = pos_marker_server
        dis_angle_client_shot = dis_angle_client
        dis_angle_server_shot = dis_angle_server
        shot = shell.name
        shot_tag = shell.kind
        auto_aim = (player.autoAimVehicle is not None)


def show_tracer(self, attackerID, shotID, isRicochet, effectsIndex, refStartPoint, refVelocity, gravity, *a):
    global token

    player = BigWorld.player()
    isOwnShoot = attackerID == player.playerVehicleID
    ownEffects = map(lambda t: t.shell.effectsIndex,
                     BigWorld.player().vehicleTypeDescriptor.gun.shots)

    if isOwnShoot and not isRicochet and (effectsIndex in ownEffects):
        if token:
            isServer = True if player.gunRotator.settingsCore.getSetting(
                'useServerAim') else False
            data = {
                'gravity': gravity,
                'velocity': vector(refVelocity),
                'gunPos': vector(gun_pos),
                'startPos': vector(refStartPoint),
                'posMarker': vector(pos_marker_server_shot if isServer else pos_marker_client_shot),
                'disAngle': dis_angle_server_shot if isServer else dis_angle_client_shot,
                'shell': str(shot),
                'isServer': isServer,
                'timeLeft': (player.arena.periodEndTime - BigWorld.serverTime()),
                'shellTag': str(wotApiProvider.short_shell_tag(shot_tag)),
                'token': str(token).replace('\"', ''),
                'gunDis': player.vehicleTypeDescriptor.gun.shotDispersionAngle,
                'ownGunDis': (
                    player.vehicleTypeDescriptor.gun.shotDispersionAngle * player._PlayerAvatar__aimingInfo[2]),
                'autoAim': auto_aim,
                'shotID': shotID,
                'ping': BigWorld.LatencyInfo().value[3] - 0.5 * 0.1,
            }

            print_log('send %s' % json.dumps({
                'dispersion': data['disAngle'],
                'id': data['shotID'],
                'pos': data['gunPos']
            }))

            post_async(config.get('urlSend'), encrypt(json.dumps(data)),
                       lambda res: print_log('server resp: %s' % str(res)))
        else:
            print_log('token is none')


init_mod()
