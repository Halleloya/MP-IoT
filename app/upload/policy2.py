from datetime import datetime # Don't Change this imports
from views.proposedSpec import Policy, DeviceDetails, PriorityType, ResponseType  # Don't Change this imports
from views.policy_api import AttributeDict

def relationship(subjectDevice: AttributeDict, objectDevice: AttributeDict, affectedDevice: AttributeDict, devices: AttributeDict, command: dict) -> bool:
    # TODO: Define the relationship function
    return set(objectDevice.links.feeds) & set(affectedDevice.links.feeds)

def assertion(subjectDevice: AttributeDict, objectDevice: AttributeDict, affectedDevice: AttributeDict, devices: AttributeDict, command: dict) -> bool:
    # TODO: Define the relationship function
    try:
        return affectedDevice.properties.on.status == True
    except:
        return False
    
policy = Policy(id="001-1256-policy_2", description="Double Check: turning on Heater when the AC is on in the same zone.",
                objectDevice=DeviceDetails("heater", {}),
                affectedDevice={"ac": DeviceDetails("ac", {"type":"ac"})},
                relationship=relationship, action="on", response=ResponseType.DoubleCheck,
                alert="You are trying to switch on a heater while the AC is running in the same Zone.",
                expiration=datetime.max.strftime("%m/%d/%Y"), priority=PriorityType.TWO, type="S1", subjectDevice=None,
                assertion=assertion) # TODO: Instantiate the policy object 


