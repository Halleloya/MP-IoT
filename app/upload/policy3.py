from datetime import datetime # Don't Change this imports
from views.proposedSpec import Policy, DeviceDetails, PriorityType, ResponseType  # Don't Change this imports
from views.policy_api import AttributeDict # Don't Change this imports

def relationship(subjectDevice: AttributeDict, objectDevice: AttributeDict, affectedDevice: AttributeDict, devices: AttributeDict, command: dict) -> bool:
    # TODO: Define the relationship function
    return True

def assertion(subjectDevice: AttributeDict, objectDevice: AttributeDict, affectedDevice: AttributeDict, devices: AttributeDict, command: dict) -> bool:
    # TODO: Define the relationship function
    try:
        return objectDevice.properties.energy_saving.status == True and int(command["action"]["temperature"]) < objectDevice.properties.energy_saving.lower_temperature_limit
    except:
        return False
    
policy = policy = Policy(id="001-234", description="Double Check: trying to set temperature of AC below 65°F when AC is on energy saving mode.",
                objectDevice=DeviceDetails("ac", {"type": "ac", "feeds": "brick.links.feeds"}),
                relationship=relationship, action="set", response=ResponseType.DoubleCheck,
                alert="You are trying to set the temperature of AC below 65°F while the AC is on energy saving mode",
                expiration=datetime.max.strftime("%m/%d/%Y"), priority=PriorityType.TWO, type="S1", subjectDevice=None,
                assertion=assertion) # TODO: Instantiate the policy object 
