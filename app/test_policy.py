import json
# from models import ThingDescription
# from neo4j_service import Neo4jService
# from utils import format_thing_description
from prodict import Prodict
from mongo_service import MongoService

class AttributeDict:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, dict):
                self.__dict__[key] = AttributeDict(**value)
            else:
                self.__dict__[key] = value
    def __getattr__(self, key):
        # First, try to return from _response
        try:
            return self.__dict__['_response'][key]
        except KeyError:
            pass
        except AttributeError:
            pass

def create_policies():
    mongo_service = MongoService()
    policy_1 = {
        "id": "policy_1",
		"description": "the total power of devices connected to the smart plug cannot exceed the rated power of the smart plug, if the work_power of the device is greater than 30",
		"matching_attributes": {
			"source": ["type", "properties.work_power"],
			"target": ["type", "properties.rated_power", "relationship.plug_by"]
		},
		"type": "S2",
		"source": {
			"type": "*"
		},
		"action": "plug_in",
		"relation": "source.actions.connected_to.id == target.id",
		"target": {
			"type": "smart_plug"
		},
        "assertion": "source.properties.work_power.value >= target.properties.rated_power.value - sum([device.properties.work_power.value for device in devices if device.links.connected_to and target.id in device.links.connected_to])",
		"response": "Deny",
		"alert": "The total power of devices connected to the smart plug cannot exceed the rated power of the smart plug"
	}
    policy_2 = {
        "id": "policy_2",
		"description": "cannot open window when the AC is on in the same zone",
		"matching_attributes": {
			"source": ["type", "links.feeds"],
			"target": ["type", "links.feeds", "property.on"]
		},
		"type": "S1",
		"source": {
			"type": "window"
		},
		"action": "open",
		"relation": "set(source.links.feeds) & set(target.links.feeds)",
		"target": {
			"type": "ac"
		},
		"assertion": "target.properties.on.status == True",
		"response": "Double Check",
		"alert": "This rarely happens. Please confirm you want to do it"
	}
    mongo_service.create_policy(policy_1)
    mongo_service.create_policy(policy_2)

def create_things():
    mongo_service = MongoService()
    window = {
        "@context": "https://www.w3.org/2019/wot/td/v1",
        "id": "urn:dev:wot:com:window:1",
        "title": "window",
        "@type": "window",
        "links": {
            "feeds": ["urn:dev:wot:com:noniot:zone:2", "urn:dev:wot:com:noniot:room:1"]
        }
    }
    ac = {
        "context": "https://www.w3.org/2019/wot/td/v1",
        "id": "urn:dev:wot:com:ac:1",
        "title": "ac",
        "@type": "ac",
        "properties": {
            "on": {
                "writable": "true",
                "schema": { "type": "boolean" },
                "status": True
            }
        },
        "links": {
            "feeds": ["urn:dev:wot:com:noniot:room:3", "urn:dev:wot:com:noniot:zone:2"]
        }
    }
    smart_plug = {
        "@context": "https://www.w3.org/2019/wot/td/v1",
        "id": "urn:dev:wot:com:smart_plug:1",
        "title": "smart_plug",
        "@type": "smart_plug",
        "properties": {
            "rated_power": {
                "writable": "true",
                "schema": { "type": "integer" },
                "value": 60
            }
        },
        "links": {
            "feeds": ["urn:dev:wot:com:noniot:zone:2"]
        }
    }
    bulb = {
        "@context": "https://www.w3.org/2019/wot/td/v1",
        "id": "urn:dev:wot:com:bulb:1",
        "title": "bulb",
        "@type": "bulb",
        "properties": {
            "work_power": {
                "writable": "true",
                "schema": { "type": "integer" },
                "value": 20
            }
        },
        "links": {
            "connected_to": ["urn:dev:wot:com:smart_plug:1"]
        }
    }
    router = {
        "@context": "https://www.w3.org/2019/wot/td/v1",
        "id": "urn:dev:wot:com:router:1",
        "title": "router",
        "@type": "router",
        "properties": {
            "work_power": {
                "writable": "true",
                "schema": { "type": "integer" },
                "value": 30
            }
        },
        "links": {
            "connected_to": ["urn:dev:wot:com:smart_plug:1"]
        }
    }
    fan = {
        "@context": "https://www.w3.org/2019/wot/td/v1",
        "id": "urn:dev:wot:com:fan:1",
        "title": "fan",
        "@type": "fan",
        "actions": {
            "connected_to": {
                "id": "urn:dev:wot:com:smart_plug:1"
            }
        },
        "properties": {
            "work_power": {
                "writable": "true",
                "schema": { "type": "integer" },
                "value": 30
            }
        },
        "links": {
            "feeds": ["urn:dev:wot:com:noniot:room:1"]
        }
    }
    mongo_service.create_thing(window)
    mongo_service.create_thing(ac)
    mongo_service.create_thing(smart_plug)
    mongo_service.create_thing(bulb)
    mongo_service.create_thing(router)
    mongo_service.create_thing(fan)
    # neo4j_service = Neo4jService()
    # thing_node = neo4j_service.find_nodes_by_template("ThingDescription", {"thing_id":"urn:dev:wot:com:window:123"})[0]
    # neo4j_service.delete_node(thing_node)

    # thing_node = neo4j_service.find_nodes_by_template("ThingDescription", {"thing_id":"urn:dev:wot:com:ac:123"})[0]
    # neo4j_service.delete_node(thing_node)

    # fmt_td = format_thing_description(window, ["id", "title"])
    # new_td = ThingDescription(thing_id=window["id"], title = window["title"], **fmt_td)
    # new_td.save()

    # fmt_td = format_thing_description(ac, ["id", "title"])
    # new_td = ThingDescription(thing_id=ac["id"], title = ac["title"], **fmt_td)
    # new_td.save()

def check_command(command):
    mongo_service = MongoService()
    criteria = dict()
    criteria["$or"] = [{"source.type":"*"}, {"source.type":command["source"]["type"]}]
    criteria["action"] = command["action"]
    policies = mongo_service.find_policies(criteria)
    # neo4j_service = Neo4jService()
    for policy in policies:
        source_criteria = dict()
        target_criteria = dict()
        source_criteria["id"] = command["source"]["id"]
        target_criteria["@type"] = policy["target"]["type"]
        # target_criteria["type"] = "ac"
        # labels = "ThingDescription"
        # labels["label"] = "ThingDescription"
        sources = mongo_service.find_things(source_criteria)
        targets = mongo_service.find_things(target_criteria)
        things = mongo_service.find_things(None)
        # sources = neo4j_service.run_match(labels=labels, properties=source_criteria)
        # targets = neo4j_service.run_match(labels=labels, properties=target_criteria)
        # things = neo4j_service.run_match(labels=labels)
        # print("++++++++++", sources)
        # print("----------", targets)
        # print("==========", things)
        devices = [AttributeDict(**device) for device in things]
        # devices = [Prodict.from_dict(device) for device in things]
        for source in sources:
            for target in targets:
                source = AttributeDict(**source)
                target = AttributeDict(**target)
                # source = Prodict.from_dict(source)
                # target = Prodict.from_dict(target)
                if eval(policy["relation"]):
                    # print(devices)
                    # print(target.id)
                    # print(source.properties.work_power.value)
                    # d = target.properties.rated_power.value - sum([device.properties.work_power.value for device in devices if device.links.connected_to and device.links.connected_to.id == target.id])
                    # d = target.properties.rated_power.value - sum([device.properties.work_power.value for device in devices if device.links.href == target.id])
                    # print(d)
                    # print(eval("source.properties.work_power.value >= target.properties.rated_power.value - sum([device.properties.work_power.value for device in devices if device.links.href == 'urn:dev:wot:com:smart_plug:1'])"))
                    # print(policy["assertion"])
                    # s = source.properties.work_power.value >= target.properties.rated_power.value - sum([device.properties.work_power.value for device in devices if device.links.href == target.id])
                    # print(s)
                    # for device in devices:
                    #     print(device.links)
                    #     if device.links.connected_to:
                    #         print(device.id)
                    if eval(policy["assertion"], locals()):
                        return policy["response"], policy["alert"]
    return "success", "success"
    

if __name__ == "__main__":
    mongo_service = MongoService()
    mongo_service.drop_collection("policies")
    mongo_service.drop_collection("things")
    create_policies()
    create_things()
    
    command_1 = {
        "source": {
            "type": "window",
            "id": "urn:dev:wot:com:window:1"
        },
        "action": "open"
    }
    response, alert = check_command(command_1)
    print("Response:", response, " Alert:", alert)

    command_2 = {
        "source": {
            "type": "fan",
            "id": "urn:dev:wot:com:fan:1"
        },
        "action": "plug_in",
        "target": {
            "id": "urn:dev:wot:com:smart_plug:1"
        }
    }
    response, alert = check_command(command_2)
    print("Response:", response, " Alert:", alert)





	# {
    #     "id": "policy_1",
	# 	"Description": "the total power of devices connected to the smart plug cannot exceed the rated power of the smart plug, if the work_power of the device is greater than 30",
	# 	"Matching_attributes": {
	# 		"Device_actor": ["type", "property.work_power"],
	# 		"Device_actee": ["type", "property.rated_power", "relationship.plug_by"]
	# 	},
	# 	"Type": "S2",
	# 	"Device_actor": {
	# 		"type": "*",
	# 		"Property.work_power.value": ">30"
	# 	},
	# 	"Action": "plug_in",
	# 	"Relation": "Device_actor.action.connected_to.object.id == Device_actee.id",
	# 	"Device_actee": {
	# 		"type": "smart_plug",
	# 	},
	# 	"Assertion": "Device_actor.property.work_power.value >= Device_actee.property.rated_power.value - {sum (device.property.work_power.value for device in Device_actee.relationship.plug_by)}",
	# 	"Respond": "Deny",
	# 	"Alert": "message respond with the Respond field"
	# }


    # {
    #     "id": "policy_2",
	# 	"description": "cannot open window when the AC is on in the same zone",
	# 	"matching_attributes": {
	# 		"source": ["type", "links.feeds"],
	# 		"target": ["type", "links.feeds", "property.on"]
	# 	},
	# 	"type": "S1",
	# 	"source": {
	# 		"type": "window"
	# 	},
	# 	"action": "open",
	# 	"relation": "source.links.href == target.links.href",
	# 	"target": {
	# 		"type": "ac"
	# 	},
	# 	"assertion": "target.property.on.status == true",
	# 	"response": "Double Check",
	# 	"alert": "This rarely happens. Please confirm you want to do it"
	# }

