# Enables you to create alarms which occur once every <x> minutes
# PREAMBLE ####################################################################
import asyncio
import datetime

# Keys: channel. Value: list of tuples (Alarm datetime, Alarm object)
alarms = []

async def _check_alarm(client):
    """Called by the main task in order to check for a triggering alarm"""
    await client.wait_until_ready()
    while not client.is_closed:
        time = datetime.datetime.now()
        while len(alarms) > 0 and time >= alarms[0][0]:
            await alarms[0][1].run()
            alarms.pop(0)
        await asyncio.sleep(1) # only check once per second

def _insert_alarm(trigger_time, alarm):
    """Set an alarm to trigger at the given time"""
    if len(alarms) == 0:
        alarms.append((trigger_time, alarm))
    success = False
    for i in range(0, len(alarms)):
        if trigger_time <= alarms[i][0]:
            alarms.insert(i, (trigger_time, alarm))
            success = True
            break
    if not success:
        alarms.append((trigger_time, alarm))

class Alarm:
    """Abstract class for alarms"""
    def __init__(self):
        self.next = ""

    def attach(self, seconds):
        """Attach this listener to repeat at the given time"""
        if self.next != "":
            self.detach()
        self.next = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        _insert_alarm(self.next, self)

    def detach(self):
        """Detach this listener from timer queue"""
        alarms.remove((self.next, self))

    async def run(self):
        """Abstract function for things that should be run when this activates"""
        pass
