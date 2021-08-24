# coding=utf-8
import BigWorld
import BattleReplay
from account_shared import readClientServerVersion
from VehicleEffects import DamageFromShotDecoder
from vehicle_systems.tankStructure import TankPartNames
from Math import Matrix, Vector3
from PlayerEvents import g_playerEvents

from events import OnEndLoad, OnShot, OnBattleResult
from battleEventSession import BattleEventSession
from wotHookEvents import wotHookEvents
from ..load_mod import config
from ..utils import print_log, print_debug
from .utils import *


class EventLogger:
    old_event_sessions = {}
    event_session = None  # type: BattleEventSession
    player = None  # type: BigWorld.player()

    temp_shot = OnShot()
    shots = {
        'order': [],
        'shots': dict()
    }

    marker = {
        'serverPos': None,
        'serverDisp': None,
        'clientPos': None,
        'clientDisp': None
    }

    def __init__(self):

        wotHookEvents.add_listener('PlayerAvatar.enableServerAim', self.on_enable_server_aim)

        wotHookEvents.add_listener('PlayerAvatar.onEnterWorld', self.on_enter_world_wot)
        wotHookEvents.add_listener('PlayerAvatar.updateTargetingInfo', self.update_targeting_info)

        wotHookEvents.add_listener('VehicleGunRotator.updateGunMarker', self.update_gun_marker_client)
        wotHookEvents.add_listener('VehicleGunRotator.setShotPosition', self.update_gun_marker_server)

        wotHookEvents.add_listener('PlayerAvatar.shoot', self.shoot)
        wotHookEvents.add_listener('PlayerAvatar.showTracer', self.show_tracer)

        wotHookEvents.add_listener('PlayerAvatar.explodeProjectile', self.explode_projectile)
        wotHookEvents.add_listener('Vehicle.showDamageFromShot', self.show_damage_from_shot)

        wotHookEvents.add_listener('ProjectileMover.killProjectile', self.kill_projectile)

        g_playerEvents.onBattleResultsReceived += self.on_battle_results_received

    def __del__(self):
        wotHookEvents.remove_listener('PlayerAvatar.enableServerAim', self.on_enable_server_aim)
        wotHookEvents.remove_listener('PlayerAvatar.onEnterWorld', self.on_enter_world_wot)
        wotHookEvents.remove_listener('PlayerAvatar.updateTargetingInfo', self.update_targeting_info)
        wotHookEvents.remove_listener('VehicleGunRotator.updateGunMarker', self.update_gun_marker_client)
        wotHookEvents.remove_listener('VehicleGunRotator.setShotPosition', self.update_gun_marker_server)
        wotHookEvents.remove_listener('PlayerAvatar.shoot', self.shoot)
        wotHookEvents.remove_listener('PlayerAvatar.showTracer', self.show_tracer)
        wotHookEvents.remove_listener('PlayerAvatar.explodeProjectile', self.explode_projectile)
        wotHookEvents.remove_listener('Vehicle.showDamageFromShot', self.show_damage_from_shot)
        wotHookEvents.remove_listener('ProjectileMover.killProjectile', self.kill_projectile)
        g_playerEvents.onBattleResultsReceived -= self.on_battle_results_received

    def on_enable_server_aim(self, obj, enable):
        if not enable:
            BigWorld.player().enableServerAim(True)

    def on_enter_world_wot(self, obj, *a):
        print_debug("on_enter_world_wot")
        if self.event_session:
            self.old_event_sessions[self.event_session.arenaID] = self.event_session

        self.event_session = None

    def update_targeting_info(self, obj, turretYaw, gunPitch, maxTurretRotationSpeed, maxGunRotationSpeed,
                              shot_disp_multiplier_factor, *a):
        if self.event_session or BattleReplay.isPlaying():
            return

        print_debug("______INIT______")

        self.player = BigWorld.player()
        player = self.player

        player.enableServerAim(True)

        onEndLoad = OnEndLoad(ArenaTag=player.arena.arenaType.geometry,
                              ArenaID=player.arenaUniqueID,
                              Base=None,
                              PlayerName=player.name,
                              PlayerBDID=player.arena.vehicles[player.playerVehicleID]['accountDBID'],
                              PlayerClan=player.arena.vehicles[player.playerVehicleID]['clanAbbrev'],
                              TankTag=BigWorld.entities[BigWorld.player().playerVehicleID].typeDescriptor.name,
                              TankType=short_tank_type(get_tank_type(player.vehicleTypeDescriptor.type.tags)),
                              TankLevel=player.vehicleTypeDescriptor.level,
                              GunTag=player.vehicleTypeDescriptor.gun.name,
                              StartDis=player.vehicleTypeDescriptor.gun.shotDispersionAngle * shot_disp_multiplier_factor,
                              SpawnPoint=vector(player.getOwnVehiclePosition()),
                              TimerToStart=0,
                              BattleMode=arenaTags[player.arena.bonusType],
                              GameVersion=readClientServerVersion()[1],
                              ModVersion=config.get('version')
                              )
        self.event_session = BattleEventSession(config.get('eventURL'), onEndLoad)

    def update_gun_marker_server(self, obj, vehicleID, shotPos, shotVec, dispersionAngle, *a, **k):
        self.marker['serverPos'] = obj._VehicleGunRotator__getGunMarkerPosition(
            shotPos, shotVec, (dispersionAngle, dispersionAngle))[0]
        self.marker['serverDisp'] = dispersionAngle

    def update_gun_marker_client(self, obj, *a, **k):
        shotPos, shotVec = obj.getCurShotPosition()
        self.marker['clientPos'] = obj._VehicleGunRotator__getGunMarkerPosition(
            shotPos, shotVec, obj._VehicleGunRotator__dispersionAngles)[0]

        self.marker['clientDisp'] = obj._VehicleGunRotator__dispersionAngles[0]

    def shoot(self, obj, isRepeat=False):
        can_shoot, error = obj.guiSessionProvider.shared.ammo.canShoot(isRepeat)
        if not can_shoot:
            return

        self.temp_shot.set_date()
        self.temp_shot.set_server_marker(vector(self.marker['serverPos']), self.marker['serverDisp'])
        self.temp_shot.set_client_marker(vector(self.marker['clientPos']), self.marker['clientDisp'])
        self.temp_shot.set_shoot(gun_position=vector(self.__own_gun_position()),
                                 battle_dispersion=self.player.vehicleTypeDescriptor.gun.shotDispersionAngle,
                                 shot_dispersion=(
                                         self.player.vehicleTypeDescriptor.gun.shotDispersionAngle *
                                         self.player._PlayerAvatar__aimingInfo[2]),
                                 shell_name=self.player.vehicleTypeDescriptor.shot.shell.name,
                                 shell_tag=self.player.vehicleTypeDescriptor.shot.shell.kind,
                                 ping=BigWorld.LatencyInfo().value[3] - 0.5 * 0.1,
                                 auto_aim=(self.player.autoAimVehicle is not None),
                                 server_aim=bool(self.player.gunRotator.settingsCore.getSetting('useServerAim'))
                                 )

    def show_tracer(self, obj, attackerID, shotID, isRicochet, effectsIndex, refStartPoint, refVelocity, gravity, *a):
        if attackerID != self.player.playerVehicleID:
            return

        if effectsIndex not in self.__own_effect_index():
            return

        if isRicochet:
            return

        self.temp_shot.set_tracer(shot_id=shotID, start=vector(refStartPoint), velocity=vector(refVelocity),
                                  gravity=gravity)
        self.shots['order'].append(shotID)
        self.shots['shots'][shotID] = self.temp_shot
        self.temp_shot = OnShot()

    def explode_projectile(self, obj, shotID, effectsIndex, effectMaterialIndex, endPoint, velocityDir,
                           damagedDestructibles):
        if effectsIndex not in self.__own_effect_index():
            return

        if shotID in self.shots['shots']:
            self.shots['shots'][shotID].set_hit(vector(endPoint), 'terrain')

    def show_damage_from_shot(self, obj, attackerID, points, effectsIndex, damageFactor, lastMaterialIsShield):
        if attackerID != self.player.playerVehicleID:
            return

        if effectsIndex not in self.__own_effect_index():
            return

        if len(self.shots['order']) == 0:
            return

        decodedPoints = DamageFromShotDecoder.decodeHitPoints(points, obj.appearance.collisions)
        if not decodedPoints:
            return

        firstHitPoint = decodedPoints[0]
        compMatrix = Matrix(obj.appearance.compoundModel.node(firstHitPoint.componentName))
        firstHitDirLocal = firstHitPoint.matrix.applyToAxis(2)
        firstHitDir = compMatrix.applyVector(firstHitDirLocal)
        firstHitDir.normalise()
        firstHitPos = compMatrix.applyPoint(firstHitPoint.matrix.translation)

        shot = self.shots['shots'][self.shots['order'][0]]
        shot.set_hit(vector(firstHitPos), 'tank')

    def kill_projectile(self, obj, shotID, position, impactVelDir, deathType):
        if abs(shotID) in self.shots['order']:
            print_debug(self.shots)
            self.shots['order'].remove(abs(shotID))
            shot = self.shots['shots'].pop(abs(shotID))  # type: OnShot
            self.event_session.add_event(shot.set_tracer_end(vector(position)))

    # TODO: Декодировать больше результатов
    # TODO: Найти хук который будет работать во время другого боя (получать результат не только непосредственно после завершения игры)
    def on_battle_results_received(self, isPlayerVehicle, results):
        print_debug('battle result received')

        if BattleReplay.isPlaying():
            return
        if not isPlayerVehicle or not results['arenaUniqueID']:
            return

        event_session = None
        if self.event_session.arenaID == results['arenaUniqueID']:
            event_session = self.event_session
        if results['arenaUniqueID'] in self.old_event_sessions:
            event_session = self.old_event_sessions.pop(results['arenaUniqueID'])

        if not event_session:
            return

        print_debug(event_session)
        decodeResult = {}
        try:
            decodeResult['res'] = 'win' if results['personal']['avatar']['team'] == results['common']['winnerTeam'] else 'lose'
            decodeResult['xp']  = results['personal']['avatar']['xp']
            decodeResult['credits']  = results['personal']['avatar']['credits']
            decodeResult['duration'] = results['common']['duration']
            decodeResult['bots_count'] = len(results['common']['bots'])
        except Exception, e:
            print_log('cannot decode battle result\n' + str(e))

        event_session.end_event_session(OnBattleResult(
            RAW=str(results),
            Result=decodeResult.get('res'),
            Credits=decodeResult.get('credits'),
            XP=decodeResult.get('xp'),
            Duration=decodeResult.get('duration'),
            BotsCount=decodeResult.get('bots_count')
        ))

    def __own_effect_index(self):
        return map(lambda t: t.shell.effectsIndex, self.player.vehicleTypeDescriptor.gun.shots)

    def __own_gun_position(self):
        if self.player.vehicle and self.player.vehicle.isStarted and self.player.vehicle.appearance:
            return self.player.vehicle.appearance.compoundModel.node(TankPartNames.GUN).position
        else:
            return self.player.getOwnVehiclePosition() + \
                   self.player.vehicleTypeDescriptor.hull.turretPositions[0] + \
                   self.player.vehicleTypeDescriptor.turret.gunPosition
