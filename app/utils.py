import flask
import json
from flask import current_app as app
from collections import defaultdict

def is_json_request(request: flask.Request, properties: list = []) -> bool:
    """Check whether the request's body could be parsed to JSON format, and all necessary properties specified by `properties` are in the JSON object
    Args:
        request (flask.Request): the flask request object wrapping the real HTTP request data
        properties (list[str]): list of property names to check. By default its an empty list
    Returns:
        boolean: whether the request is a JSON-content request and contains all the properties
    """
    try:
        body = request.get_json()
    except TypeError:
        return False
    if body is None:
        return False
    for prop in properties:
        if prop not in body:
            return False
    return True

def format_thing_description(thing_desp, pops=[]):
    fmt_td = {k:json.dumps(v) for k,v in thing_desp.items()}
    for item in pops:
        if item in fmt_td:
            fmt_td.pop(item) 
    print(fmt_td)
    return fmt_td

def transform_links(things):
    things = list(things)
    for thing in things:
        links = thing["links"]
        new_links = defaultdict(list)
        for link in links:
            print("=====", link)
            rel = link["rel"]
            id = link["href"]
            new_links[rel].append(id)
        thing["links"] = new_links
    return things
