import logging
import traceback
from flask import request
from flask_restful import Resource

import uuid
from .Drive_api import Drive_API, drive_config
from .templates.Volumes import get_volume_instance
from .templates.VolumeCollection import get_volume_collection_instance

INTERNAL_ERROR = 500

volume_members = {}
volume_data = {}
class VolumeCollectionAPI(Resource):
    def __init__(self, **kwargs):
        self.rb = kwargs.get('rb', '')
        logging.info('VolumeCollectionAPI initialized')

    def get(self, ident1, ident2):
        try:

            data = get_volume_collection_instance(
                wildcards={"rb": self.rb, "system_id":ident1, "storage_id": "Storage-1"}, 
                volume_ids=[]
            )
            if ident1 not in volume_members:
                volume_members[ident1] = {}
                if ident2 not in volume_members[ident1]:
                    volume_members[ident1][ident2] = {}
            if len(volume_members[ident1][ident2])>0:
                vids = []
                for vid in volume_members[ident1][ident2]:
                    vids.append(vid)
                data = get_volume_collection_instance(
                wildcards={"rb": self.rb, "system_id":ident1, "storage_id": "Storage-1"}, 
                volume_ids=vids
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
            config = {}
            if ident1 not in volume_members:
                volume_members[ident1] = {}
                if ident2 not in volume_members:
                    volume_members[ident1][ident2] = {}
            volume_id = len(volume_members[ident1][ident2])+1
            req = request.json
            links= req['Links']['Drives']
            
            # Generate UUID type 4
            volume_uuid = str(uuid.uuid4())
            # Calculate min capacity bytes for raid 0 and raid 1 validation
            min_capacity_bytes=float('inf')
            for link in links:
                drive_id = link["@odata.id"].split('/')[-1]
                chassis_id = link["@odata.id"].split('/')[-3]
                drive_api = Drive_API(rb="/redfish/v1")
                response, status = drive_api.get(chassis_id, drive_id)
                if min_capacity_bytes>drive_config[drive_id]['CapacityBytes']:
                 min_capacity_bytes = drive_config[drive_id]['CapacityBytes']
            
            # RAID Drive links validation 
            if req['RAIDType'] == "RAID0":
                if len(links)<2:
                    return {"error":"Cannot create RAID0 volume with the drive. Minimum of 2 drive links is required for RAID0 volume."}, 400
                if req['CapacityBytes']>len(links)*min_capacity_bytes:
                    return {"error":f"Capacity of bytes exceeded for RAID0. Maximum capacity is {len(links)*min_capacity_bytes}"}, 400
            elif req['RAIDType'] == "RAID1":
                if len(links)<2:
                    return {"error":"Cannot create RAID1 volume with the drive. Minimum of 2 drive links is required for RAID1 volume."}, 400
                if min_capacity_bytes<req['CapacityBytes']:
                    return {"error":f"Capacity of bytes exceeded for RAID1. Maximum capacity is {min_capacity_bytes}"}, 400
            
            drive_links = []
            for link in links:
                drive_id = link["@odata.id"].split('/')[-1]
                chassis_id = link["@odata.id"].split('/')[-3]
                drive_api = Drive_API(rb="/redfish/v1")
                response, status = drive_api.get(chassis_id, drive_id)
                drive_links.append(link['@odata.id'])
                if not response["Links"]["Volumes"]:
                    drive_config[drive_id]["Links"]["Volumes"] = {"@odata.id":self.rb+"Systems/"+ident1+"/Storage/"+ident2+"/Volumes/"+"Volume-"+str(volume_id)}
                else:
                    return {"error":"Cannot create volume with the drive. Drive is already attached to another volume."}, 400
            
            vid = "Volume-"+str(volume_id)
            config = get_volume_instance(wildcards={"rb": self.rb, "system_id":ident1, "storage_id":ident2, "volume_id":volume_id, "durable_name":volume_uuid}, drive_ids=drive_links, raid_type=req['RAIDType'], capacity_bytes=req['CapacityBytes'])
            volume_members[ident1][ident2][vid]=config
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
            global config
            global wildcards
            durable_name = volume_members[ident1][ident2][ident3]['Identifiers'][0]['DurableName']
            drive_ids = []
            for id in volume_members[ident1][ident2][ident3]['Links']['Drives']:
                drive_ids.append(id['@odata.id'])
            capacity_bytes = volume_members[ident1][ident2][ident3]['CapacityBytes']
            raid_type = volume_members[ident1][ident2][ident3]['RAIDType']
            config = get_volume_instance({'rb':self.rb, 'system_id':ident1, 'storage_id':ident2, 'volume_id':ident3, 'durable_name':durable_name}, drive_ids=drive_ids, raid_type=raid_type, capacity_bytes=capacity_bytes)
            return config, 200
        except Exception:
            traceback.print_exc()
            return {"error": "Internal server error"}, INTERNAL_ERROR
    
    def delete(self, ident1, ident2, ident3):
        try:
            if ident1 in volume_members and ident2 in volume_members[ident1] and ident3 in volume_members[ident1][ident2]:
                volume_data = volume_members[ident1][ident2][ident3]
                drive_links = volume_data["Links"]["Drives"]
            
                for link in drive_links:
                    drive_id = link["@odata.id"].split("/")[-1]
                    if drive_id in drive_config:
                        if "Links" in drive_config[drive_id] and "Volumes" in drive_config[drive_id]["Links"]:
                            del drive_config[drive_id]["Links"]["Volumes"]

                del volume_members[ident1][ident2][ident3]

                return {"message": f"Volume {ident3} deleted successfully."}, 204
            else:
                return {"error": "Volume not found."}, 404
        except Exception:
            traceback.print_exc()
            return {"error": "Internal server error"}, INTERNAL_ERROR
