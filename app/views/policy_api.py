import ast
import datetime
from cProfile import label
import json
from logging import Logger, error
from operator import ne
from flask import Blueprint, config, request, url_for, redirect, Response, make_response, jsonify, session, \
    render_template
from flask import current_app as app
from flask_login import current_user as user
from mongo_service import MongoService
from utils import is_json_request, format_thing_description, transform_links
from views import proposedSpec
from importlib import import_module
import os
from werkzeug.utils import secure_filename

policy_api = Blueprint('policy_api', __name__)
ERROR_JSON = {"error": "Invalid request."}
WARNING_JSON = {"error": "Invalid request."}
INVALID_FILE = {"error": "Invalid file Selected"}
INVALID_POLICY_OBJECT = {"error": "Invalid Policy Object"}
INVALID_FILE_NAME = {"error": "A policy with the same fileName exists"}


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


@policy_api.route('/register2', methods=['POST'])
def register2():
    """Register thing description at the target location. 
    If the current directory is the target location specified by `location` argument, the operation is processed locally
    
    Args:
        All of the following arguments are required and passed in the request URL.
        td (JSON str): the information of the thing description to be registered in JSON format
    Returns:
        HTTP Response: if the register is completed, a simple success string with HTTP status code 200 is returned
            Otherwise a reason is returned in the response and HTTP status code is set to 400
    """
    if not is_json_request(request, ["td"]):
        return jsonify(ERROR_JSON), 400

    body = request.get_json()
    thing_description = body["td"]
    mongo_service = MongoService()
    mongo_service.create_thing(thing_description)

    return make_response("Created", 200)


@policy_api.route('/delete2', methods=['POST', 'DELETE'])
@policy_api.route('/delete2/<thing_id>', methods=['POST', 'DELETE'])
def delete2(thing_id):
    """
        Deletes a thing
    """
    mongo_service = MongoService()
    mongo_service.delete_thing(thing_id)
    return make_response("Deleted", 200)


@policy_api.route('/policy/v2', methods=['POST'])
def policyV2():
    if 'file' not in request.files:
        return jsonify(ERROR_JSON), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify(INVALID_FILE), 400
    if not file.filename.endswith('.py'):
        return jsonify(INVALID_FILE), 400

    filename = secure_filename(file.filename)
    print(filename)
    # if same filename already exists in the uploads folder
    if os.path.isfile(app.config['UPLOAD_FOLDER'] + '/' + filename):
        return jsonify(INVALID_FILE_NAME), 400

    # Saving the files to the folder
    file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))

    module = import_module(app.config['UPLOAD_FOLDER'] + "." + filename.split('.')[0])

    policy_object = getattr(module, "policy")

    print(policy_object)

    mongo_service = MongoService()
    print(policy_object.to_dict())

    mongo_service.create_policy(policy_object.to_dict())

    return make_response("Created", 200)


@policy_api.route('/policy/v2/<id>', methods=['GET'])
def getPolicyV2(id):
    mongo_service = MongoService()
    criteria = {}
    criteria["id"] = id
    policies = mongo_service.find_policies(criteria)
    res = []
    for policyItem in policies:
        print(policyItem)
        res.append(proposedSpec.Policy.from_dict(policyItem))

    return json.dumps(res[0].to_dict())


@policy_api.route('/policy', methods=['POST'])
def policy():
    if not is_json_request(request, ["td"]):
        return jsonify(ERROR_JSON), 400

    body = request.get_json()
    policy = body["td"]

    mongo_service = MongoService()
    mongo_service.create_policy(policy)

    return make_response("Created", 200)


@policy_api.route('/command', methods=['POST'])
def command():
    if not is_json_request(request, ["td"]):
        return jsonify(ERROR_JSON), 400

    body = request.get_json()
    command = body["td"]
    mongo_service = MongoService()

    criteria = dict()
    or_criteria = ["*", command["objectDevice"]["type"]]
    criteria["$or"] = [{"@type": {"$in": or_criteria}}, {"action": command["action"]["type"]}]

    # Fetching Policy by Action and object device type
    policies = mongo_service.find_policies(criteria)

    # Converting fetched Policy into Policy Object
    policies = [proposedSpec.Policy.from_dict(policy) for policy in policies]

    for policy in policies:

        # Checking if the policy is valid
        if datetime.datetime.utcnow() > datetime.datetime.strptime(policy.expiration,"%m/%d/%Y"):
            # Policy Invalid Skip it
            continue

        # Fetching object Devices based on certain criteria
        object_device_criteria = dict()
        object_device_criteria["id"] = command["objectDevice"]["id"]
        object_devices = transform_links(mongo_service.find_things(object_device_criteria))

        # Fetching affected devices based on certain criteria
        affected_device_criteria = dict()
        or_criteria = ["*"]

        if policy.affectedDevice is not None:
            for key in policy.affectedDevice:
                affected_device = policy.affectedDevice[key]
                if affected_device.type != "":
                    or_criteria.append(affected_device.type)

        affected_device_criteria["$or"] = [{"@type": {"$in": or_criteria}}]
        affected_devices = transform_links(mongo_service.find_things(affected_device_criteria))

        # Fetching Subject Device based on certain criteria
        subject_device_criteria = {}
        if "subjectDevice" in command:
            subject_device_criteria["@type"] = command["subjectDevice"]["id"]
        else:
            subject_device_criteria["@type"] = "smartphone"  # defaults to smartphone

        subject_devices = transform_links(mongo_service.find_things(subject_device_criteria))

        # Fetching the entire device list
        things = transform_links(mongo_service.find_things(None))
        devices = [AttributeDict(**device) for device in things]

        if not len(object_devices):
            object_devices = [None]

        if not len(affected_devices):
            affected_devices = [None]

        for subject_device in subject_devices:
            for object_device in object_devices:
                for affected_device in affected_devices:
                    subject_device_detail, object_device_detail, affected_device_detail = None, None, None
                    if object_device is not None:
                        object_device_detail = AttributeDict(**object_device)
                    if affected_device is not None:
                        affected_device_detail = AttributeDict(**affected_device)
                    if subject_device is not None:
                        subject_device_detail = AttributeDict(**subject_device)

                    if policy.relationship(subject_device_detail, object_device_detail, affected_device_detail,
                                           devices, command):
                        print("Relationship evaluation successful for the subject, object and affected device tuple.")
                        if (policy.assertion is not None and
                                policy.assertion(subject_device_detail, object_device_detail, affected_device_detail,
                                                 devices, command)):
                            print("Assertion evaluation successful for the subject, object and affected device tuple.")
                            error = ERROR_JSON
                            error["error"] = policy.response.name
                            error["message"] = policy.alert
                            return jsonify(error), 400
    return make_response("Success", 200)
