import logging
import traceback
from flask import request
from flask_restful import Resource

from .templates.Volumes import get_volume_instance
from .templates.VolumeCollection import get_volume_collection_instance

INTERNAL_ERROR = 500

members = []

class VolumeCollectionAPI(Resource):
    def __init__(self, **kwargs):
        self.rb = kwargs.get('rb', '')
        logging.info('VolumeCollectionAPI initialized')

    def get(self, ident1, ident2):
        try:
           
            data = get_volume_collection_instance(
                wildcards={"rb": self.rb, "system_id":ident1, "storage_id": "Storage-1"}, 
                volume_ids=members
            )
            return data, 200
        except Exception:
            traceback.print_exc()
            return {"error": "Internal server error"}, INTERNAL_ERROR
    def post(self, ident1, ident2):

        logging.info('ComputerSystemAPI POST called')
        try:
            global config
            global wildcards
            
            members[ident1][ident2]=config
            resp = config, 201
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp   

        
class VolumeAPI(Resource):
    def __init__(self, **kwargs):
        self.rb = kwargs.get('rb', '')
        logging.info('VolumeAPI initialized')
    def get(self, ident1, ident2, ident3):
        try:
            global member_data
    
        except Exception:
            traceback.print_exc()
            return {"error": "Internal server error"}, INTERNAL_ERROR