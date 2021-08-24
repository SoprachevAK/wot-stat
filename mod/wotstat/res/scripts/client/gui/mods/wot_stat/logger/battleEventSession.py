import json
import BigWorld

from events import Event, OnEndLoad, OnBattleResult
from ..common.asyncResponse import post_async
from ..common.cryptoPlaceholder import encrypt
from ..utils import print_log


class BattleEventSession:
    send_queue = []
    token = None
    eventURL = ''
    send_interval = 5
    arenaID = None
    enable = True

    def __init__(self, event_URL, on_end_load_event, sendInterval=5):
        # type: (str, OnEndLoad, float) -> None

        self.eventURL = event_URL
        self.send_interval = sendInterval
        self.arenaID = on_end_load_event.ArenaID

        self.__post_events([on_end_load_event], self.__init_send_callback)

    def add_event(self, event):
        # type: (Event) -> None
        self.send_queue.append(event)

    def end_event_session(self, battle_result_event):
        # type: (OnBattleResult) -> None
        self.add_event(battle_result_event)
        self.enable = False


    def __init_send_callback(self, res):
        # type: (str) -> None
        self.token = res
        print_log('setToken: ' + str(res))
        self.__send_event_loop()

    def __send_event_loop(self):
        for event in self.send_queue:
            event.Token = self.token
        self.__post_events(self.send_queue)

        self.send_queue = []

        if self.enable:
            BigWorld.callback(self.send_interval, self.__send_event_loop)

    def __post_events(self, events, callback = None):
        if events and len(events) > 0:
            data = {
                'events': map(lambda t: t.get_dict(), events)
            }
            post_async(self.eventURL, encrypt(json.dumps(data)), callback)
            print_log(json.dumps(data))
