from flask import request, jsonify, make_response
from flask_restful import Resource
import logging

# Import utility functions
from api_emulator.utils import replace_recurse
from api_emulator.redfish.templates.Bios import get_Bios_instance
members = {}
class BiosAPI(Resource):

    def __init__(self, **kwargs):
        """Initialize with configuration parameters."""
        self.wildcards = kwargs.get("wildcards", {})
        logging.info("BiosAPI initialized with wildcards: %s", self.wildcards)

    def get(self, ident):  # Ensure Flask-RESTful passes 'ident' correctly
        """Handles GET requests for BIOS settings."""
        logging.info(f"GET request received for BIOS: {ident}")
        
        try:
            wildcards = {
                "rb": "/redfish/v1/",
                "id": ident
            }
            bios_data = get_Bios_instance(wildcards)
            return make_response(jsonify(bios_data), 200)

        except Exception as e:
            logging.error(f"Error fetching BIOS settings: {str(e)}")
            return make_response(jsonify({"error": "Internal Server Error"}), 500)

    def put(self, ident):  # Ensure Flask-RESTful passes 'ident' correctly
        """Handles PUT requests to update BIOS settings."""
        logging.info(f"PUT request received for BIOS: {ident}")

        try:
            # Get JSON payload from request
            request_data = request.get_json()

            # Validate input
            if not request_data:
                return make_response(jsonify({"error": "Invalid input data"}), 400)

            wildcards = {
                "rb": "/redfish/v1/",
                "id": ident
            }
            bios_data = get_Bios_instance(wildcards)

            # Apply updates from request
            if "Attributes" in request_data:
                bios_data["Attributes"].update(request_data["Attributes"])

            logging.info(f"Updated BIOS data: {bios_data}")
            return make_response(jsonify({"message": "BIOS updated", "bios": bios_data}), 200)

        except Exception as e:
            logging.error(f"Error updating BIOS settings: {str(e)}")
            return make_response(jsonify({"error": "Internal Server Error"}), 500)


class BiosCollectionAPI(Resource):
    def __init__(self):
        logging.info('BiosCollectionAPI init called')
        self.config = {
            '@odata.context': '/redfish/v1/$metadata#BiosCollection.BiosCollection',
            '@odata.id': '/redfish/v1/Bios',
            '@odata.type': '#BiosCollection.1.0.0.BiosCollection',
            'Name': 'BIOS Collection',
            'Members@odata.count': len(members),
            'Members': [{'@odata.id': x['@odata.id']} for x in list(members.values())]
        }

    # HTTP GET
    def get(self):
        logging.info('BiosCollectionAPI GET called')
        try:
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp