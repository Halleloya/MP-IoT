from datetime import datetime
from views.proposedSpec import Policy, DeviceDetails, PriorityType, ResponseType


def relation(objectDevice, affectedDevice):
    try:
        return set(objectDevice["links"]["feeds"]) & set(affectedDevice["links"]["feeds"])
    except:
        return False


def assertion(objectDevice, affectedDevice):
    try:
        return affectedDevice["properties"]["high_power"]["status"]
    except:
        return False


policy = Policy(id="001-234", description="Double Check: turn on heater when AC is on for the same zone",
                objectDevice=DeviceDetails("heater", {"type": "wot.type", "feeds": "brick.links.feeds"}),
                affectedDevice={"ac": DeviceDetails("ac", {"type": "wot.type", "feeds": "brick.links.feeds",
                                                           "on": "wot.property.on.status"})},
                relationship=relation, action="turn on", response=ResponseType.DoubleCheck,
                alert="Your AC is currently on. Please confirm you want to turn on the heater",
                expiration=datetime.max.strftime("%m/%d/%Y"), priority=PriorityType.TWO, type="S1", subjectDevice=None,
                assertion=assertion)
