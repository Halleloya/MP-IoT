from datetime import datetime # Don't Change this imports
from views.proposedSpec import Policy, DeviceDetails, PriorityType, ResponseType  # Don't Change this imports
from views.policy_api import AttributeDict

def relationship(subjectDevice: AttributeDict, objectDevice: AttributeDict, affectedDevice: AttributeDict, devices: AttributeDict, command: dict) -> bool:
    # TODO: Define the relationship function
    return objectDevice.actions.connected_to.id == affectedDevice.id

def assertion(subjectDevice: AttributeDict, objectDevice: AttributeDict, affectedDevice: AttributeDict, devices: AttributeDict, command: dict) -> bool:
    # TODO: Define the relationship function
    try:
        return objectDevice.properties.work_power.value >= affectedDevice.properties.rated_power.value - sum([device.properties.work_power.value for device in devices if device.links.connected_to and affectedDevice.id in device.links.connected_to])
    except:
        return False
    
policy = Policy(id="001-123-policy_1", description="Deny: the total power of devices connected to the smart plug exceed the rated power of the smart plug.",
                objectDevice=DeviceDetails("*", {}),
                affectedDevice={"smart_plug": DeviceDetails("smart_plug", {})},
                relationship=relationship, action="plug_in", response=ResponseType.Deny,
                alert="The total power of devices connected to the smart plug cannot exceed the rated power of the smart plug",
                expiration=datetime.max.strftime("%m/%d/%Y"), priority=PriorityType.TWO, type="S1", subjectDevice=None,
                assertion=assertion) # TODO: Instantiate the policy object 
