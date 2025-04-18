# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# Manager API File

"""
Collection API:  GET, POST
Singleton  API:  GET, POST, PATCH, DELETE
"""

import g

import sys, traceback
import logging
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

# Resource and SubResource imports
from .templates.Manager import get_Manager_instance

members = {}

INTERNAL_ERROR = 500


# Manager Singleton API
class ManagerAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('ManagerAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident):
        logging.info('ManagerAPI GET called')
        try:
            # Find the entry with the correct value for Id
            resp = 404
            if ident in members:
                resp = members[ident], 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self, ident):
        logging.info('ManagerAPI PUT called')
        return 'PUT is not a supported command for ManagerAPI', 405

    # HTTP POST
    # This is an emulator-only POST command that creates new resource
    # instances from a predefined template. The new instance is given
    # the identifier "ident", which is taken from the end of the URL.
    # PATCH commands can then be used to update the new instance.
    def post(self, ident):
        logging.info('ManagerAPI POST called')
        try:
            global wildcards
            wildcards['id'] = ident
            wildcards['linkSystem'] = ['UpdateWithPATCH']
            wildcards['linkChassis'] = ['UpdateWithPATCH']
            wildcards['linkInChassis'] = ['UpdateWithPATCH']
            config = get_Manager_instance(wildcards)
            members[ident] = config
            resp = config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident):
        logging.info('ManagerAPI PATCH called')
        raw_dict = request.get_json(force=True)
        try:
            # Update specific portions of the identified object
            for key, value in raw_dict.items():
                members[ident][key] = value
            resp = members[ident], 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP DELETE
    def delete(self, ident):
        logging.info('ManagerAPI DELETE called')
        try:
            # Find the entry with the correct value for Id
            resp = 404
            if ident in members:
                del(members[ident])
                resp = 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp


# Manager Collection API
class ManagerCollectionAPI(Resource):

    def __init__(self):
        logging.info('ManagerCollectionAPI init called')
        self.rb = g.rest_base
        self.config = {
            '@odata.context': self.rb + '$metadata#ManagerCollection.ManagerCollection',
            '@odata.id': self.rb + 'Managers',
            '@odata.type': '#ManagerCollection.ManagerCollection',
            'Name': 'Manager Collection',
            'Links': {}
        }
        self.config['Links']['Members@odata.count'] = len(members)
        self.config['Links']['Members'] = [{'@odata.id':x['@odata.id']} for
                x in list(members.values())]

    # HTTP GET
    def get(self):
        logging.info('ManagerCollectionAPI GET called')
        try:
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self):
        logging.info('ManagerCollectionAPI PUT called')
        return 'PUT is not a supported command for ManagerCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    # POST should allow adding multiple instances to a collection.
    # For now, this only adds one instance.
    # TODO: 'id' should be obtained from the request data.
    def post(self):
        logging.info('ManagerCollectionAPI POST called')
        return 'POST is not a supported command for ManagerCollectionAPI', 405
        try:
            config = request.get_json(force=True)
            ok, msg = self.verify(config)
            if ok:
                members[config['id']] = config
                resp = config, 201
            else:
                resp = msg, 400
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PATCH
    def patch(self):
        logging.info('ManagerCollectionAPI PATCH called')
        return 'PATCH is not a supported command for ManagerCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('ManagerCollectionAPI DELETE called')
        return 'DELETE is not a supported command for ManagerCollectionAPI', 405


# CreateManager
#
# Called internally to create instances of a resource. If the
# resource has subordinate resources, those subordinate resource(s)
# are created automatically.
#
# Note: In 'init', the first time through, kwargs may not have any
# values, so we need to check. The call to 'init' stores the path
# wildcards. The wildcards are used to modify the resource template
# when subsequent calls are made to instantiate resources.
class CreateManager(Resource):

    def __init__(self, **kwargs):
        logging.info('CreateManager init called')
        if 'resource_class_kwargs' in kwargs:
            global wildcards
            wildcards = copy.deepcopy(kwargs['resource_class_kwargs'])

    # Create instance
    def put(self, ident):
        logging.info('CreateManager put called')
        try:
            global config
            global wildcards
            wildcards['id'] = ident
            config = get_Manager_instance(wildcards)
            members[ident] = config
            resp = config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        logging.info('CreateManager init exit')
        return resp

class ManagerResetAPI(Resource):
    def __init__(self, **kwargs):
        logging.info('ManagerResetAPI init called')
        global wildcards  
        wildcards = kwargs  

    def post(self, ident):
        logging.info(f'ManagerResetAPI POST called for {ident}')
        
        try:
            global wildcards 
            if ident not in members:
                logging.error(f"Manager {ident} not found in members.")
                return {"error": f"Manager {ident} not found"}, 404

            req = request.get_json()
            if not req or "ResetType" not in req:
                return {"error": "Missing ResetType"}, 400

            wildcards['sys_id'] = ident
            wildcards['rb'] = "/redfish/v1/"
            valid_reset_types = ["ForceRestart", "GracefulRestart"]

            reset_type = req["ResetType"]
            if reset_type not in valid_reset_types:
                return {"error": f"Invalid ResetType: {reset_type}"}, 400

            from time import sleep
            if "Status" not in members[ident]:
                members[ident]["Status"] = {}
            if "State" not in members[ident]["Status"]:
                logging.warning(f"'Status' key missing in {ident}, initializing it.")
                members[ident]["Status"]["State"] = "Unknown"

            current_state = members[ident]["Status"]["State"]
            if current_state == "Disabled":
                members[ident]["Status"]["State"] = "Enabled"
                logging.info(f"{ident} enabled")
            if reset_type=="ForceRestart":
                members[ident]["Status"]["State"] = "Disabled"
                logging.info(f"{ident} Restart pending")
                sleep(2)
                members[ident]["Status"]["State"] = "Enabled"
                logging.info(f"{ident} powered back On after Restart.")
            else:
                logging.info("Shutting down all processes")
                sleep(2)
                members[ident]["Status"]["State"] = "Disabled"
                logging.info(f"{ident} Restart pending")
                sleep(2)
                members[ident]["Status"]["State"] = "Enabled"
                logging.info(f"{ident} powered back On after Restart.")
            response = {
                "Id": ident,
                "ResetType": reset_type,
                "Status": members[ident]["Status"],
                "Message": f"Manager {ident} reset successfully using {reset_type}"
            }

            return response, 200

        except Exception as e:
            logging.error(f"Error in Reset API: {e}")
            traceback.print_exc()
            return {"error": "Internal Server Error"}, INTERNAL_ERROR

