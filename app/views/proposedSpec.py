import json
from typing import Dict, List, Callable, Any, Tuple, Union
from datetime import datetime
from enum import IntEnum
import pickle


class DeviceDetails:
    def __init__(self, type: str, matchingAttribute: Dict[str, str]):
        self.type = type
        self.matchingAttribute = matchingAttribute

    @staticmethod
    def from_dict(rawDict):

        if rawDict is None:
            return None

        type = rawDict.get("type", "")
        if "type" in rawDict:
            rawDict.pop("type")

        return DeviceDetails(type=type, matchingAttribute=rawDict)

    def to_dict(self):
        return {
            "type": self.type,
            "matchingAttribute": self.matchingAttribute
        }


class ResponseType(IntEnum):
    DoubleCheck = 1
    Approve = 2
    Deny = 3


class PriorityType(IntEnum):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9


class Policy:
    def __init__(self, id: str, description: str,
                 objectDevice: DeviceDetails, relationship: Callable, action: str, response: ResponseType,
                 expiration: str = datetime.max.strftime("%m/%d/%Y"), alert: str = "",
                 priority: PriorityType = PriorityType.SIX, type: str = "", subjectDevice: DeviceDetails = None,
                 assertion: Callable = None, affectedDevice: Dict[str, DeviceDetails] = None):
        self.id = id
        self.description = description
        self.type = type
        self.subjectDevice = subjectDevice
        self.objectDevice = objectDevice
        self.affectedDevice = affectedDevice
        self.relationship = relationship
        self.assertion = assertion
        self.action = action
        self.response = response
        self.expiration = expiration
        self.alert = alert
        self.priority = priority

    def to_dict(self):

        dict_object = {}

        dict_object["id"] = self.id
        dict_object["description"] = self.description
        dict_object["action"] = self.action
        dict_object["objectDevice"] = self.objectDevice.to_dict()
        if self.affectedDevice is not None:
            dict_object["affectedDevice"] = {key: self.affectedDevice[key].to_dict() for key in self.affectedDevice}
        dict_object["relationship"] = pickle.dumps(self.relationship)
        dict_object["expiration"] = self.expiration
        dict_object["alert"] = self.alert
        dict_object["priority"] = self.priority.value
        dict_object["response"] = self.response.value
        if self.subjectDevice is not None:
            dict_object["subjectDevice"] = self.subjectDevice.to_dict()
        if self.assertion is not None:
            dict_object["assertion"] = pickle.dumps(self.assertion)

        return dict_object

    @staticmethod
    def from_dict(rawDict):
        """
        Converts the dictionary of values into a class.
        """
        print(rawDict)
        # Check if the required fields are present or not
        requiredfields = ["id", "description", "action", "objectDevice", "relationship", "response"]

        if len(set(requiredfields) - set(list(rawDict.keys()))) != 0:
            raise Exception("Required Fields not available for creating a Policy")

        relationship_callable = pickle.loads(rawDict["relationship"])

        assertion_callable = None
        if "assertion" in rawDict:
            assertion_callable = pickle.loads(rawDict["assertion"])

        priority_val = PriorityType.SIX
        if "priority" in rawDict:
            priority_val = PriorityType(rawDict["priority"])

        affected_device = None
        if "affectedDevice" in rawDict:
            affected_device = {key: DeviceDetails.from_dict(rawDict["affectedDevice"][key]) for key in
                              rawDict["affectedDevice"]}

        return Policy(id=rawDict["id"], description=rawDict["description"], action=rawDict["action"],
                      objectDevice=DeviceDetails.from_dict(rawDict["objectDevice"]),
                      affectedDevice=affected_device,
                      relationship=relationship_callable, response=ResponseType(rawDict["response"]),
                      expiration=rawDict.get("expiration", datetime.max.strftime("%m/%d/%Y")),
                      alert=rawDict.get("alert", ""),
                      priority=priority_val, type=rawDict.get("type", ""),
                      subjectDevice=DeviceDetails.from_dict(rawDict.get("subjectDevice", None)),
                      assertion=assertion_callable)

