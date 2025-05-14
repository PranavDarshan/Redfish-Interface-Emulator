import g
import sys, traceback
import logging
import copy
from flask import Flask, request, make_response
from flask_restful import reqparse, Api, Resource
from .templates.Drive import get_Drive_instance
drives_config={}
INTERNAL_ERROR=500
class Drive_API(Resource):
    def __init__(self, **kwargs):
        logging.info('DrivesAPI init called')
        self.rb = kwargs.get('rb', '')
    
    
    def get(self,ident,ident1):
        logging.info(f'DrivesAPI GET called')
        try:
            global drive_config
            drive_config=get_Drive_instance({'rb': self.rb, 'ch_id': ident,'dr_id':ident1})  
            return drive_config, 200
        except Exception:
            traceback.print_exc()
            return INTERNAL_ERROR
    
    def post(self):
        return 'POST NOT SUPPORTED FOR DRIVES COLLECTION',405
    
    def patch(self):
        return 'PATCH NOT SUPPORTED FOR DRIVES COLLECTION',405

class CreateDrive(Resource):

    def __init__(self, **kwargs):
        logging.info('CreateDrive init called')
        if 'resource_class_kwargs' in kwargs:
            global wildcards
            wildcards = copy.deepcopy(kwargs['resource_class_kwargs'])

    def put(self):
        logging.info('CreateDrives put called')
        try:
            global config
            global wildcards
            config = get_Drive_instance(wildcards)
            resp = config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR  
        logging.info('CreateDrive init exit')
        return resp

    